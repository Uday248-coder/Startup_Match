from datetime import datetime

def compute_match(investor, startup):
    sector_match = 1.0 if startup["sector"] in investor["sectors"] else 0.0
    stage_match = 1.0 if investor["stage_preference"] == startup["stage"] else 0.0
    location_match = 1.0 if startup["location"] in investor["locations"] else 0.0

    funding_match = 0.0
    if investor["min_check"] and investor["max_check"]:
        if investor["min_check"] <= startup["funding_needed"] <= investor["max_check"]:
            funding_match = 1.0

    score = (sector_match * 0.4 +
             stage_match * 0.2 +
             location_match * 0.2 +
             funding_match * 0.2)

    return {
        "investor_id": investor["id"],
        "startup_id": startup["id"],
        "score": score,
        "sector_match": sector_match,
        "stage_match": stage_match,
        "location_match": location_match,
        "funding_match": funding_match,
        "computed_at": datetime.utcnow().isoformat()
    }
