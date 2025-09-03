import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import csv

WORDS_PER_PAGE = 300  # words per page assumption

# Load EPUB
book = epub.read_epub("hpmor.epub")

chapters = []
for item in book.get_items():
    if item.get_type() == ebooklib.ITEM_DOCUMENT:
        chapters.append(item.get_content())

chapter_counts = []
all_texts = []  # store each chapter's text split into lines

for idx, content in enumerate(chapters, start=1):
    soup = BeautifulSoup(content, "html.parser")

    # Grab chapter title
    title_tag = soup.find(["h1", "h2", "h3"])
    title = title_tag.get_text().strip() if title_tag else f"Chapter {idx}"

    # Extract clean text split into lines
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    all_texts.append(lines)

    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)
    approx_pages = round(word_count / WORDS_PER_PAGE, 1)

    chapter_counts.append((idx, title, word_count, approx_pages))
    print(f"{title} (Chapter {idx}): {word_count} words (~{approx_pages} pages)")

# Totals
total_words = sum(ch[2] for ch in chapter_counts)
total_pages = round(total_words / WORDS_PER_PAGE, 1)
print(f"\nTOTAL: {total_words} words (~{total_pages} pages)")

# Save CSV
with open("hpmor_epub_wordcounts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["ChapterNumber", "Title", "WordCount", "ApproxPages"])
    for ch_num, title, wc, pages in chapter_counts:
        writer.writerow([ch_num, title, wc, pages])
    writer.writerow(["TOTAL", "", total_words, total_pages])

# Progress tracker
print("\n--- Progress Tracker ---")
try:
    chapter_num = int(input("Enter the chapter number you are on: "))
    snippet = input("Enter a short snippet of text from the line you are on: ").strip().lower()

    current_lines = all_texts[chapter_num-1]

    # Find the line index that contains the snippet
    line_index = None
    for i, line in enumerate(current_lines):
        if snippet in line.lower():
            line_index = i
            break

    if line_index is None:
        raise ValueError("Snippet not found in chapter text.")

    # Words before this chapter
    words_before = sum(ch[2] for ch in chapter_counts[:chapter_num-1])

    # Words up to the snippet line
    current_text_up_to_line = " ".join(current_lines[:line_index+1])
    words_in_current = len(re.findall(r"\b\w+\b", current_text_up_to_line))

    words_completed = words_before + words_in_current
    pages_completed = round(words_completed / WORDS_PER_PAGE, 1)
    percent_completed = round((words_completed / total_words) * 100, 2)
    pages_completed_scaled = percent_completed*2732/100.

    print(f"\nMatched line {line_index+1} in Chapter {chapter_num}.")
    print(f"You have completed ~{pages_completed}/{total_pages} pages "
          f"({percent_completed}%). Scaled pages: {pages_completed_scaled}")

except Exception as e:
    print(f"Skipping progress tracker: {e}")
