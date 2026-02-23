import requests
from bs4 import BeautifulSoup
import csv
import time
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

# List of pages to scrape (replace with actual URLs)
TARGET_URLS = [
    "https://angel.co/companies?locations=India",
    "https://angel.co/companies?locations=United-States",
    # Add more country/sector filters
]

OUTPUT_FILE = "startup_funding.csv"

def fetch_html(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            return res.text
        else:
            print(f"[WARN] Request failed ({res.status_code}): {url}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception on fetch:{e}")
        return None

def parse_startup_list(html):
    soup = BeautifulSoup(html, "html.parser")
    startups = []
    
    # AngelList list item selector (class names change, adjust accordingly)
    for item in soup.select("div.company"):
        name = item.select_one("a.button[data-action='profile']")
        if not name:
            continue
        startups.append({
            "name": name.text.strip(),
            "profile_url": name.get("href")
        })
    return startups

def parse_startup_profile(url):
    html = fetch_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    
    # Extract funding table, dates, and investors
    funding_info = []
    for row in soup.select("table.funding-rounds tr"):
        cells = row.select("td")
        if len(cells) < 3:
            continue
        date     = cells[0].get_text(strip=True)
        amount   = cells[1].get_text(strip=True)
        investors = cells[2].get_text(strip=True)
        funding_info.append((date, amount, investors))

    return funding_info

def save_csv(data):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["startup", "fund_date", "fund_amount", "investors"])
        for row in data:
            writer.writerow(row)

def main():
    all_data = []

    for base_url in TARGET_URLS:
        html = fetch_html(base_url)
        if not html:
            continue

        startups = parse_startup_list(html)

        for s in startups:
            profile_url = s["profile_url"]
            if not profile_url.startswith("http"):
                profile_url = "https://angel.co" + profile_url

            print(f"[INFO] Scraping: {s['name']} ({profile_url})")
            funding_data = parse_startup_profile(profile_url)
            if not funding_data:
                continue

            for (date, amount, investors) in funding_data:
                all_data.append([
                    s["name"],
                    date,
                    amount,
                    investors
                ])

            # Be polite with delays
            time.sleep(random.uniform(1.0, 3.0))

    save_csv(all_data)
    print(f"[DONE] Saved {len(all_data)} funding rows to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

    