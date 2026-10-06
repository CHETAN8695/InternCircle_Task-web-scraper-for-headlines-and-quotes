# Web Scraper for Headlines & Quotes

A Python program that scrapes the latest tech headlines from **Hacker News** and inspirational quotes from **quotes.toscrape.com**, then saves the results in both **clean text** and **JSON** formats.

---

## 🚀 Features
- Scrapes **Hacker News headlines** (titles + links).
- Scrapes **quotes** with author names and tags.
- Handles HTTP requests with headers, timeouts, and error management.
- Parses HTML using **BeautifulSoup**.
- Saves results in:
  - Readable text files (`headlines.txt`, `quotes.txt`)
  - Structured JSON files (`headlines.json`, `quotes.json`)

---

## 📂 Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/web-scraper.git
   cd web-scraper
pip install requests beautifulsoup4
