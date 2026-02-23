import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pydantic import BaseModel
from datetime import datetime
import uuid
import json

class InvestorProfile(BaseModel):
    id: str
    email: str | None = None
    name: str
    company: str | None = None
    sectors: list[str]
    stage_preference: str | None = None
    min_check: int | None = None
    max_check: int | None = None
    locations: list[str]
    created_at: str

HEADERS = {
    "User-Agent": UserAgent().random
}

BASE_URL = "https://example.com/investors?page={}"

def parse_investor(card):
    name = card.select_one(".investor-name")
    company = card.select_one(".company")
    sectors = card.select(".sector-tag")
    location = card.select_one(".location")

    return InvestorProfile(
        id=str(uuid.uuid4()),
        email=None,
        name=name.text.strip() if name else "",
        company=company.text.strip() if company else None,
        sectors=[s.text.strip() for s in sectors],
        stage_preference=None,
        min_check=None,
        max_check=None,
        locations=[location.text.strip()] if location else [],
        created_at=datetime.utcnow().isoformat()
    ).model_dump()

def scrape_investors(pages=5):
    results = []
    for page in range(1, pages + 1):
        url = BASE_URL.format(page)
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "lxml")
        investor_cards = soup.select(".investor-card")
        for card in investor_cards:
            results.append(parse_investor(card))
    return results

if __name__ == "__main__":
    data = scrape_investors(pages=3)
    with open("investors.json", "w") as f:
        json.dump(data, f, indent=2)
