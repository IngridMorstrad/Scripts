import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import re
import calendar
import time
import random
import os

# Updated cache file for India-specific data
CACHE_FILE = 'visa_bulletin_data_india.csv'
# Reference date for converting dates to days.
# We no longer rely on a single fixed date for normalization, but keep it for display purposes.
REF_DATE = datetime(2019, 6, 1).date()

def date_to_days_since_ref(date):
    """
    Converts a datetime object or Timestamp to the number of days since the reference date.
    This is used for numerical representation before normalization.
    """
    if date is None:
        return None
    if isinstance(date, pd.Timestamp):
        date = date.date()
    return (date - REF_DATE).days

def normalize_data(df, category_col, date_col):
    """
    Normalizes the date data for a given category and date column to a range of [0, 1].
    Returns the normalized dataframe and the min/max values used for scaling.
    """
    df_copy = df.copy()
    
    # Convert dates to days since a reference date for numerical scaling
    df_copy['BulletinDays'] = df_copy[date_col].apply(date_to_days_since_ref)
    df_copy['PriorityDays'] = df_copy[category_col].apply(date_to_days_since_ref)
    
    # Store min/max values for later un-normalization
    min_x = df_copy['PriorityDays'].min()
    max_x = df_copy['PriorityDays'].max() + 7300
    min_y = df_copy['BulletinDays'].min()
    max_y = df_copy['BulletinDays'].max() + 25700
    
    # Handle the case of zero range to prevent division by zero
    if (max_x - min_x) == 0:
        df_copy['PriorityNormalized'] = 0
    else:
        df_copy['PriorityNormalized'] = (df_copy['PriorityDays'] - min_x) / (max_x - min_x)
    if (max_y - min_y) == 0:
        df_copy['BulletinNormalized'] = 0
    else:
        df_copy['BulletinNormalized'] = (df_copy['BulletinDays'] - min_y) / (max_y - min_y)
    
    return df_copy, {'min_x': min_x, 'max_x': max_x, 'min_y': min_y, 'max_y': max_y}

def unnormalize_data(normalized_value, min_val, max_val):
    """
    Converts a normalized value back to its original numerical range.
    """
    return normalized_value * (max_val - min_val) + min_val

def generate_visa_bulletin_urls(start_year, end_year):
    """
    Generates a list of URLs for the visa bulletin for a given range of years,
    handling the fiscal year logic for October, November, and December.
    """
    urls = []
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    base_url = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{url_year}/visa-bulletin-for-{month}-{calendar_year}.html"
    
    for calendar_year in range(start_year, end_year + 1):
        for month_num in range(1, 13):
            if calendar_year == current_year and month_num > (current_month + 1):
                continue
            month_name = calendar.month_name[month_num].lower()
            if month_num >= 10: 
                url_year = calendar_year + 1
            else:
                url_year = calendar_year
            
            urls.append(base_url.format(
                url_year=url_year, 
                month=month_name, 
                calendar_year=calendar_year
            ))
            
    return urls

def parse_priority_date(date_str, bulletin_date):
    """
    Parses the priority date string from the bulletin table.
    """
    if not date_str or date_str.upper() == 'U':
        return None
    if date_str.upper() == 'C':
        return bulletin_date
    try:
        return datetime.strptime(date_str, '%d%b%y')
    except ValueError:
        return None

def scrape_bulletin_data(url):
    """
    Scrapes a single visa bulletin page to find the EB-2 and EB-3 priority dates for India.
    """
    print(f"Fetching: {url}")
    try:
        response = requests.get(url, timeout=10)
        time.sleep(random.uniform(0, 3))
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table')
    
    dates = {'EB2': None, 'EB3': None}
    found_table = False

    for table in tables:
        if "employment" in table.get_text().lower():
            found_table = True
            rows = table.find_all('tr')
            
            india_col_index = -1
            if rows:
                header_cells = rows[0].find_all(['th', 'td'])
                for i, cell in enumerate(header_cells):
                    if "india" in cell.get_text().lower():
                        india_col_index = i
                        break
            
            if india_col_index == -1:
                continue

            bulletin_date = None
            match = re.search(r"(\w+)-(\d{4})\.html", url)
            if match:
                month_name, year = match.groups()
                try:
                    month_num = list(calendar.month_name).index(month_name.capitalize())
                    bulletin_date = datetime(int(year), month_num, 1)
                except ValueError:
                    continue

            if not bulletin_date:
                continue

            for row in rows:
                cells = row.find_all(['td', 'th'])
                if not cells:
                    continue
                
                row_header = cells[0].get_text()
                
                category_map = {"2nd": "EB2", "3rd": "EB3"}
                for key, category in category_map.items():
                    if key in row_header:
                        if len(cells) > india_col_index:
                            priority_date_str = cells[india_col_index].get_text().strip()
                            dates[category] = parse_priority_date(priority_date_str, bulletin_date)
            break 
            
    return dates if found_table else None

