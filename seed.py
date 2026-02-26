"""
StartMatch — Demo Seed Script
Wipes db.sqlite and inserts 20 pre-registered demo entities.
Run ONCE before launching app.py:
    python seed.py
"""

import sqlite3, hashlib, os, uuid

DB = "data/db.sqlite"
DEFAULT_PW = hashlib.sha256("Demo@1234".encode()).hexdigest()

os.makedirs("data", exist_ok=True)

# ── 1. DROP & RECREATE ─────────────────────────────────────────────────────────
con = sqlite3.connect(DB)
con.executescript("""
    DROP TABLE IF EXISTS startups;
    DROP TABLE IF EXISTS investors;
    DROP TABLE IF EXISTS users;

    CREATE TABLE startups (
        id TEXT PRIMARY KEY, name TEXT, founder TEXT, sector TEXT,
        stage TEXT, location TEXT, description TEXT,
        revenue REAL DEFAULT 0, website TEXT,
        team_size INTEGER DEFAULT 0,
        linkedin TEXT,
        target_market TEXT,
        business_model TEXT,
        country TEXT,
        mrr REAL DEFAULT 0,
        growth_rate REAL DEFAULT 0,
        runway INTEGER DEFAULT 0,
        burn_rate REAL DEFAULT 0
    );

    CREATE TABLE investors (
        id TEXT PRIMARY KEY, name TEXT, firm TEXT, sector TEXT,
        stage TEXT, location TEXT, thesis TEXT,
        ticket_size REAL DEFAULT 0, website TEXT,
        fund_size REAL DEFAULT 0,
        portfolio_count INTEGER DEFAULT 0,
        notable_investments TEXT,
        geo_focus TEXT,
        co_invest_pref TEXT,
        decision_timeline TEXT,
        business_model_pref TEXT,
        linkedin TEXT,
        investments_per_year INTEGER DEFAULT 0
    );

    CREATE TABLE users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        entity_id TEXT NOT NULL
    );
""")
con.commit()

# ── 2. HELPERS ─────────────────────────────────────────────────────────────────
def sid(): return str(uuid.uuid4())

def add_startup(username, d):
    eid = sid()
    con.execute("""
        INSERT INTO startups VALUES
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (eid, d['name'], d['founder'], d['sector'], d['stage'],
          d['location'], d['description'], d['revenue'], d['website'],
          d['team_size'], d['linkedin'], d['target_market'],
          d['business_model'], d['country'], d['mrr'],
          d['growth_rate'], d['runway'], d['burn_rate']))
    con.execute("INSERT INTO users VALUES (?,?,?,?)",
                (username, DEFAULT_PW, "Startup", eid))

def add_investor(username, d):
    eid = sid()
    con.execute("""
        INSERT INTO investors VALUES
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (eid, d['name'], d['firm'], d['sector'], d['stage'],
          d['location'], d['thesis'], d['ticket_size'], d['website'],
          d['fund_size'], d['portfolio_count'], d['notable_investments'],
          d['geo_focus'], d['co_invest_pref'], d['decision_timeline'],
          d['business_model_pref'], d['linkedin'], d['investments_per_year']))
    con.execute("INSERT INTO users VALUES (?,?,?,?)",
                (username, DEFAULT_PW, "Investor", eid))

# ── 3. STARTUPS (11) ───────────────────────────────────────────────────────────
add_startup("neuralcart", dict(
    name="NeuralCart", founder="Priya Sharma", sector="AI/ML",
    stage="Series A", location="San Francisco, USA",
    description="NeuralCart is an AI-native personalization engine for e-commerce. "
                "Our deep learning models analyze real-time behavioral signals to predict "
                "purchase intent and serve hyper-relevant product recommendations, "
                "increasing conversion rates by an average of 34% for our clients. "
                "We integrate via a single API line and are live on 40+ Shopify and "
                "Magento stores across North America.",
    revenue=1_400_000, website="https://neuralcart.io",
    team_size=18, linkedin="https://linkedin.com/company/neuralcart",
    target_market="Mid-market e-commerce brands ($5M–$100M GMV)",
    business_model="SaaS", country="United States",
    mrr=116_000, growth_rate=12.4, runway=22, burn_rate=95_000,
))

