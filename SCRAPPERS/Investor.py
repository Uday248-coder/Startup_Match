import requests
from bs4 import BeautifulSoup
import csv
import uuid
import time
import random
from datetime import datetime

BASE_URL = "https://example.com/investors?page={}"
OUTPUT_FILE = "investors.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def clean_number(text):
    if not text:
        return None
    return int("".join(filter(str.isdigit, text)))

def parse_investor(card):
    name = card.select_one(".investor-name")
    company = card.select_one(".company")
    sectors = card.select(".sector")
    stage = card.select_one(".stage")
    location = card.select_one(".location")
    check_range = card.select_one(".check-size")

    min_check, max_check = None, None
    if check_range:
        nums = [int(x) for x in check_range.text.replace(",", "").split("-") if x.strip().isdigit()]
        if len(nums) == 2:
            min_check, max_check = nums

    return {
        "id": str(uuid.uuid4()),
        "email": None,
        "name": name.text.strip() if name else "",
        "company": company.text.strip() if company else "",
        "sectors": "|".join([s.text.strip() for s in sectors]),
        "stage_preference": stage.text.strip() if stage else "",
        "min_check": min_check,
        "max_check": max_check,
        "locations": location.text.strip() if location else "",
        "created_at": datetime.utcnow().isoformat()
    }

def scrape(max_pages=2000):  # adjust to reach 30–50k rows
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id","email","name","company","sectors","stage_preference",
            "min_check","max_check","locations","created_at"
        ])
        writer.writeheader()

        total = 0

        for page in range(1, max_pages + 1):
            url = BASE_URL.format(page)
            r = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(r.text, "lxml")

            cards = soup.select(".investor-card")
            if not cards:
                break

            for card in cards:
                data = parse_investor(card)
                writer.writerow(data)
                total += 1

            print(f"Page {page} | Total investors: {total}")
            time.sleep(random.uniform(1, 2))

    print("Finished. Total records:", total)

if __name__ == "__main__":
    scrape()