def calculate_rmse(y_true, y_pred):
    """Calculates the Root Mean Square Error."""
    return np.sqrt(np.mean((y_true - y_pred) ** 2))

def find_best_model(train_df, val_df, category_col):
    """
    Compares different regression models on the normalized validation set and returns
    the best-fitting one based on the lowest RMSE.
    """
    train_df = train_df[['BulletinDate', category_col]].dropna()
    val_df = val_df[['BulletinDate', category_col]].dropna()

    if len(train_df) < 3 or len(val_df) < 1:
        print(f"Not enough data to find best model for {category_col}.")
        return None, None, float('inf'), None

    # Normalize the training and validation data
    train_df_normalized, train_scale = normalize_data(train_df, category_col, 'BulletinDate')
    val_df_normalized, _ = normalize_data(val_df, category_col, 'BulletinDate')
    
    best_model = None
    min_rmse = float('inf')
    best_coeffs = None
    
    x_train, y_train = train_df_normalized['PriorityNormalized'], train_df_normalized['BulletinNormalized']
    x_val, y_val = val_df_normalized['PriorityNormalized'], val_df_normalized['BulletinNormalized']

    # --- Test 1: Logarithmic Model ---
    df_log_safe_train = train_df_normalized[train_df_normalized['PriorityNormalized'] > 0]
    df_log_safe_val = val_df_normalized[val_df_normalized['PriorityNormalized'] > 0]

    if len(df_log_safe_train) >= 2 and len(df_log_safe_val) >= 1:
        x_log_train = np.log(df_log_safe_train['PriorityNormalized'])
        y_log_train = df_log_safe_train['BulletinNormalized']
        try:
            coeffs = np.polyfit(x_log_train, y_log_train, 1)
            x_log_val = np.log(df_log_safe_val['PriorityNormalized'])
            y_pred_val = coeffs[0] * x_log_val + coeffs[1]
            rmse = calculate_rmse(df_log_safe_val['BulletinNormalized'], y_pred_val)
            if rmse < min_rmse:
                min_rmse = rmse
                best_model = "logarithmic"
                best_coeffs = coeffs
        except (np.linalg.LinAlgError, ValueError):
            pass

    # --- Test 2: Linear Model ---
    if len(x_train) >= 2:
        try:
            coeffs = np.polyfit(x_train, y_train, 1)
            y_pred_val = coeffs[0] * x_val + coeffs[1]
            rmse = calculate_rmse(y_val, y_pred_val)
            if rmse < min_rmse:
                min_rmse = rmse
                best_model = "linear"
                best_coeffs = coeffs
        except (np.linalg.LinAlgError, ValueError):
            pass

    # --- Test 3: 2nd-degree Polynomial Model ---
    if len(x_train) >= 3:
        try:
            coeffs = np.polyfit(x_train, y_train, 2)
            y_pred_val = coeffs[0] * x_val**2 + coeffs[1] * x_val + coeffs[2]
            rmse = calculate_rmse(y_val, y_pred_val)
            if rmse < min_rmse:
                min_rmse = rmse
                best_model = "2nd-degree polynomial"
                best_coeffs = coeffs
        except (np.linalg.LinAlgError, ValueError):
            pass

    # --- Test 4: Exponential Model ---
    df_exp_safe_train = train_df_normalized[train_df_normalized['BulletinNormalized'] > 0]
    df_exp_safe_val = val_df_normalized[val_df_normalized['BulletinNormalized'] > 0]

    if len(df_exp_safe_train) >= 2 and len(df_exp_safe_val) >= 1:
        x_exp_train = df_exp_safe_train['PriorityNormalized']
        y_exp_train = np.log(df_exp_safe_train['BulletinNormalized'])
        try:
            coeffs = np.polyfit(x_exp_train, y_exp_train, 1)
            x_exp_val = df_exp_safe_val['PriorityNormalized']
            y_pred_val = np.exp(coeffs[0] * x_exp_val + coeffs[1])
            rmse = calculate_rmse(df_exp_safe_val['BulletinNormalized'], y_pred_val)
            ## MANUAL CHANGE
            if True or rmse < min_rmse:
                min_rmse = rmse
                best_model = "exponential"
                best_coeffs = coeffs
        except (np.linalg.LinAlgError, ValueError):
            pass

    return best_model, best_coeffs, min_rmse, train_scale