add_startup("greengrid", dict(
    name="GreenGrid", founder="Liam O'Brien", sector="CleanTech",
    stage="Seed", location="Austin, USA",
    description="GreenGrid is a peer-to-peer renewable energy trading platform built "
                "on a private blockchain. Households with solar installations can sell "
                "excess generation directly to neighbours at transparent market rates, "
                "bypassing utility intermediaries. We currently operate in three Texas "
                "grid zones with 1,200 active prosumers and $280K in annualised "
                "transaction volume.",
    revenue=210_000, website="https://greengrid.energy",
    team_size=9, linkedin="https://linkedin.com/company/greengrid-energy",
    target_market="Residential solar owners and eco-conscious urban renters",
    business_model="Marketplace", country="United States",
    mrr=17_500, growth_rate=18.2, runway=18, burn_rate=62_000,
))

add_startup("medpulse", dict(
    name="MedPulse", founder="Aisha Kone", sector="HealthTech",
    stage="Pre-Seed", location="Boston, USA",
    description="MedPulse builds remote patient monitoring infrastructure for "
                "post-discharge cardiac care. Our IoT wearable patches transmit "
                "continuous ECG, SpO2 and blood pressure data to a cloud dashboard "
                "where ML anomaly detection flags deterioration up to 6 hours before "
                "clinical presentation. In our pilot with Mass General Brigham, "
                "30-day readmission rates dropped 41%.",
    revenue=0, website="https://medpulse.health",
    team_size=5, linkedin="https://linkedin.com/company/medpulse",
    target_market="Hospital systems and cardiology outpatient clinics",
    business_model="B2B", country="United States",
    mrr=0, growth_rate=0, runway=14, burn_rate=38_000,
))

add_startup("codementorai", dict(
    name="CodeMentor AI", founder="Raj Patel", sector="EdTech",
    stage="Seed", location="Bangalore, India",
    description="CodeMentor AI is an adaptive learning platform for self-taught "
                "developers. Our LLM-powered curriculum engine generates personalised "
                "learning paths from a 20-minute diagnostic, then provides real-time "
                "code review, automated pair programming sessions and peer matching. "
                "We have 48,000 active learners across 90 countries and a 4.8/5 "
                "NPS score from paying subscribers.",
    revenue=380_000, website="https://codementor.ai",
    team_size=22, linkedin="https://linkedin.com/company/codementorai",
    target_market="Self-taught developers aged 18–35 seeking employment",
    business_model="B2C", country="India",
    mrr=31_600, growth_rate=9.8, runway=26, burn_rate=48_000,
))

add_startup("cybershield", dict(
    name="CyberShield", founder="Tom Zhang", sector="Cybersecurity",
    stage="Series B", location="New York, USA",
    description="CyberShield is a zero-trust security platform that uses behavioural "
                "AI to detect and neutralise insider threats in real time. Our "
                "agent-based solution monitors user activity, device state and network "
                "flows, assigning continuous trust scores without disrupting workflows. "
                "Current ARR is $9.2M with 34 enterprise clients including three "
                "Fortune 500 financial institutions.",
    revenue=9_200_000, website="https://cybershield.io",
    team_size=67, linkedin="https://linkedin.com/company/cybershield",
    target_market="Enterprise financial services and healthcare CISOs",
    business_model="B2B", country="United States",
    mrr=766_000, growth_rate=7.1, runway=36, burn_rate=420_000,
))

