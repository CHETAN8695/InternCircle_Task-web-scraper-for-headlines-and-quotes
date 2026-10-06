"""
Web Scraper for Headlines & Quotes
----------------------------------
Scrapes the latest tech headlines (Hacker News) and quotes (quotes.toscrape.com)
using requests + BeautifulSoup, then saves the results as clean text and JSON.

Key features:
  1. HTTP requests handling (headers, timeout, error handling)
  2. HTML tag inspection & extraction (BeautifulSoup)
  3. Data formatting into clean text / JSON

Install dependencies:
    pip install requests beautifulsoup4
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"])
    import requests
    from bs4 import BeautifulSoup

HEADLINES_URL = "https://news.ycombinator.com/"
QUOTES_URL = "https://quotes.toscrape.com/page/{}/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; StudentScraper/1.0)"}
TIMEOUT = 10  # seconds


# ---------- 1. HTTP requests handling ----------
def fetch_page(url):
    """Download a page and return its HTML text, or None if the request fails."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()  # raises an error for 4xx / 5xx responses
        return response.text
    except requests.exceptions.Timeout:
        print(f"  [Error] Request timed out: {url}")
    except requests.exceptions.ConnectionError:
        print("  [Error] Connection failed. Check your internet connection.")
    except requests.exceptions.HTTPError as e:
        print(f"  [Error] HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"  [Error] Something went wrong: {e}")
    return None


# ---------- 2. HTML tag inspection & extraction ----------
def parse_headlines(html, limit=15):
    """Extract headline titles and links from a Hacker News page."""
    soup = BeautifulSoup(html, "html.parser")
    headlines = []

    # Each headline is an <a> tag inside <span class="titleline">
    for tag in soup.select("span.titleline > a"):
        title = tag.get_text(strip=True)
        link = urljoin(HEADLINES_URL, tag.get("href", ""))  # fix relative links
        headlines.append({"title": title, "link": link})
        if len(headlines) >= limit:
            break
    return headlines


def parse_quotes(html):
    """Extract quote text, author and tags from a quotes.toscrape.com page."""
    soup = BeautifulSoup(html, "html.parser")
    quotes = []

    for block in soup.find_all("div", class_="quote"):
        text_tag = block.find("span", class_="text")
        author_tag = block.find("small", class_="author")
        if not text_tag or not author_tag:
            continue  # skip incomplete blocks

        quotes.append(
            {
                "quote": text_tag.get_text(strip=True).strip("\u201c\u201d"),
                "author": author_tag.get_text(strip=True),
                "tags": [t.get_text(strip=True) for t in block.find_all("a", class_="tag")],
            }
        )
    return quotes


def scrape_headlines(limit=15):
    html = fetch_page(HEADLINES_URL)
    return parse_headlines(html, limit) if html else []


def scrape_quotes(pages=2):
    all_quotes = []
    for page in range(1, pages + 1):
        html = fetch_page(QUOTES_URL.format(page))
        if not html:
            break
        found = parse_quotes(html)
        if not found:  # no more pages
            break
        all_quotes.extend(found)
        time.sleep(1)  # be polite to the server
    return all_quotes


# ---------- 3. Data formatting into clean text / JSON ----------
def format_headlines_text(headlines):
    lines = []
    for i, h in enumerate(headlines, start=1):
        lines.append(f"{i}. {h['title']}")
        lines.append(f"   Link: {h['link']}")
    return "\n".join(lines)


def format_quotes_text(quotes):
    lines = []
    for i, q in enumerate(quotes, start=1):
        lines.append(f'{i}. "{q["quote"]}"')
        lines.append(f"   - {q['author']}  [Tags: {', '.join(q['tags']) or 'none'}]")
    return "\n".join(lines)


def save_json(data, source, filename):
    payload = {
        "source": source,
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(data),
        "data": data,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4, ensure_ascii=False)


def save_text(text, title, filename):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{title}\nScraped on: {stamp}\n{'=' * 50}\n\n{text}\n")


# ---------- Main program ----------
def run_headlines():
    print("\nScraping latest tech headlines...")
    headlines = scrape_headlines()
    if not headlines:
        print("No headlines found.")
        return
    print(f"\nFound {len(headlines)} headlines:\n")
    print(format_headlines_text(headlines))

    save_json(headlines, HEADLINES_URL, "headlines.json")
    save_text(format_headlines_text(headlines), "Latest Tech Headlines", "headlines.txt")
    print("\nSaved to headlines.json and headlines.txt")


def run_quotes():
    print("\nScraping quotes...")
    quotes = scrape_quotes()
    if not quotes:
        print("No quotes found.")
        return
    print(f"\nFound {len(quotes)} quotes:\n")
    print(format_quotes_text(quotes))

    save_json(quotes, "https://quotes.toscrape.com/", "quotes.json")
    save_text(format_quotes_text(quotes), "Quotes Collection", "quotes.txt")
    print("\nSaved to quotes.json and quotes.txt")


def main():
    while True:
        print("\n===== Web Scraper =====")
        print("1. Scrape tech headlines")
        print("2. Scrape quotes")
        print("3. Scrape both")
        print("4. Exit")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            run_headlines()
        elif choice == "2":
            run_quotes()
        elif choice == "3":
            run_headlines()
            run_quotes()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()