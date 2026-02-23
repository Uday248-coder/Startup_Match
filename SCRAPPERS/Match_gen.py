import csv
import uuid
from datetime import datetime

INVESTOR_FILE = "investors.csv"
STARTUP_FILE = "startups.csv"
OUTPUT_FILE = "matches.csv"

def compute_match(inv, st):
    sector_match = 1.0 if st["sector"] in inv["sectors"].split("|") else 0.0
    stage_match = 1.0 if inv["stage_preference"] == st["stage"] else 0.0
    location_match = 1.0 if st["location"] in inv["locations"] else 0.0

    funding_match = 0.0
    if inv["min_check"] and inv["max_check"] and st["funding_needed"]:
        if int(inv["min_check"]) <= int(st["funding_needed"]) <= int(inv["max_check"]):
            funding_match = 1.0

    score = (
        sector_match * 0.4 +
        stage_match * 0.2 +
        location_match * 0.2 +
        funding_match * 0.2
    )

    return {
        "investor_id": inv["id"],
        "startup_id": st["id"],
        "score": score,
        "sector_match": sector_match,
        "stage_match": stage_match,
        "location_match": location_match,
        "funding_match": funding_match,
        "computed_at": datetime.utcnow().isoformat()
    }

def generate_matches(limit=50000):
    with open(INVESTOR_FILE) as f1, open(STARTUP_FILE) as f2:
        investors = list(csv.DictReader(f1))
        startups = list(csv.DictReader(f2))

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=[
            "investor_id","startup_id","score",
            "sector_match","stage_match","location_match",
            "funding_match","computed_at"
        ])
        writer.writeheader()

        count = 0

        for inv in investors:
            for st in startups:
                writer.writerow(compute_match(inv, st))
                count += 1
                if count >= limit:
                    print("Generated:", count)
                    return

    print("Generated:", count)

if __name__ == "__main__":
    generate_matches()