add_startup("finflow", dict(
    name="FinFlow", founder="Carlos Mendez", sector="FinTech",
    stage="Pre-Seed", location="Miami, USA",
    description="FinFlow is an open banking cash flow intelligence dashboard for "
                "SMB owners. We aggregate data from 2,400 bank connections via Plaid "
                "and Teller, then apply ML forecasting to predict insolvency risk, "
                "flag anomalous spend and surface working capital optimisation "
                "recommendations. Our waitlist has 3,200 signups from QBO and Xero "
                "user communities.",
    revenue=42_000, website="https://getfinflow.com",
    team_size=4, linkedin="https://linkedin.com/company/finflow",
    target_market="SMB owners with $500K–$10M annual revenue",
    business_model="SaaS", country="United States",
    mrr=3_500, growth_rate=22.0, runway=12, burn_rate=28_000,
))

add_startup("theralink", dict(
    name="TheraLink", founder="Jin Li", sector="Mental Health",
    stage="Seed", location="Seattle, USA",
    description="TheraLink is a clinically-validated digital mental health platform "
                "that pairs users with trained peer support specialists, triaged by "
                "an NLP-powered intake system. Our proprietary SAFE-score model "
                "escalates high-risk sessions to licensed clinicians within 4 minutes. "
                "We serve 14 enterprise EAP contracts and have delivered 220,000 "
                "support sessions with a 91% user satisfaction rate.",
    revenue=620_000, website="https://theralink.care",
    team_size=31, linkedin="https://linkedin.com/company/theralink",
    target_market="Mid-to-large employers and employee assistance programme providers",
    business_model="B2B", country="United States",
    mrr=51_600, growth_rate=14.3, runway=20, burn_rate=78_000,
))

add_startup("recruitlens", dict(
    name="RecruitLens", founder="Yemi Adeyemi", sector="HR Tech",
    stage="Series A", location="London, UK",
    description="RecruitLens is a bias-reduction hiring platform that anonymises CVs, "
                "structures interview scorecards and applies predictive analytics to "
                "surface diverse candidate slates. Clients report a 2.3x improvement "
                "in underrepresented hire rates within two quarters. We are live in "
                "180 companies across the UK and EU, with ARR of £1.1M and a "
                "land-and-expand motion averaging 3.2x NRR.",
    revenue=1_100_000, website="https://recruitlens.io",
    team_size=24, linkedin="https://linkedin.com/company/recruitlens",
    target_market="Head of Talent and CPOs at 500–5,000 employee tech companies",
    business_model="B2B", country="United Kingdom",
    mrr=91_600, growth_rate=11.2, runway=28, burn_rate=110_000,
))

add_startup("agribot", dict(
    name="AgriBot", founder="Fatima Al-Hassan", sector="AgriTech",
    stage="Seed", location="Des Moines, USA",
    description="AgriBot builds autonomous drone fleet management software for "
                "precision agriculture. Farm operators deploy our fixed-wing and "
                "multirotor fleets for crop health imaging, variable-rate spraying "
                "and yield forecasting. Our CV models detect 47 crop diseases with "
                "94% accuracy. We manage 380,000 acres under contract across the "
                "US Midwest with $290K ARR.",
    revenue=290_000, website="https://agribot.farm",
    team_size=13, linkedin="https://linkedin.com/company/agribot",
    target_market="Large-scale row crop operators (1,000+ acres)",
    business_model="SaaS", country="United States",
    mrr=24_100, growth_rate=16.8, runway=17, burn_rate=55_000,
))

add_startup("paymesh", dict(
    name="PayMesh", founder="Nadia Okonkwo", sector="FinTech",
    stage="Series B", location="Lagos, Nigeria",
    description="PayMesh is a cross-border B2B payment infrastructure layer using "
                "stablecoin settlement rails to enable instant, sub-1% fee "
                "transactions between African and global counterparties. Our API "
                "is embedded in 60+ ERP and procurement platforms. We processed "
                "$340M in transaction volume in 2024 and are live in 22 African "
                "markets with regulatory licences in 14 jurisdictions.",
    revenue=4_800_000, website="https://paymesh.finance",
    team_size=89, linkedin="https://linkedin.com/company/paymesh",
    target_market="African SMEs and multinationals paying African suppliers",
    business_model="B2B", country="Nigeria",
    mrr=400_000, growth_rate=19.5, runway=40, burn_rate=280_000,
))

