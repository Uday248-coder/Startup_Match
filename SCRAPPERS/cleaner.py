def normalize_sector(sector):
    sector_map = {
        "AI": "Technology",
        "FinTech": "Finance",
        "MedTech": "Healthcare"
    }
    return sector_map.get(sector, sector)

def clean_numeric(value):
    if not value:
        return None
    return int("".join(filter(str.isdigit, value)))
