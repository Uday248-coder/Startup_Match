import requests
from bs4 import BeautifulSoup
import csv
import uuid
import time
import random
from datetime import datetime

BASE_URL = "https://example.com/startups?page={}"
OUTPUT_FILE = "startups.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def clean_number(text):
    if not text:
        return None
    return int("".join(filter(str.isdigit, text)))

def parse_startup(card):
    name = card.select_one(".startup-name")
    description = card.select_one(".description")
    sector = card.select_one(".sector")
    stage = card.select_one(".stage")
    funding = card.select_one(".funding")
    location = card.select_one(".location")
    team = card.select_one(".team-size")
    revenue = card.select_one(".revenue")
    growth = card.select_one(".growth")

    return {
        "id": str(uuid.uuid4()),
        "email": None,
        "name": name.text.strip() if name else "",
        "description": description.text.strip() if description else "",
        "sector": sector.text.strip() if sector else "",
        "stage": stage.text.strip() if stage else "",
        "funding_needed": clean_number(funding.text) if funding else None,
        "location": location.text.strip() if location else "",
        "team_size": clean_number(team.text) if team else None,
        "revenue": clean_number(revenue.text) if revenue else None,
        "growth_rate": clean_number(growth.text) if growth else None,
        "created_at": datetime.utcnow().isoformat()
    }

def scrape(max_pages=3000):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id","email","name","description","sector","stage",
            "funding_needed","location","team_size",
            "revenue","growth_rate","created_at"
        ])
        writer.writeheader()

        total = 0

        for page in range(1, max_pages + 1):
            url = BASE_URL.format(page)
            r = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(r.text, "lxml")

            cards = soup.select(".startup-card")
            if not cards:
                break

            for card in cards:
                writer.writerow(parse_startup(card))
                total += 1

            print(f"Page {page} | Total startups: {total}")
            time.sleep(random.uniform(1, 2))

    print("Finished. Total records:", total)

if __name__ == "__main__":
    scrape()