add_startup("carbontrace", dict(
    name="CarbonTrace", founder="Ben Hooper", sector="CleanTech",
    stage="Pre-Seed", location="London, UK",
    description="CarbonTrace automates Scope 1–3 emissions measurement for SMEs. "
                "We integrate natively with QuickBooks, Xero, SAP and supply chain "
                "APIs to extract activity data, apply IPCC-aligned emission factors "
                "and generate audit-ready GHG reports in 20 minutes rather than "
                "20 weeks. Our CSRD and TCFD report templates are used by 140 "
                "companies in our beta.",
    revenue=28_000, website="https://carbontrace.io",
    team_size=6, linkedin="https://linkedin.com/company/carbontrace",
    target_market="CFOs and sustainability leads at 50–500 employee SMEs in the EU",
    business_model="SaaS", country="United Kingdom",
    mrr=2_300, growth_rate=31.0, runway=11, burn_rate=24_000,
))

# ── 4. INVESTORS (9) ──────────────────────────────────────────────────────────
add_investor("sarahchen", dict(
    name="Sarah Chen", firm="Sequoia Capital", sector="AI/ML",
    stage="Seed, Series A",
    location="Menlo Park, USA",
    thesis="I back AI-native companies applying large language models and deep learning "
           "to transform consumer commerce, personalisation and recommendation systems. "
           "I am particularly interested in infrastructure-layer AI plays that develop "
           "compounding data moats and can expand into adjacent verticals. Strong "
           "preference for technical founders with prior ML research or product experience "
           "at top-tier companies.",
    ticket_size=750_000, website="https://sequoiacap.com",
    fund_size=8_500_000_000,
    portfolio_count=42,
    notable_investments="Stripe, Figma, Scale AI, Hugging Face",
    geo_focus="North America, Europe",
    co_invest_pref="Lead",
    decision_timeline="2–4 Weeks",
    business_model_pref="B2B",
    linkedin="https://linkedin.com/in/sarahchen-sequoia",
    investments_per_year=8,
))

add_investor("davidokafor", dict(
    name="David Okafor", firm="Andreessen Horowitz", sector="FinTech",
    stage="Series A, Series B",
    location="San Francisco, USA",
    thesis="I invest in infrastructure-layer fintech companies disrupting cross-border "
           "payments, open banking and embedded finance, with a strong focus on "
           "high-growth emerging markets in Africa, Southeast Asia and Latin America. "
           "I look for teams with deep regulatory knowledge and network effects "
           "that become harder to displace as transaction volume grows.",
    ticket_size=3_000_000, website="https://a16z.com",
    fund_size=35_000_000_000,
    portfolio_count=61,
    notable_investments="Robinhood, Chime, Chipper Cash, Flutterwave",
    geo_focus="Africa, Southeast Asia, North America, Latin America",
    co_invest_pref="Lead",
    decision_timeline="3–6 Weeks",
    business_model_pref="B2B",
    linkedin="https://linkedin.com/in/davidokafor-a16z",
    investments_per_year=10,
))

add_investor("emilywatson", dict(
    name="Emily Watson", firm="Breakthrough Energy Ventures", sector="CleanTech",
    stage="Seed, Series A",
    location="Seattle, USA",
    thesis="I fund science-based climate technology companies with a clear and "
           "measurable pathway to gigaton-scale CO2 reduction. My focus areas include "
           "grid modernisation, distributed renewable energy, industrial decarbonisation "
           "and carbon measurement tools. I prioritise founders who combine deep "
           "technical credibility with a pragmatic commercialisation strategy.",
    ticket_size=1_000_000, website="https://breakthroughenergy.org/investing",
    fund_size=2_000_000_000,
    portfolio_count=28,
    notable_investments="Commonwealth Fusion, Form Energy, Lilac Solutions",
    geo_focus="North America, Europe",
    co_invest_pref="Lead",
    decision_timeline="4–8 Weeks",
    business_model_pref="B2B",
    linkedin="https://linkedin.com/in/emilywatson-bev",
    investments_per_year=6,
))

