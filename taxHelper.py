## TODO: Handle wash sales
## Disclaimer: May break at any time, not guaranteed to work.

## Instructions:
## Use "a tax software" to get transactions,
## then replace column 3 (which says "Short term sales (covered)" or similar, with the date the security was acquired)
## Replace filename with the file containing these transactions
## Run python3 taxHelper.py
## Paste output into the JS console for "another tax software"

FILENAME="abc"

parsed = []
with open(FILENAME, "r") as f:
    parsed = [line.split("\t") for line in f]

old_dat = ""
for line in parsed:
    print(f"""
    document.getElementById('temp_inv_desc').value = "{line[0]}";
    document.getElementById('sold_date').value = "{line[1][:-5]}";
    document.getElementById('sale_price').value = "{line[3][1:]}";
    document.getElementById('temp_basis').value = "{line[4][1:]}";
    document.getElementById('acq_date').value = "{line[2]}";
    document.getElementById('basis_shown-C').checked = true;
    $('#taxForm > div:nth-child(14) > div > div.button-right.mt-4.mt-sm-0 > a').click();
    """)
    print("await new Promise(r => setTimeout(r, 3000));")
    print("""$('#taxForm > div > div.button-section.box > div.button-right.mt-4.mt-sm-0 > a').click(); await new Promise(r => setTimeout(r, 3000));$('#taxForm > div > div.button-section.box > div.button-right.mt-4.mt-sm-0 > a:nth-child(1)').click(); await new Promise(r => setTimeout(r, 3000));document.getElementById('sale_type-I').checked = true; $('#taxForm > div:nth-child(15) > div > div.button-right.mt-4.mt-sm-0 > a').click(); await new Promise(r => setTimeout(r, 3000));""")
