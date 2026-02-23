class StartupProfile(BaseModel):
    id: str
    email: str | None = None
    name: str
    description: str | None = None
    sector: str | None = None
    stage: str | None = None
    funding_needed: int | None = None
    location: str | None = None
    team_size: int | None = None
    revenue: int | None = None
    growth_rate: float | None = None
    created_at: str

def parse_startup(card):
    name = card.select_one(".startup-name")
    description = card.select_one(".description")
    sector = card.select_one(".sector")
    location = card.select_one(".location")

    return StartupProfile(
        id=str(uuid.uuid4()),
        email=None,
        name=name.text.strip() if name else "",
        description=description.text.strip() if description else None,
        sector=sector.text.strip() if sector else None,
        stage=None,
        funding_needed=None,
        location=location.text.strip() if location else None,
        team_size=None,
        revenue=None,
        growth_rate=None,
        created_at=datetime.utcnow().isoformat()
    ).model_dump()