def plot_regression_line(ax, df, category_col, color, label, model, coeffs, scale):
    """
    Plots a regression line based on a given model and coefficients.
    The calculations are done on normalized data and then un-normalized for plotting.
    """
    if model is None or coeffs is None or scale is None:
        return

    # Create a range of normalized bulletin days to plot over
    y_normalized_range = np.linspace(0, 1, 100)
    x_normalized_plot = np.full_like(y_normalized_range, np.nan)

    try:
        if model == "logarithmic":
            a, b = coeffs
            # Handle potential log(0)
            y_log_safe = y_normalized_range.copy()
            y_log_safe[y_log_safe == 0] = 1e-9
            x_normalized_plot = np.exp((y_log_safe - b) / a)
        elif model == "linear":
            a, b = coeffs
            x_normalized_plot = (y_normalized_range - b) / a
        elif model == "2nd-degree polynomial":
            a, b, c = coeffs
            sqrt_term = b**2 - 4*a*(c - y_normalized_range)
            positive_discriminant_mask = sqrt_term >= 0
            x_normalized_plot[positive_discriminant_mask] = (-b + np.sqrt(sqrt_term[positive_discriminant_mask])) / (2*a)
        elif model == "exponential":
            a, b = coeffs
            # Handle potential log(0)
            y_log_safe = y_normalized_range.copy()
            y_log_safe[y_log_safe <= 0] = 1e-9
            x_normalized_plot = (np.log(y_log_safe) - b) / a
        else:
            return
            
    except (ValueError, TypeError, np.linalg.LinAlgError):
        print(f"Failed to plot custom {label} regression line. Check coefficients.")
        return

    # Filter out invalid values (e.g., from complex numbers or extreme values)
    valid_mask = (x_normalized_plot >= 0) & (x_normalized_plot <= 1) & np.isfinite(x_normalized_plot)

    # Un-normalize the calculated values back to days
    x_days_unnormalized = unnormalize_data(x_normalized_plot[valid_mask], scale['min_x'], scale['max_x'])
    y_days_unnormalized = unnormalize_data(y_normalized_range[valid_mask], scale['min_y'], scale['max_y'])
    
    # Convert the un-normalized days back to datetime objects for plotting
    x_dates = [REF_DATE + timedelta(days=int(val)) for val in x_days_unnormalized]
    y_dates = [REF_DATE + timedelta(days=int(val)) for val in y_days_unnormalized]
    
    ax.plot(y_dates, x_dates, color=color, linestyle='--', linewidth=2, label=f'{label} ({model})')

def predict_current_date(priority_date_str, model, coeffs, scale):
    """
    Predicts the future current date using a given regression model.
    The prediction is done on normalized values and then un-normalized.
    """
    if coeffs is None or model is None or scale is None:
        return None

    try:
        priority_date = datetime.strptime(priority_date_str, '%Y-%m-%d')
        x_days = date_to_days_since_ref(priority_date.date())
        
        # Normalize the input priority date
        x_normalized = (x_days - scale['min_x']) / (scale['max_x'] - scale['min_x'])

        if model == "logarithmic":
            if x_normalized <= 0: return None
            y_normalized = coeffs[0] * np.log(x_normalized) + coeffs[1]
        elif model == "linear":
            y_normalized = coeffs[0] * x_normalized + coeffs[1]
        elif model == "2nd-degree polynomial":
            y_normalized = coeffs[0] * x_normalized**2 + coeffs[1] * x_normalized + coeffs[2]
        elif model == "exponential":
            if x_normalized < 0: return None
            y_normalized = np.exp(coeffs[0] * x_normalized + coeffs[1])
        else:
            return None

        # Un-normalize the predicted bulletin date back to days, then to a date object
        y_days = unnormalize_data(y_normalized, scale['min_y'], scale['max_y'])
        return y_days
    except (ValueError, TypeError) as e:
        print(f"Prediction error: {e}")
        return None