add_investor("marcuslee", dict(
    name="Marcus Lee", firm="Tiger Global Management", sector="Cybersecurity",
    stage="Series B, Series C+",
    location="New York, USA",
    thesis="I partner with enterprise cybersecurity companies using AI and behavioural "
           "analytics to solve identity, zero-trust access and insider threat challenges "
           "at scale. I look for products that are already deeply embedded in enterprise "
           "workflows, with strong NRR above 120% and a clear path to platform expansion "
           "across the security stack.",
    ticket_size=10_000_000, website="https://tigerglobal.com",
    fund_size=50_000_000_000,
    portfolio_count=95,
    notable_investments="CrowdStrike, SentinelOne, Netskope",
    geo_focus="North America, Europe, Israel",
    co_invest_pref="Lead",
    decision_timeline="1–2 Weeks",
    business_model_pref="B2B",
    linkedin="https://linkedin.com/in/marcuslee-tigerglobal",
    investments_per_year=14,
))

add_investor("priyanair", dict(
    name="Priya Nair", firm="Khosla Ventures", sector="HealthTech",
    stage="Pre-Seed, Seed",
    location="Palo Alto, USA",
    thesis="I fund early-stage digital health and medtech companies using machine "
           "learning, wearables and remote monitoring to shift healthcare from reactive "
           "to predictive. I am drawn to founders with strong clinical validation data "
           "and existing hospital or payer relationships. Particular interest in "
           "cardiovascular, oncology and post-acute care applications.",
    ticket_size=500_000, website="https://khoslaventures.com",
    fund_size=1_500_000_000,
    portfolio_count=33,
    notable_investments="Omada Health, Lyra Health, Current Health",
    geo_focus="North America",
    co_invest_pref="Lead",
    decision_timeline="2–4 Weeks",
    business_model_pref="B2B",
    linkedin="https://linkedin.com/in/priyanair-khosla",
    investments_per_year=9,
))

add_investor("jamesoconnor", dict(
    name="James O'Connor", firm="Union Square Ventures", sector="EdTech",
    stage="Seed, Series A",
    location="New York, USA",
    thesis="I invest in education technology platforms that democratise access to "
           "quality learning through AI-driven personalisation, community content "
           "and immersive experiences. I am especially interested in platforms "
           "serving non-traditional learners — adult re-skilling, emerging market "
           "students and vocational pathways — where unit economics improve with scale.",
    ticket_size=800_000, website="https://usv.com",
    fund_size=1_200_000_000,
    portfolio_count=47,
    notable_investments="Duolingo, Codecademy, Khan Academy",
    geo_focus="North America, Europe, South Asia",
    co_invest_pref="Either",
    decision_timeline="3–5 Weeks",
    business_model_pref="B2C",
    linkedin="https://linkedin.com/in/jamesoconnor-usv",
    investments_per_year=7,
))

add_investor("fatoudiallo", dict(
    name="Fatou Diallo", firm="Accel Partners", sector="HR Tech",
    stage="Series A, Series B",
    location="London, UK",
    thesis="I back future-of-work platforms leveraging data and AI to solve hiring "
           "bias, workforce planning and employee engagement for global enterprise "
           "clients. I look for strong land-and-expand SaaS motions with NRR above "
           "115%, clear CHRO-level sponsorship and a defensible data network effect "
           "that compounds as more organisations join the platform.",
    ticket_size=2_000_000, website="https://accel.com",
    fund_size=3_000_000_000,
    portfolio_count=78,
    notable_investments="Workday, Personio, HiBob, Deel",
    geo_focus="Europe, North America",
    co_invest_pref="Lead",
    decision_timeline="2–4 Weeks",
    business_model_pref="B2B",
    linkedin="https://linkedin.com/in/fatoudiallo-accel",
    investments_per_year=11,
))