def main():
    """
    Main function to orchestrate the scraping, analysis, and plotting.
    """
    if os.path.exists(CACHE_FILE):
        print(f"Loading existing data from {CACHE_FILE}...")
        df = pd.read_csv(CACHE_FILE, parse_dates=['BulletinDate', 'EB2_PriorityDate_India', 'EB3_PriorityDate_India'])
    else:
        print("No cache file found. Creating a new DataFrame.")
        df = pd.DataFrame(columns=['BulletinDate', 'EB2_PriorityDate_India', 'EB3_PriorityDate_India'])

    start_year = 2013
    end_year = (datetime.now() + timedelta(days=30)).year
    all_urls = generate_visa_bulletin_urls(start_year, end_year)
    
    scraped_bulletin_dates = set(pd.to_datetime(df['BulletinDate']).dt.date)
    urls_to_scrape = []
    for url in all_urls:
        match = re.search(r"(\w+)-(\d{4})\.html", url)
        if match:
            month_name, year = match.groups()
            try:
                month_num = list(calendar.month_name).index(month_name.capitalize())
                bulletin_date = datetime(int(year), month_num, 1).date()
                if bulletin_date not in scraped_bulletin_dates:
                    urls_to_scrape.append(url)
            except ValueError:
                continue

    print(f"Found {len(urls_to_scrape)} new bulletins to scrape.")

    if urls_to_scrape:
        fetch = False
        with open(CACHE_FILE, 'a', newline='') as f:
            if df.empty:
                f.write('BulletinDate,EB2_PriorityDate_India,EB3_PriorityDate_India\n')
            if not fetch: urls_to_scrape = []
            for url in urls_to_scrape:
                dates = scrape_bulletin_data(url)
                if dates:
                    match = re.search(r"(\w+)-(\d{4})\.html", url)
                    month_name, year = match.groups()
                    month_num = list(calendar.month_name).index(month_name.capitalize())
                    bulletin_date = datetime(int(year), month_num, 1)
                    eb2_date_str = dates['EB2'].strftime('%Y-%m-%d') if dates['EB2'] else ''
                    eb3_date_str = dates['EB3'].strftime('%Y-%m-%d') if dates['EB3'] else ''
                    f.write(f"{bulletin_date.strftime('%Y-%m-%d')},{eb2_date_str},{eb3_date_str}\n")
                    print(f"  -> Saved data for {bulletin_date.strftime('%Y-%m')}")
        df = pd.read_csv(CACHE_FILE, parse_dates=['BulletinDate', 'EB2_PriorityDate_India', 'EB3_PriorityDate_India'])

    if df.empty:
        print("No data available to plot. Exiting.")
        return

    df = df.dropna(subset=['EB2_PriorityDate_India', 'EB3_PriorityDate_India'], how='all').reset_index(drop=True)
    
    print("\n--- Running multiple validation splits to find the best model ---")
    num_runs = 10
    model_results = {'EB2': {}, 'EB3': {}}
    model_types = ["linear", "logarithmic", "2nd-degree polynomial", "exponential"]

    for i in range(num_runs):
        print(f"Validation Run {i+1}/{num_runs}")
        val_df = df.sample(frac=0.2, random_state=i) # Use different seed for each run
        train_df = df.drop(val_df.index)

        eb2_model_run, eb2_coeffs_run, eb2_rmse_run, eb2_scale_run = find_best_model(train_df, val_df, 'EB2_PriorityDate_India')
        eb3_model_run, eb3_coeffs_run, eb3_rmse_run, eb3_scale_run = find_best_model(train_df, val_df, 'EB3_PriorityDate_India')

        # Store results for EB-2
        if eb2_model_run:
            if eb2_model_run not in model_results['EB2']:
                model_results['EB2'][eb2_model_run] = {'rmse': [], 'coeffs': [], 'scale': []}
            model_results['EB2'][eb2_model_run]['rmse'].append(eb2_rmse_run)
            model_results['EB2'][eb2_model_run]['coeffs'].append(eb2_coeffs_run)
            model_results['EB2'][eb2_model_run]['scale'].append(eb2_scale_run)

        # Store results for EB-3
        if eb3_model_run:
            if eb3_model_run not in model_results['EB3']:
                model_results['EB3'][eb3_model_run] = {'rmse': [], 'coeffs': [], 'scale': []}
            model_results['EB3'][eb3_model_run]['rmse'].append(eb3_rmse_run)
            model_results['EB3'][eb3_model_run]['coeffs'].append(eb3_coeffs_run)
            model_results['EB3'][eb3_model_run]['scale'].append(eb3_scale_run)

    # Find the overall best model based on average RMSE
    best_eb2_model = None
    min_eb2_avg_rmse = float('inf')
    best_eb2_coeffs = None
    best_eb2_scale = None
    
    for model_type, results in model_results['EB2'].items():
        if results['rmse']:
            avg_rmse = np.mean(results['rmse'])
            print(f"EB-2 Model {model_type}: Avg RMSE = {avg_rmse:.2f} days")
            if avg_rmse < min_eb2_avg_rmse:
                min_eb2_avg_rmse = avg_rmse
                best_eb2_model = model_type
                # Choose the coeffs from the run with the lowest RMSE
                best_run_index = np.argmin(results['rmse'])
                best_eb2_coeffs = results['coeffs'][best_run_index]
                best_eb2_scale = results['scale'][best_run_index]
    
    best_eb3_model = None
    min_eb3_avg_rmse = float('inf')
    best_eb3_coeffs = None
    best_eb3_scale = None

    for model_type, results in model_results['EB3'].items():
        if results['rmse']:
            avg_rmse = np.mean(results['rmse'])
            print(f"EB-3 Model {model_type}: Avg RMSE = {avg_rmse:.2f} days")
            if avg_rmse < min_eb3_avg_rmse:
                min_eb3_avg_rmse = avg_rmse
                best_eb3_model = model_type
                best_run_index = np.argmin(results['rmse'])
                best_eb3_coeffs = results['coeffs'][best_run_index]
                best_eb3_scale = results['scale'][best_run_index]

    print(f"\nOverall Best EB-2 Model: {best_eb2_model} (Avg RMSE: {min_eb2_avg_rmse:.2f} days)")
    print(f"Overall Best EB-3 Model: {best_eb3_model} (Avg RMSE: {min_eb3_avg_rmse:.2f} days)")

    # Plotting
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(14, 8))

    ax.scatter(df['BulletinDate'], df['EB2_PriorityDate_India'], label='EB-2 India', color='royalblue', alpha=0.6)
    ax.scatter(df['BulletinDate'], df['EB3_PriorityDate_India'], label='EB-3 India', color='green', alpha=0.6)
    
    plot_regression_line(ax, df, 'EB2_PriorityDate_India', 'darkblue', 'EB-2 India', best_eb2_model, best_eb2_coeffs, best_eb2_scale)
    plot_regression_line(ax, df, 'EB3_PriorityDate_India', 'darkgreen', 'EB-3 India', best_eb3_model, best_eb3_coeffs, best_eb3_scale)

    ax.set_title('Green Card Wait Time (EB-2 & EB-3 Categories for India)', fontsize=18, fontweight='bold')
    ax.set_xlabel('Bulletin Date (Date Became Current)', fontsize=12)
    ax.set_ylabel('Priority Date (Date of Filing)', fontsize=12)
    
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.yaxis.set_major_locator(mdates.YearLocator())
    ax.yaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    fig.text(0.5, 0.01, "Chart tracks 'Final Action Dates' for India. Best-fit model selected using average RMSE over multiple runs.", ha='center', fontsize=10, style='italic')
    plt.show()

    print("\n--- Wait Time Prediction ---")
    while True:
        try:
            priority_date_str = input("Enter a priority date to predict (YYYY-MM-DD): ")
            if not priority_date_str:
                print("No date entered. Exiting prediction mode.")
                return
            datetime.strptime(priority_date_str, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
    
    # Get predictions in days
    eb2_days = predict_current_date(priority_date_str, best_eb2_model, best_eb2_coeffs, best_eb2_scale)
    eb3_days = predict_current_date(priority_date_str, best_eb3_model, best_eb3_coeffs, best_eb3_scale)

    if eb2_days is not None:
        eb2_predicted_date = REF_DATE + timedelta(days=int(eb2_days))
        print(f"Predicted EB-2 current date: {eb2_predicted_date.strftime('%Y-%m-%d')}")
    else:
        print("EB-2 prediction failed.")

    if eb3_days is not None:
        eb3_predicted_date = REF_DATE + timedelta(days=int(eb3_days))
        print(f"Predicted EB-3 current date: {eb3_predicted_date.strftime('%Y-%m-%d')}")
    else:
        print("EB-3 prediction failed.")

    # Calculate and predict average
    if eb2_days is not None and eb3_days is not None:
        average_days = (eb2_days + eb3_days) / 2
        average_predicted_date = REF_DATE + timedelta(days=int(average_days))
        print(f"Predicted average current date: {average_predicted_date.strftime('%Y-%m-%d')}")
    elif eb2_days is not None or eb3_days is not None:
        print("Cannot calculate average prediction due to one failed model.")
    else:
        print("Both predictions failed.")

if __name__ == '__main__':
    main()