add_investor("kevinpark", dict(
    name="Kevin Park", firm="Founders Fund", sector="AI/ML",
    stage="Series A, Series B",
    location="San Francisco, USA",
    thesis="I invest in transformative AI companies building proprietary foundation "
           "models or vertical AI infrastructure that creates compounding defensibility "
           "in high-value B2B verticals. I am sceptical of thin wrappers and highly "
           "interested in teams that have accumulated unique training data, "
           "domain-specific fine-tuning pipelines or novel inference optimisation "
           "that cannot be replicated by hyperscalers.",
    ticket_size=4_000_000, website="https://foundersfund.com",
    fund_size=5_000_000_000,
    portfolio_count=55,
    notable_investments="Palantir, Anduril, Neuralink, Vicarious",
    geo_focus="North America",
    co_invest_pref="Lead",
    decision_timeline="1–3 Weeks",
    business_model_pref="B2B",
    linkedin="https://linkedin.com/in/kevinpark-ff",
    investments_per_year=8,
))

add_investor("rachelkim", dict(
    name="Rachel Kim", firm="General Catalyst", sector="Mental Health",
    stage="Seed, Series A",
    location="Boston, USA",
    thesis="I fund digital mental health platforms that combine clinical rigour with "
           "consumer-grade UX to scale access to therapy, peer support and crisis "
           "intervention. I prioritise companies with published outcomes data, "
           "existing payer or employer contracts, and a clear regulatory pathway. "
           "Strong interest in AI-assisted triage models that reduce time-to-care "
           "without sacrificing clinical quality.",
    ticket_size=1_200_000, website="https://generalcatalyst.com",
    fund_size=6_000_000_000,
    portfolio_count=44,
    notable_investments="Headspace, Spring Health, Brightline, Calm",
    geo_focus="North America, Europe",
    co_invest_pref="Either",
    decision_timeline="3–5 Weeks",
    business_model_pref="B2B",
    linkedin="https://linkedin.com/in/rachelkim-gc",
    investments_per_year=9,
))

con.commit()
con.close()

# ── 5. PRINT CREDENTIALS TABLE ─────────────────────────────────────────────────
print("\n" + "="*62)
print("  StartMatch — Demo Credentials (all passwords: Demo@1234)")
print("="*62)
print(f"  {'Username':<20} {'Role':<10} {'Entity'}")
print("-"*62)
creds = [
    ("neuralcart",   "Startup",  "NeuralCart"),
    ("greengrid",    "Startup",  "GreenGrid"),
    ("medpulse",     "Startup",  "MedPulse"),
    ("codementorai", "Startup",  "CodeMentor AI"),
    ("cybershield",  "Startup",  "CyberShield"),
    ("finflow",      "Startup",  "FinFlow"),
    ("theralink",    "Startup",  "TheraLink"),
    ("recruitlens",  "Startup",  "RecruitLens"),
    ("agribot",      "Startup",  "AgriBot"),
    ("paymesh",      "Startup",  "PayMesh"),
    ("carbontrace",  "Startup",  "CarbonTrace"),
    ("sarahchen",    "Investor", "Sarah Chen — Sequoia"),
    ("davidokafor",  "Investor", "David Okafor — a16z"),
    ("emilywatson",  "Investor", "Emily Watson — Breakthrough Energy"),
    ("marcuslee",    "Investor", "Marcus Lee — Tiger Global"),
    ("priyanair",    "Investor", "Priya Nair — Khosla"),
    ("jamesoconnor", "Investor", "James O'Connor — USV"),
    ("fatoudiallo",  "Investor", "Fatou Diallo — Accel"),
    ("kevinpark",    "Investor", "Kevin Park — Founders Fund"),
    ("rachelkim",    "Investor", "Rachel Kim — General Catalyst"),
]
for u, r, e in creds:
    print(f"  {u:<20} {r:<10} {e}")
print("="*62)
print("  All accounts ready. Run: streamlit run app.py --server.fileWatcherType none")
print("="*62 + "\n")