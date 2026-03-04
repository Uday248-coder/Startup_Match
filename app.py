import streamlit as st
import pandas as pd
import numpy as np
import sqlite3, hashlib, re, os, uuid
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objects as go

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════
DB = "data/db.sqlite"
SECTORS    = ["AI/ML","FinTech","HealthTech","EdTech","CleanTech","Cybersecurity",
              "AgriTech","HR Tech","Manufacturing","Logistics","Mental Health",
              "SaaS","E-commerce","Web3","Other"]
STAGES     = ["Pre-Seed","Seed","Series A","Series B","Series C+"]
BIZ_MODELS = ["B2B","B2C","B2B2C","Marketplace","SaaS","Deep Tech","Other"]
GEO_REGIONS= ["North America","Europe","South Asia","Southeast Asia",
               "Africa","Latin America","Middle East","Global"]
CO_INVEST  = ["Lead","Follow","Either"]
DECISION_TL= ["1–2 Weeks","2–4 Weeks","1–2 Months","2–3 Months","3+ Months"]
SECTOR_COLORS = {
    "AI/ML":"#818cf8","FinTech":"#2dd4bf","HealthTech":"#34d399",
    "EdTech":"#fbbf24","CleanTech":"#4ade80","Cybersecurity":"#f87171",
    "AgriTech":"#a3e635","HR Tech":"#c084fc","Manufacturing":"#fb923c",
    "Logistics":"#38bdf8","Mental Health":"#f472b6","SaaS":"#818cf8",
    "E-commerce":"#fb923c","Web3":"#a78bfa","Other":"#94a3b8",
}
STAGE_TICKET = {
    "Pre-Seed":(0,500_000),"Seed":(100_000,2_000_000),
    "Series A":(1_000_000,10_000_000),"Series B":(5_000_000,30_000_000),
    "Series C+":(20_000_000,200_000_000),
}
STOP = {"a","an","the","and","or","but","in","on","at","to","for","of","with",
        "by","from","is","are","was","were","be","been","have","has","had","do",
        "does","did","will","would","could","should","may","might","that","this",
        "these","those","it","its","as","into","their","our","we","they","using",
        "use","used","via","across","through","within","between","such","also",
        "both","each","more","most","over","than","up","out","can","not","no",
        "all","any","if","about","after","before","during","new","large","high",
        "low","key","based","build","built","help","helps","scale","company",
        "startup","investor","fund","capital","growth","platform","tech",
        "technology","solution","solutions","provides","provide","focused","focus",
        "strong","clear","deep","early","stage","market","data","model","models",
        "team","product","business","global","world","first","users","clients"}

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="StartMatch", layout="wide",
                   initial_sidebar_state="collapsed")

# ═══════════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── BASE ── */
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"]>section,.main,.block-container,
[data-testid="stVerticalBlock"],[data-testid="stVerticalBlockBorderWrapper"]{
  background:#0d0d14 !important;
  color:#f1f5f9 !important;
  font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif !important;
}
.block-container{ padding-top:1.5rem !important; max-width:1200px !important; }

/* ── HIDE SIDEBAR ENTIRELY ── */
[data-testid="stSidebar"]{ display:none !important; }
[data-testid="stSidebarCollapsedControl"]{ display:none !important; }

/* ── TYPOGRAPHY ── */
h1{ font-size:1.9rem !important; font-weight:800 !important;
    letter-spacing:-.03em !important; color:#f8fafc !important; }
h2{ font-size:1.35rem !important; font-weight:700 !important;
    letter-spacing:-.02em !important; color:#f1f5f9 !important; }
h3{ font-size:1.05rem !important; font-weight:700 !important;
    color:#e2e8f0 !important; }
h4{ font-size:.9rem !important; font-weight:700 !important;
    color:#cbd5e1 !important; }
p,span,div,label,li,td,th,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"]*{ color:#e2e8f0 !important; }
.stCaption,[data-testid="stCaptionContainer"]*{
  color:#64748b !important; font-size:.78rem !important;
}

/* ── NAV TABS ── */
[data-testid="stTabs"] [data-baseweb="tab-list"]{
  background:transparent !important;
  border-bottom:1px solid #1a1a2e !important;
  border-radius:0 !important;
  padding:0 2px !important;
  gap:0 !important;
  margin-bottom:28px !important;
}
button[data-baseweb="tab"]{
  border-radius:0 !important;
  color:#64748b !important;
  background:transparent !important;
  padding:0 18px 14px !important;
  font-size:.875rem !important;
  font-weight:600 !important;
  letter-spacing:.005em !important;
  border-bottom:2px solid transparent !important;
  margin-bottom:-1px !important;
  transition:color .15s, border-color .15s !important;
}
button[data-baseweb="tab"]:hover{ color:#cbd5e1 !important; }
button[data-baseweb="tab"][aria-selected="true"]{
  color:#f8fafc !important; font-weight:700 !important;
  border-bottom:2px solid #f59e0b !important;
  background:transparent !important;
  box-shadow:none !important;
}

/* ── CARDS ── */
[data-testid="stVerticalBlockBorderWrapper"]{
  background:#13131f !important;
  border:1px solid #1a1a2e !important;
  border-radius:12px !important;
  transition:border-color .2s, box-shadow .2s !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover{
  border-color:#2a2a42 !important;
  box-shadow:0 4px 24px rgba(0,0,0,.4) !important;
}

/* ── PROGRESS BAR ── */
[data-testid="stProgressBar"]>div{
  background:#1a1a2e !important; border-radius:999px !important; height:4px !important;
}
[data-testid="stProgressBar"]>div>div{
  border-radius:999px !important;
  background:linear-gradient(90deg,#92400e,#f59e0b) !important;
}

/* ── PRIMARY BUTTON ── */
.stButton>button{
  background:linear-gradient(135deg,#b45309,#f59e0b) !important;
  color:#0a0a0f !important; border:none !important;
  border-radius:8px !important; font-weight:700 !important;
  font-size:.875rem !important; padding:9px 20px !important;
  transition:all .18s !important;
  box-shadow:0 1px 12px rgba(245,158,11,.25) !important;
  letter-spacing:.01em !important;
}
.stButton>button:hover{
  background:linear-gradient(135deg,#d97706,#fbbf24) !important;
  box-shadow:0 4px 20px rgba(245,158,11,.45) !important;
  transform:translateY(-1px) !important;
}
div[data-testid="column"]:last-child .stButton>button,
.ghost-btn .stButton>button{
  background:transparent !important;
  color:#94a3b8 !important;
  border:1px solid #2a2a42 !important;
  box-shadow:none !important;
}
div[data-testid="column"]:last-child .stButton>button:hover,
.ghost-btn .stButton>button:hover{
  border-color:#64748b !important;
  color:#f1f5f9 !important;
  transform:none !important;
}

/* ── SIGN OUT BUTTON — always ghost style ── */
.signout-btn .stButton>button{
  background:transparent !important;
  color:#64748b !important;
  border:1px solid #2a2a42 !important;
  box-shadow:none !important;
  padding:6px 14px !important;
  font-size:.78rem !important;
  font-weight:600 !important;
}
.signout-btn .stButton>button:hover{
  border-color:#f87171 !important;
  color:#f87171 !important;
  transform:none !important;
  box-shadow:none !important;
}

/* ── LINK BUTTON ── */
div[data-testid="stLinkButton"] a{
  background:linear-gradient(135deg,#b45309,#f59e0b) !important;
  color:#0a0a0f !important; border:none !important;
  border-radius:8px !important; padding:9px 20px !important;
  font-weight:700 !important; font-size:.875rem !important;
  text-decoration:none !important; display:inline-block !important;
  box-shadow:0 1px 12px rgba(245,158,11,.25) !important;
  transition:all .18s !important;
}
div[data-testid="stLinkButton"] a:hover{
  box-shadow:0 4px 20px rgba(245,158,11,.45) !important;
  transform:translateY(-1px) !important;
}

/* ── INPUTS ── */
input[type="text"],input[type="password"],input[type="number"],textarea,
[data-baseweb="input"] input,[data-baseweb="textarea"] textarea{
  background:#0d0d14 !important; color:#f1f5f9 !important;
  border:1px solid #1a1a2e !important; border-radius:8px !important;
  font-size:.9rem !important; transition:border-color .15s !important;
}
input:focus,textarea:focus{
  border-color:#f59e0b !important;
  box-shadow:0 0 0 3px rgba(245,158,11,.12) !important;
}
input::placeholder,textarea::placeholder{ color:#2a2a42 !important; }
[data-testid="stTextInput"]>label,[data-testid="stTextArea"]>label,
[data-testid="stNumberInput"]>label{ color:#94a3b8 !important;
  font-size:.8rem !important; font-weight:600 !important;
  text-transform:uppercase !important; letter-spacing:.07em !important;
}

/* ── SELECT ── */
[data-baseweb="select"]>div:first-child{
  background:#0d0d14 !important; border:1px solid #1a1a2e !important;
  border-radius:8px !important;
}
[data-baseweb="select"] span,[data-baseweb="select"] div{ color:#f1f5f9 !important; }
[data-baseweb="popover"],[data-baseweb="menu"]{
  background:#13131f !important; border:1px solid #1a1a2e !important;
}
[data-baseweb="menu"] li{ color:#e2e8f0 !important; }
[data-baseweb="menu"] li:hover{ background:#1a1a2e !important; }
[data-baseweb="tag"]{ background:#92400e !important; border-radius:6px !important; }
[data-baseweb="tag"] span{ color:#fbbf24 !important; }
[data-testid="stSelectbox"]>label,[data-testid="stMultiSelect"]>label{
  color:#94a3b8 !important; font-size:.8rem !important;
  font-weight:600 !important; text-transform:uppercase !important;
  letter-spacing:.07em !important;
}

/* ── METRICS ── */
[data-testid="stMetric"]{
  background:#13131f !important; border:1px solid #1a1a2e !important;
  border-radius:10px !important; padding:16px 18px !important;
}
[data-testid="stMetricLabel"] p{
  font-size:.68rem !important; font-weight:700 !important;
  color:#64748b !important; text-transform:uppercase !important;
  letter-spacing:.09em !important;
}
[data-testid="stMetricValue"]{
  color:#f8fafc !important; font-size:1.1rem !important; font-weight:800 !important;
}
[data-testid="stMetricDelta"] svg{ display:none !important; }

/* ── RADIO ── */
[data-testid="stRadio"] label p{ color:#e2e8f0 !important; }
[data-testid="stRadio"]>label{
  color:#94a3b8 !important; font-size:.8rem !important;
  font-weight:600 !important; text-transform:uppercase !important;
  letter-spacing:.07em !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"]{ border-radius:10px !important; }
[data-testid="stAlert"] p{ color:inherit !important; }
[data-testid="stInfo"]{
  background:rgba(245,158,11,.07) !important;
  border:1px solid rgba(245,158,11,.25) !important;
}
[data-testid="stInfo"] p{ color:#fbbf24 !important; }
[data-testid="stSuccess"]{
  background:rgba(52,211,153,.07) !important;
  border:1px solid rgba(52,211,153,.25) !important;
}
[data-testid="stError"]{
  background:rgba(248,113,113,.07) !important;
  border:1px solid rgba(248,113,113,.25) !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"]{
  background:#13131f !important; border:1px solid #1a1a2e !important;
  border-radius:10px !important;
}
[data-testid="stExpander"] summary{ color:#e2e8f0 !important; }
[data-testid="stExpander"] summary:hover{ color:#fbbf24 !important; }
[data-testid="stExpander"] summary svg{ fill:#64748b !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar{ width:4px; height:4px; }
::-webkit-scrollbar-track{ background:#0d0d14; }
::-webkit-scrollbar-thumb{ background:#1a1a2e; border-radius:4px; }
::-webkit-scrollbar-thumb:hover{ background:#f59e0b; }

/* ── MISC ── */
hr{ border-color:#1a1a2e !important; margin:20px 0 !important; }
#MainMenu,footer,[data-testid="stDecoration"],[data-testid="stToolbar"],
[data-testid="stHeader"]{
  background:transparent !important;
  border-bottom:none !important;
  height:0 !important;
  min-height:0 !important;
  overflow:visible !important;
}
[data-testid="stHeader"]>*{ display:none !important; }
[data-testid="stNumberInput"] button{
  background:#1a1a2e !important; border:1px solid #2a2a42 !important;
  color:#94a3b8 !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════════════════════
def get_con():
    os.makedirs("data", exist_ok=True)
    con = sqlite3.connect(DB, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = get_con()
    con.executescript("""
        CREATE TABLE IF NOT EXISTS startups (
            id TEXT PRIMARY KEY, name TEXT, founder TEXT, sector TEXT,
            stage TEXT, location TEXT, description TEXT,
            revenue REAL DEFAULT 0, website TEXT,
            team_size INTEGER DEFAULT 0, linkedin TEXT DEFAULT '',
            target_market TEXT DEFAULT '', business_model TEXT DEFAULT '',
            country TEXT DEFAULT '', mrr REAL DEFAULT 0,
            growth_rate REAL DEFAULT 0, runway INTEGER DEFAULT 0,
            burn_rate REAL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS investors (
            id TEXT PRIMARY KEY, name TEXT, firm TEXT, sector TEXT,
            stage TEXT, location TEXT, thesis TEXT,
            ticket_size REAL DEFAULT 0, website TEXT,
            fund_size REAL DEFAULT 0, portfolio_count INTEGER DEFAULT 0,
            notable_investments TEXT DEFAULT '', geo_focus TEXT DEFAULT '',
            co_invest_pref TEXT DEFAULT '', decision_timeline TEXT DEFAULT '',
            business_model_pref TEXT DEFAULT '', linkedin TEXT DEFAULT '',
            investments_per_year INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, password TEXT NOT NULL,
            role TEXT NOT NULL, entity_id TEXT NOT NULL
        );
    """)
    new_s = [("team_size","INTEGER DEFAULT 0"),("linkedin","TEXT DEFAULT ''"),
             ("target_market","TEXT DEFAULT ''"),("business_model","TEXT DEFAULT ''"),
             ("country","TEXT DEFAULT ''"),("mrr","REAL DEFAULT 0"),
             ("growth_rate","REAL DEFAULT 0"),("runway","INTEGER DEFAULT 0"),
             ("burn_rate","REAL DEFAULT 0")]
    new_i = [("fund_size","REAL DEFAULT 0"),("portfolio_count","INTEGER DEFAULT 0"),
             ("notable_investments","TEXT DEFAULT ''"),("geo_focus","TEXT DEFAULT ''"),
             ("co_invest_pref","TEXT DEFAULT ''"),("decision_timeline","TEXT DEFAULT ''"),
             ("business_model_pref","TEXT DEFAULT ''"),("linkedin","TEXT DEFAULT ''"),
             ("investments_per_year","INTEGER DEFAULT 0")]
    for col,typ in new_s:
        try: con.execute(f"ALTER TABLE startups ADD COLUMN {col} {typ}")
        except: pass
    for col,typ in new_i:
        try: con.execute(f"ALTER TABLE investors ADD COLUMN {col} {typ}")
        except: pass
    con.commit(); con.close()

init_db()

# ── CRUD ───────────────────────────────────────────────────────────────────────
def qry(sql, params=(), many=False, write=False):
    con = get_con(); cur = con.execute(sql, params)
    if write: con.commit(); con.close(); return None
    res = cur.fetchall() if many else cur.fetchone()
    con.close()
    return [dict(r) for r in res] if many else (dict(res) if res else None)

def get_startup(eid):  return qry("SELECT * FROM startups  WHERE id=?", (eid,))
def get_investor(eid): return qry("SELECT * FROM investors WHERE id=?", (eid,))
def all_startups():    return qry("SELECT * FROM startups",  many=True) or []
def all_investors():   return qry("SELECT * FROM investors", many=True) or []
def get_user(u):       return qry("SELECT * FROM users WHERE username=?", (u,))
def hash_pw(p):        return hashlib.sha256(p.encode()).hexdigest()

def registered_opposite(role):
    con = get_con()
    if role == "Startup":
        ids = [r[0] for r in con.execute(
            "SELECT entity_id FROM users WHERE role='Investor'").fetchall()]
        tbl = "investors"
    else:
        ids = [r[0] for r in con.execute(
            "SELECT entity_id FROM users WHERE role='Startup'").fetchall()]
        tbl = "startups"
    con.close()
    if not ids: return []
    ph = ",".join("?"*len(ids))
    return qry(f"SELECT * FROM {tbl} WHERE id IN ({ph})", ids, many=True) or []

def ins_startup(d, username, pw):
    eid = str(uuid.uuid4())
    qry("""INSERT INTO startups VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (eid,d['name'],d['founder'],d['sector'],d['stage'],d['location'],
         d['description'],d['revenue'],d['website'],d['team_size'],d['linkedin'],
         d['target_market'],d['business_model'],d['country'],d['mrr'],
         d['growth_rate'],d['runway'],d['burn_rate']), write=True)
    qry("INSERT INTO users VALUES(?,?,?,?)",(username,hash_pw(pw),"Startup",eid),write=True)

def ins_investor(d, username, pw):
    eid = str(uuid.uuid4())
    qry("""INSERT INTO investors VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (eid,d['name'],d['firm'],d['sector'],d['stage'],d['location'],
         d['thesis'],d['ticket_size'],d['website'],d['fund_size'],
         d['portfolio_count'],d['notable_investments'],d['geo_focus'],
         d['co_invest_pref'],d['decision_timeline'],d['business_model_pref'],
         d['linkedin'],d['investments_per_year']), write=True)
    qry("INSERT INTO users VALUES(?,?,?,?)",(username,hash_pw(pw),"Investor",eid),write=True)

def upd_startup(d):
    qry("""UPDATE startups SET name=?,founder=?,sector=?,stage=?,location=?,
           description=?,revenue=?,website=?,team_size=?,linkedin=?,
           target_market=?,business_model=?,country=?,mrr=?,growth_rate=?,
           runway=?,burn_rate=? WHERE id=?""",
        (d['name'],d['founder'],d['sector'],d['stage'],d['location'],
         d['description'],d['revenue'],d['website'],d['team_size'],d['linkedin'],
         d['target_market'],d['business_model'],d['country'],d['mrr'],
         d['growth_rate'],d['runway'],d['burn_rate'],d['id']), write=True)

def upd_investor(d):
    qry("""UPDATE investors SET name=?,firm=?,sector=?,stage=?,location=?,
           thesis=?,ticket_size=?,website=?,fund_size=?,portfolio_count=?,
           notable_investments=?,geo_focus=?,co_invest_pref=?,
           decision_timeline=?,business_model_pref=?,linkedin=?,
           investments_per_year=? WHERE id=?""",
        (d['name'],d['firm'],d['sector'],d['stage'],d['location'],
         d['thesis'],d['ticket_size'],d['website'],d['fund_size'],
         d['portfolio_count'],d['notable_investments'],d['geo_focus'],
         d['co_invest_pref'],d['decision_timeline'],d['business_model_pref'],
         d['linkedin'],d['investments_per_year'],d['id']), write=True)

# ═══════════════════════════════════════════════════════════════════════════════
# AI MODEL + MATCHING
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="Loading AI model…")
def get_model(): return SentenceTransformer("all-MiniLM-L6-v2")

def emb(t):  return get_model().encode([t or ""], convert_to_numpy=True)[0]
def embs(ts): return get_model().encode([t or "" for t in ts], convert_to_numpy=True)

def compute_matches(user):
    me = get_startup(user['entity_id']) if user['role']=="Startup" \
         else get_investor(user['entity_id'])
    if not me: return []
    corpus = registered_opposite(user['role'])
    if not corpus: return []
    my_txt = (me.get('description') if user['role']=="Startup" else me.get('thesis')) or ""
    ctxts  = [(e.get('thesis') if user['role']=="Startup" else e.get('description')) or ""
              for e in corpus]
    sims   = cosine_similarity([emb(my_txt)], embs(ctxts))[0]
    top    = np.argsort(sims)[::-1][:5]
    return [(corpus[i], round(float(sims[i])*100,1)) for i in top]


def compute_filtered_matches(user, f_sector=None, f_stage=None, f_location=None, f_biz_model=None):
    """
    Return top-5 matches from the opposite side, filtered by any combination
    of sector, stage, location and business model.

    For a Startup the counterpart is an Investor:
        sector       → investor.sector
        stage        → investor.stage  (comma-separated list)
        location     → investor.location
        biz_model    → investor.business_model_pref

    For an Investor the counterpart is a Startup:
        sector       → startup.sector
        stage        → startup.stage
        location     → startup.location
        biz_model    → startup.business_model

    Returns (results, total_before_filter, total_after_filter) where
    results is a list of (entity_dict, score).
    """
    me = get_startup(user['entity_id']) if user['role'] == "Startup" \
         else get_investor(user['entity_id'])
    if not me:
        return [], 0, 0

    corpus = registered_opposite(user['role'])
    total_before = len(corpus)
    if not corpus:
        return [], 0, 0

    filtered = []
    for e in corpus:
        if user['role'] == "Startup":
            # e is an investor
            if f_sector and f_sector != "All":
                if (e.get('sector') or '') != f_sector:
                    continue
            if f_stage and f_stage != "All":
                inv_stages = [s.strip() for s in (e.get('stage') or '').split(',')]
                if f_stage not in inv_stages:
                    continue
            if f_location and f_location.strip():
                if f_location.lower().strip() not in (e.get('location') or '').lower():
                    continue
            if f_biz_model and f_biz_model != "All":
                pref = (e.get('business_model_pref') or '').strip()
                if pref not in ('Any', f_biz_model):
                    continue
        else:
            # e is a startup
            if f_sector and f_sector != "All":
                if (e.get('sector') or '') != f_sector:
                    continue
            if f_stage and f_stage != "All":
                if (e.get('stage') or '') != f_stage:
                    continue
            if f_location and f_location.strip():
                if f_location.lower().strip() not in (e.get('location') or '').lower():
                    continue
            if f_biz_model and f_biz_model != "All":
                if (e.get('business_model') or '') != f_biz_model:
                    continue
        filtered.append(e)

    total_after = len(filtered)
    if not filtered:
        return [], total_before, 0

    my_txt = (me.get('description') if user['role'] == "Startup" else me.get('thesis')) or ""
    ctxts  = [(e.get('thesis') if user['role'] == "Startup" else e.get('description')) or ""
              for e in filtered]
    sims   = cosine_similarity([emb(my_txt)], embs(ctxts))[0]
    top    = np.argsort(sims)[::-1][:5]
    results = [(filtered[i], round(float(sims[i]) * 100, 1)) for i in top]
    return results, total_before, total_after


def radar_scores(s, inv, nlp):
    sec = 100.0 if s.get('sector')==inv.get('sector') else 15.0
    istg= [x.strip() for x in (inv.get('stage') or '').split(',')]
    stg = 100.0 if s.get('stage') in istg else 20.0
    loc = 100.0 if (s.get('location','') or '').lower().strip()==\
                   (inv.get('location','') or '').lower().strip() else 35.0
    tick= inv.get('ticket_size',0) or 0
    lo,hi=STAGE_TICKET.get(s.get('stage',''), (0,float('inf')))
    if hi==float('inf'): hi=max(tick*2,1)
    if lo<=tick<=hi:         sc=100.0
    elif tick<lo and lo>0:   sc=max(10.0,100-((lo-tick)/lo)*90)
    else:                    sc=max(10.0,100-((tick-max(hi,1))/max(hi,1))*60)
    return {"Sector":round(sec,1),"Stage":round(stg,1),"Location":round(loc,1),
            "Semantic":round(nlp,1),"Scale":round(sc,1)}

def kw_overlap(a, b, n=8):
    tok = lambda t: {w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', t or '')
                     if w.lower() not in STOP}
    pool = tok(a) & tok(b)
    if not pool: pool = tok(b)
    return sorted(pool)[:n]

# ═══════════════════════════════════════════════════════════════════════════════
# RULE-BASED GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════
def gen_summary(me, them, my_role, score):
    if my_role == "Startup":
        s,inv = me,them
        stgs  = [x.strip() for x in (inv.get('stage') or '').split(',')]
        s1 = (f"{inv.get('name','This investor')} at {inv.get('firm','their firm')} "
              f"invests in {inv.get('sector','technology')}, targeting "
              f"{' and '.join(stgs)} companies.")
        kw = kw_overlap(s.get('description',''), inv.get('thesis',''))
        s2 = (f"Shared thematic focus on {', '.join(kw[:3])} underpins the {score}% score."
              if kw else f"A {score}% semantic similarity reflects meaningful thesis alignment.")
        tick=inv.get('ticket_size',0) or 0
        lo,hi=STAGE_TICKET.get(s.get('stage',''), (0,float('inf')))
        if hi==float('inf'): hi=tick*2 or 1
        s3 = (f"Their typical ticket of ${tick:,.0f} aligns with {s.get('stage','')} funding norms."
              if lo<=tick<=hi else
              f"Note a potential size mismatch: ${tick:,.0f} vs typical ${lo:,.0f}–${hi:,.0f} "
              f"for {s.get('stage','')} stage.")
        return f"{s1} {s2} {s3}"
    else:
        inv,s = me,them
        rev = s.get('revenue',0) or 0
        s1 = (f"{s.get('name','This startup')} is a {s.get('stage','')} "
              f"{s.get('sector','')} company"
              f"{', founded by '+s['founder'] if s.get('founder') else ''}.")
        kw = kw_overlap(inv.get('thesis',''), s.get('description',''))
        s2 = (f"Key overlaps — {', '.join(kw[:4])} — directly map to your investment thesis."
              if kw else f"The {score}% score reflects strong thesis-to-pitch alignment.")
        s3 = (f"They report ${rev:,.0f} ARR" +
              (f" with {s.get('growth_rate',0):.1f}% MoM growth." if s.get('growth_rate',0)>0 else ".")
              if rev>0 else "Currently pre-revenue — high-potential early entry opportunity.")
        return f"{s1} {s2} {s3}"

def gen_red_flags(s, inv):
    flags = []
    if (s.get('sector') or '') != (inv.get('sector') or ''):
        flags.append(f"Sector mismatch — startup is in {s.get('sector','?')}, "
                     f"investor focuses on {inv.get('sector','?')}")
    istg = [x.strip() for x in (inv.get('stage') or '').split(',')]
    if s.get('stage') not in istg:
        flags.append(f"Stage gap — startup is {s.get('stage','?')}, "
                     f"investor targets {inv.get('stage','?')}")
    sl=(s.get('location','') or '').lower().strip()
    il=(inv.get('location','') or '').lower().strip()
    if sl and il and sl!=il:
        flags.append(f"Geographic gap — {s.get('location','?')} vs {inv.get('location','?')}")
    tick=inv.get('ticket_size',0) or 0
    lo,hi=STAGE_TICKET.get(s.get('stage',''), (0,float('inf')))
    if hi!=float('inf') and tick>0:
        if tick>hi*1.5:
            flags.append(f"Ticket too large — ${tick:,.0f} exceeds typical "
                         f"${lo:,.0f}–${hi:,.0f} for {s.get('stage','')}")
        elif tick<lo*0.5:
            flags.append(f"Ticket too small — ${tick:,.0f} below typical "
                         f"${lo:,.0f}–${hi:,.0f} for {s.get('stage','')}")
    return flags

def gen_next_steps(me, them, my_role):
    if my_role == "Startup":
        inv = them
        kw  = kw_overlap(me.get('description',''), inv.get('thesis',''))
        return [
            f"Research {inv.get('name','their')} portfolio at {inv.get('firm','')} — "
            f"identify past {inv.get('sector','')} bets and their exit outcomes.",
            f"Lead with {' and '.join(kw[:2]) if kw else 'your core differentiator'} "
            f"in your opening — these words appear directly in their thesis.",
            f"Prepare {me.get('stage','')} milestone proof: MRR trajectory, retention, "
            f"and your 18-month roadmap with clear funding deployment plan.",
            f"Keep your cold outreach to 3 paragraphs: hook, traction, ask. "
            f"Reference their {inv.get('sector','')} focus explicitly.",
        ]
    else:
        s   = them
        kw  = kw_overlap(me.get('thesis',''), s.get('description',''))
        rev = s.get('revenue',0) or 0
        return [
            f"Review {s.get('name','this startup')}'s product"
            f"{' at '+s['website'] if s.get('website') else ''} "
            f"before first contact — understand their UX and positioning.",
            f"Prepare diligence questions around "
            f"{'revenue quality and retention' if rev>0 else 'path to first revenue'} "
            f"and {me.get('stage','')} milestone expectations.",
            f"Explore their angle on {' and '.join(kw[:2]) if kw else 'core problem'} "
            f"— these themes align with your stated thesis.",
            f"Send a 2-paragraph note: reference your {me.get('sector','')} thesis "
            f"and your typical {me.get('stage','')} check. Propose a 20-min call.",
        ]

def market_summary(s_df, i_df, my_sector, my_role):
    ns, ni = len(s_df), len(i_df)
    out = [f"The platform has **{ns}** startup{'s' if ns!=1 else ''} and "
           f"**{ni}** investor{'s' if ni!=1 else ''} registered."]
    if ns>0 and 'Sector' in s_df.columns:
        ts = s_df['Sector'].value_counts()
        out.append(f"**{ts.index[0]}** leads among startups with **{ts.iloc[0]}** "
                   f"{'company' if ts.iloc[0]==1 else 'companies'}.")
    if ni>0 and 'Sector' in i_df.columns and my_sector:
        mc = len(i_df[i_df['Sector']==my_sector])
        out.append(f"Your sector (**{my_sector}**) has **{mc}** active investor"
                   f"{'s' if mc!=1 else ''} on platform."
                   if mc>0 else
                   f"No investors focused on **{my_sector}** registered yet — low competition.")
    return " ".join(out)

def chart_insight(df, col, entity_type, uval=None):
    if df.empty or col not in df.columns: return ""
    vc = df[col].value_counts()
    top,tn,tot = vc.index[0],vc.iloc[0],len(df)
    pct = round(tn/tot*100)
    line = f"**{top}** is most common ({tn}/{tot} {entity_type}, {pct}%)"
    if uval and uval!=top:
        line += f". Your segment ({uval}) has {vc.get(uval,0)}."
    elif uval and uval==top:
        line += " — you are in the most competitive segment."
    return line

# ═══════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def sector_color(sec): return SECTOR_COLORS.get(sec, "#94a3b8")

def avatar_html(name, sector, size=44):
    parts    = name.strip().split()
    initials = (parts[0][0] + (parts[1][0] if len(parts)>1 else parts[0][1])).upper()
    c        = sector_color(sector)
    fs       = size//3
    return (f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
            f'background:{c}18;border:1.5px solid {c}45;display:flex;'
            f'align-items:center;justify-content:center;font-weight:800;'
            f'font-size:{fs}px;color:{c};flex-shrink:0;letter-spacing:-.02em">'
            f'{initials}</div>')

def score_html(s, large=False):
    c = "#34d399" if s>=70 else ("#fbbf24" if s>=50 else "#f87171")
    sz= "1.6rem" if large else "1.15rem"
    return (f'<span style="font-size:{sz};font-weight:900;color:{c};'
            f'letter-spacing:-.02em">{s}%</span>')

def score_ring_svg(s, size=80):
    c    = "#34d399" if s>=70 else ("#fbbf24" if s>=50 else "#f87171")
    r    = size*0.42; cx=size//2; sw=size*0.09
    circ = 2*3.14159*r; dash = circ*(s/100)
    fs   = int(size*0.2)
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<circle cx="{cx}" cy="{cx}" r="{r}" fill="none" stroke="#1a1a2e" '
            f'stroke-width="{sw}"/>'
            f'<circle cx="{cx}" cy="{cx}" r="{r}" fill="none" stroke="{c}" '
            f'stroke-width="{sw}" stroke-dasharray="{dash:.1f} {circ:.1f}" '
            f'stroke-linecap="round" transform="rotate(-90 {cx} {cx})"/>'
            f'<text x="{cx}" y="{cx}" text-anchor="middle" '
            f'dominant-baseline="middle" fill="{c}" font-size="{fs}" '
            f'font-weight="900" font-family="Inter,sans-serif">{s}%</text>'
            f'</svg>')

def sec_pill(sec):
    c = sector_color(sec)
    return (f'<span style="background:{c}18;color:{c};border:1px solid {c}35;'
            f'border-radius:5px;padding:2px 9px;font-size:.72rem;font-weight:700;'
            f'letter-spacing:.03em">{sec}</span>')

def stage_pill(stg):
    return (f'<span style="background:#1a1a2e;color:#94a3b8;border:1px solid #2a2a42;'
            f'border-radius:5px;padding:2px 9px;font-size:.72rem;font-weight:600">'
            f'{stg}</span>')

def tag_html(t):
    return (f'<span style="background:rgba(245,158,11,.1);color:#fbbf24;'
            f'border:1px solid rgba(245,158,11,.25);border-radius:5px;'
            f'padding:3px 9px;font-size:.77rem;font-weight:600;'
            f'margin:0 5px 5px 0;display:inline-block">{t}</span>')

def lbl(text):
    return (f'<span style="font-size:.68rem;font-weight:700;color:#475569;'
            f'text-transform:uppercase;letter-spacing:.09em;'
            f'display:block;margin-bottom:6px">{text}</span>')

def fmt_m(v):
    if v >= 1_000_000: return f"${v/1_000_000:.1f}M"
    if v >= 1_000:     return f"${v/1_000:.0f}K"
    return f"${v:,.0f}"

def completeness(e, role):
    if role == "Startup":
        fields = ['name','founder','sector','stage','location','description',
                  'website','linkedin','target_market','business_model','country',
                  'mrr','growth_rate','team_size']
    else:
        fields = ['name','firm','sector','stage','location','thesis',
                  'website','linkedin','geo_focus','co_invest_pref',
                  'decision_timeline','fund_size','portfolio_count','notable_investments']
    filled = sum(1 for f in fields if e.get(f) not in (None,'',0))
    return round(filled/len(fields)*100)

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════
DEFS = dict(authenticated=False, user=None, auth_view="login",
            signup_step=1, signup_data={},
            drilldown_id=None, drilldown_score=None, drilldown_role=None,
            edit_mode=False)
for k,v in DEFS.items():
    if k not in st.session_state: st.session_state[k]=v

def get_me():
    u = st.session_state.user
    return get_startup(u['entity_id']) if u['role']=="Startup" \
           else get_investor(u['entity_id'])

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER  (sign-out button top-right)
# ═══════════════════════════════════════════════════════════════════════════════
def render_header():
    u  = st.session_state.user
    me = get_me()
    nm = (me or {}).get('name', u['username'])
    sc = (me or {}).get('sector','Other')
    c  = sector_color(sc)
    parts = nm.strip().split()
    ini   = (parts[0][0]+(parts[1][0] if len(parts)>1 else parts[0][1] if len(parts[0])>1 else '')).upper()
    role_badge = (
        f'<span style="background:rgba(129,140,248,.15);color:#818cf8;'
        f'border-radius:4px;padding:1px 7px;font-size:.68rem;font-weight:700;'
        f'letter-spacing:.04em">INVESTOR</span>'
        if u['role']=="Investor" else
        f'<span style="background:rgba(52,211,153,.15);color:#34d399;'
        f'border-radius:4px;padding:1px 7px;font-size:.68rem;font-weight:700;'
        f'letter-spacing:.04em">STARTUP</span>'
    )

    h_col, btn_col = st.columns([11, 1])
    with h_col:
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:18px 2px 0;margin-bottom:0">
          <div style="display:flex;align-items:center;gap:10px">
            <div style="width:30px;height:30px;background:linear-gradient(135deg,#b45309,#f59e0b);
                        border-radius:7px;display:flex;align-items:center;justify-content:center">
              <span style="color:#0a0a0f;font-weight:900;font-size:.85rem;
                           font-family:Inter,sans-serif">S</span>
            </div>
            <div style="display:flex;align-items:baseline;gap:1px">
              <span style="font-size:1.1rem;font-weight:900;color:#f8fafc;
                           letter-spacing:-.03em">Start</span>
              <span style="font-size:1.1rem;font-weight:900;color:#f59e0b;
                           letter-spacing:-.03em">Match</span>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:14px">
            {role_badge}
            <div style="display:flex;align-items:center;gap:9px">
              <div style="width:30px;height:30px;border-radius:50%;
                          background:{c}18;border:1.5px solid {c}50;
                          display:flex;align-items:center;justify-content:center;
                          font-weight:800;font-size:.72rem;color:{c}">{ini}</div>
              <div style="line-height:1.25">
                <div style="font-size:.82rem;font-weight:700;color:#f1f5f9">{nm}</div>
                <div style="font-size:.68rem;color:#475569">@{u['username']}</div>
              </div>
            </div>
          </div>
        </div>
        <div style="height:1px;background:#1a1a2e;margin:14px 0 0"></div>
        """, unsafe_allow_html=True)

    with btn_col:
        st.markdown('<div class="signout-btn" style="padding-top:22px">', unsafe_allow_html=True)
        if st.button("Sign out", key="header_signout"):
            st.session_state.update(DEFS); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH — LOGIN
# ═══════════════════════════════════════════════════════════════════════════════
def login_page():
    _,c,_ = st.columns([1,1.2,1])
    with c:
        st.markdown("""
        <div style="text-align:center;padding:40px 0 32px">
          <div style="display:inline-flex;align-items:center;gap:10px;margin-bottom:14px">
            <div style="width:38px;height:38px;background:linear-gradient(135deg,#b45309,#f59e0b);
                        border-radius:10px;display:flex;align-items:center;
                        justify-content:center">
              <span style="color:#0a0a0f;font-weight:900;font-size:1.1rem;
                           font-family:Inter,sans-serif">S</span>
            </div>
            <span style="font-size:1.7rem;font-weight:900;color:#f8fafc;
                         letter-spacing:-.04em">Start<span style="color:#f59e0b">Match</span></span>
          </div>
          <p style="color:#64748b;font-size:.88rem;margin:0">
            AI-powered startup and investor matching
          </p>
        </div>
        """, unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### Sign in to your account")
            st.markdown("<br>", unsafe_allow_html=True)
            u  = st.text_input("Username", placeholder="Enter your username", key="li_u")
            pw = st.text_input("Password", type="password",
                               placeholder="Enter your password", key="li_p")
            st.markdown("<br>", unsafe_allow_html=True)
            b1,b2 = st.columns(2)
            with b1:
                if st.button("Sign In", use_container_width=True):
                    row = get_user(u.strip())
                    if row and row['password']==hash_pw(pw):
                        st.session_state.authenticated=True
                        st.session_state.user=row; st.rerun()
                    else: st.error("Incorrect username or password.")
            with b2:
                if st.button("Create Account", use_container_width=True):
                    st.session_state.auth_view="signup"
                    st.session_state.signup_step=1
                    st.session_state.signup_data={}; st.rerun()
        st.markdown(
            "<p style='text-align:center;color:#334155;font-size:.74rem;"
            "margin-top:16px'>By continuing you agree to StartMatch Terms of Service</p>",
            unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH — MULTI-STEP SIGNUP
# ═══════════════════════════════════════════════════════════════════════════════
def signup_page():
    step = st.session_state.signup_step
    sd   = st.session_state.signup_data

    _,c,_ = st.columns([1,2.4,1])
    with c:
        st.markdown("""
        <div style="text-align:center;padding:28px 0 20px">
          <span style="font-size:1.4rem;font-weight:900;color:#f8fafc;
                       letter-spacing:-.03em">Start<span style="color:#f59e0b">Match</span></span>
        </div>""", unsafe_allow_html=True)

        steps = ["Identity","About","Financials & Access"]
        prog_html = '<div style="display:flex;align-items:center;margin-bottom:24px">'
        for i,s in enumerate(steps,1):
            active = i==step
            done   = i<step
            clr = "#f59e0b" if active else ("#34d399" if done else "#1a1a2e")
            tc  = "#0a0a0f" if (active or done) else "#475569"
            prog_html += (
                f'<div style="display:flex;align-items:center;gap:8px;flex:1">'
                f'<div style="width:26px;height:26px;border-radius:50%;'
                f'background:{clr};display:flex;align-items:center;'
                f'justify-content:center;font-weight:800;font-size:.75rem;'
                f'color:{tc};flex-shrink:0">{"✓" if done else i}</div>'
                f'<span style="font-size:.78rem;font-weight:{"700" if active else "500"};'
                f'color:{"#f1f5f9" if active else "#475569"}">{s}</span>'
                f'{"<div style=\'flex:1;height:1px;background:#1a1a2e;margin:0 6px\'></div>" if i<3 else ""}'
                f'</div>')
        prog_html += '</div>'
        st.markdown(prog_html, unsafe_allow_html=True)

        if step == 1:
            with st.container(border=True):
                st.markdown("### Step 1 — Identity")
                st.markdown("<br>", unsafe_allow_html=True)
                role = st.radio("I am a", ["Startup","Investor"],
                                horizontal=True, key="su_role",
                                index=0 if sd.get('role','Startup')=="Startup" else 1)
                st.markdown("---")
                if role == "Startup":
                    r1,r2 = st.columns(2)
                    name    = r1.text_input("Company Name", placeholder="e.g. NeuralCart", key="su_n")
                    founder = r2.text_input("Founder Name", placeholder="e.g. Priya Sharma", key="su_f")
                    r3,r4   = st.columns(2)
                    sector  = r3.selectbox("Sector", SECTORS, key="su_sec")
                    stage   = r4.selectbox("Funding Stage", STAGES, key="su_stg")
                    r5,r6   = st.columns(2)
                    location= r5.text_input("City", placeholder="San Francisco", key="su_loc")
                    country = r6.text_input("Country of Incorporation", placeholder="United States", key="su_cty")
                else:
                    r1,r2 = st.columns(2)
                    name = r1.text_input("Full Name", placeholder="e.g. Sarah Chen", key="su_n")
                    firm = r2.text_input("Firm / Fund", placeholder="e.g. Sequoia Capital", key="su_firm")
                    r3,r4 = st.columns(2)
                    sector   = r3.selectbox("Primary Sector Focus", SECTORS, key="su_sec")
                    location = r4.text_input("City", placeholder="Menlo Park", key="su_loc")
                    stage_sel= st.multiselect("Preferred Investment Stages",
                                              STAGES, default=["Seed"], key="su_stg")
                    country = ""

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Continue →", use_container_width=True, key="su_next1"):
                    errs = []
                    if not name.strip(): errs.append("Name is required.")
                    if role=="Startup" and not founder.strip(): errs.append("Founder is required.")
                    if role=="Investor" and not firm.strip(): errs.append("Firm is required.")
                    if not location.strip(): errs.append("City is required.")
                    if role=="Investor" and not stage_sel: errs.append("Select at least one stage.")
                    if errs:
                        for e in errs: st.error(e)
                    else:
                        st.session_state.signup_data.update(dict(
                            role=role, name=name.strip(),
                            founder=founder.strip() if role=="Startup" else "",
                            firm=firm.strip() if role=="Investor" else "",
                            sector=sector,
                            stage=stage if role=="Startup" else ", ".join(stage_sel),
                            location=location.strip(), country=country.strip(),
                        ))
                        st.session_state.signup_step=2; st.rerun()

        elif step == 2:
            role = sd.get('role','Startup')
            with st.container(border=True):
                st.markdown("### Step 2 — About")
                st.markdown("<br>", unsafe_allow_html=True)
                if role == "Startup":
                    r1,r2 = st.columns(2)
                    biz_model    = r1.selectbox("Business Model", BIZ_MODELS, key="su_bm")
                    target_market= r2.text_input("Target Market",
                                                 placeholder="e.g. Mid-market e-commerce brands", key="su_tm")
                    website = st.text_input("Website URL", placeholder="https://...", key="su_web")
                    linkedin= st.text_input("LinkedIn URL", placeholder="https://linkedin.com/company/...", key="su_li")
                    st.markdown('<span style="font-size:.8rem;font-weight:600;color:#94a3b8;'
                                'text-transform:uppercase;letter-spacing:.07em">'
                                'Pitch / Description</span>', unsafe_allow_html=True)
                    desc = st.text_area("", placeholder="Describe your product, the problem you solve, "
                                        "your technology, target market and current traction. "
                                        "More detail = better AI match scores.",
                                        height=120, key="su_desc", label_visibility="collapsed")
                    st.caption(f"{len(desc)} / 1000 chars recommended")
                else:
                    r1,r2 = st.columns(2)
                    bm_pref = r1.selectbox("Preferred Business Model", ["Any"]+BIZ_MODELS, key="su_bm")
                    geo = r2.multiselect("Geographic Focus", GEO_REGIONS,
                                         default=["North America"], key="su_geo")
                    website = st.text_input("Fund Website", placeholder="https://...", key="su_web")
                    linkedin= st.text_input("LinkedIn URL", placeholder="https://linkedin.com/in/...", key="su_li")
                    st.markdown('<span style="font-size:.8rem;font-weight:600;color:#94a3b8;'
                                'text-transform:uppercase;letter-spacing:.07em">'
                                'Investment Thesis</span>', unsafe_allow_html=True)
                    thesis = st.text_area("", placeholder="Describe the types of companies you invest in, "
                                          "your key beliefs, focus areas and what excites you. "
                                          "This is the primary input for AI matching.",
                                          height=120, key="su_thesis", label_visibility="collapsed")
                    st.caption(f"{len(thesis)} / 1000 chars recommended")
                    target_market = ""; desc = ""; biz_model = ""

                st.markdown("<br>", unsafe_allow_html=True)
                bc1,bc2 = st.columns(2)
                with bc1:
                    if st.button("← Back", use_container_width=True, key="su_back2"):
                        st.session_state.signup_step=1; st.rerun()
                with bc2:
                    if st.button("Continue →", use_container_width=True, key="su_next2"):
                        errs = []
                        if role=="Startup" and not desc.strip(): errs.append("Description is required.")
                        if role=="Investor" and not thesis.strip(): errs.append("Thesis is required.")
                        if errs:
                            for e in errs: st.error(e)
                        else:
                            updates = dict(website=website.strip(), linkedin=linkedin.strip())
                            if role=="Startup":
                                updates.update(description=desc.strip(),
                                               business_model=biz_model,
                                               target_market=target_market.strip())
                            else:
                                updates.update(thesis=thesis.strip(),
                                               business_model_pref=bm_pref,
                                               geo_focus=", ".join(geo))
                            st.session_state.signup_data.update(updates)
                            st.session_state.signup_step=3; st.rerun()

        elif step == 3:
            role = sd.get('role','Startup')
            with st.container(border=True):
                st.markdown("### Step 3 — Financials & Access")
                st.markdown("<br>", unsafe_allow_html=True)
                if role == "Startup":
                    r1,r2,r3 = st.columns(3)
                    revenue   = r1.number_input("Annual Revenue ($)", min_value=0,
                                                value=0, step=10000, key="su_rev")
                    mrr       = r2.number_input("MRR ($)", min_value=0,
                                                value=0, step=1000, key="su_mrr")
                    team_size = r3.number_input("Team Size", min_value=1,
                                                value=1, step=1, key="su_ts")
                    r4,r5,r6 = st.columns(3)
                    growth_rate= r4.number_input("MoM Growth (%)", min_value=0.0,
                                                  value=0.0, step=0.5, key="su_gr")
                    runway     = r5.number_input("Runway (months)", min_value=0,
                                                  value=12, step=1, key="su_rw")
                    burn_rate  = r6.number_input("Monthly Burn ($)", min_value=0,
                                                  value=0, step=5000, key="su_br")
                else:
                    r1,r2,r3 = st.columns(3)
                    fund_size      = r1.number_input("Fund Size ($)", min_value=0,
                                                     value=100_000_000, step=10_000_000, key="su_fs")
                    ticket_size    = r2.number_input("Typical Ticket ($)", min_value=0,
                                                     value=500_000, step=50_000, key="su_tick")
                    portfolio_count= r3.number_input("Portfolio Companies", min_value=0,
                                                     value=0, step=1, key="su_pc")
                    r4,r5 = st.columns(2)
                    investments_per_year= r4.number_input("Deals / Year", min_value=0,
                                                           value=5, step=1, key="su_ipy")
                    co_inv  = r5.selectbox("Co-invest Preference", CO_INVEST, key="su_ci")
                    dtl     = st.selectbox("Decision Timeline", DECISION_TL, key="su_dtl")
                    notable = st.text_input("Notable Past Investments",
                                            placeholder="e.g. Stripe, Figma, Scale AI", key="su_ni")

                st.markdown("---")
                st.markdown('<span style="font-size:.8rem;font-weight:600;color:#94a3b8;'
                            'text-transform:uppercase;letter-spacing:.07em">Account Credentials</span>',
                            unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                cr1,cr2,cr3 = st.columns(3)
                uname = cr1.text_input("Username", placeholder="Choose a username", key="su_u")
                pw1   = cr2.text_input("Password", type="password",
                                       placeholder="Min. 6 characters", key="su_p1")
                pw2   = cr3.text_input("Confirm Password", type="password", key="su_p2")

                st.markdown("<br>", unsafe_allow_html=True)
                bc1,bc2 = st.columns(2)
                with bc1:
                    if st.button("← Back", use_container_width=True, key="su_back3"):
                        st.session_state.signup_step=2; st.rerun()
                with bc2:
                    if st.button("Create Account", use_container_width=True, key="su_finish"):
                        errs = []
                        if not uname.strip(): errs.append("Username is required.")
                        if len(pw1)<6: errs.append("Password must be 6+ characters.")
                        if pw1!=pw2:   errs.append("Passwords do not match.")
                        if get_user(uname.strip()): errs.append("Username already taken.")
                        if errs:
                            for e in errs: st.error(e)
                        else:
                            d = st.session_state.signup_data
                            if role == "Startup":
                                ins_startup(dict(
                                    name=d['name'],founder=d['founder'],
                                    sector=d['sector'],stage=d['stage'],
                                    location=d['location'],country=d.get('country',''),
                                    description=d.get('description',''),
                                    website=d.get('website',''),linkedin=d.get('linkedin',''),
                                    business_model=d.get('business_model',''),
                                    target_market=d.get('target_market',''),
                                    revenue=revenue,mrr=mrr,team_size=team_size,
                                    growth_rate=growth_rate,runway=runway,burn_rate=burn_rate,
                                ), uname.strip(), pw1)
                            else:
                                ins_investor(dict(
                                    name=d['name'],firm=d['firm'],
                                    sector=d['sector'],stage=d['stage'],
                                    location=d['location'],
                                    thesis=d.get('thesis',''),
                                    website=d.get('website',''),linkedin=d.get('linkedin',''),
                                    business_model_pref=d.get('business_model_pref',''),
                                    geo_focus=d.get('geo_focus',''),
                                    fund_size=fund_size,ticket_size=ticket_size,
                                    portfolio_count=portfolio_count,
                                    investments_per_year=investments_per_year,
                                    co_invest_pref=co_inv,decision_timeline=dtl,
                                    notable_investments=notable.strip(),
                                ), uname.strip(), pw1)
                            st.success("Account created. Sign in below.")
                            st.session_state.auth_view="login"
                            st.session_state.signup_step=1
                            st.session_state.signup_data={}; st.rerun()

        if st.button("← Back to Sign In", key="su_signin_link"):
            st.session_state.auth_view="login"
            st.session_state.signup_step=1
            st.session_state.signup_data={}; st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def dashboard_tab():
    u  = st.session_state.user
    me = get_me()
    if not me: st.error("Profile not found."); return

    nm  = me.get('name','')
    sc  = me.get('sector','Other')
    clr = sector_color(sc)

    with st.container(border=True):
        gc1,gc2 = st.columns([4,1])
        with gc1:
            st.markdown(f"## Welcome back, {nm}")
            st.markdown(
                f"{sec_pill(sc)} {stage_pill(me.get('stage',''))} "
                f'<span style="color:#475569;font-size:.82rem;margin-left:6px">'
                f'📍 {me.get("location","—")}</span>',
                unsafe_allow_html=True)
        with gc2:
            comp = completeness(me, u['role'])
            st.markdown(score_ring_svg(comp,68), unsafe_allow_html=True)
            st.caption("Profile complete")

    st.markdown("<br>", unsafe_allow_html=True)

    all_s  = all_startups()
    all_i  = all_investors()
    matches= compute_matches(u)
    best   = matches[0][1] if matches else 0.0
    corp   = registered_opposite(u['role'])

    mc1,mc2,mc3,mc4 = st.columns(4)
    mc1.metric("Registered Startups",  len(all_s))
    mc2.metric("Registered Investors", len(all_i))
    mc3.metric("Best Match Score",     f"{best}%")
    mc4.metric("Potential Matches",    len(corp))

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([3,2], gap="large")

    with left:
        target = "Investors" if u['role']=="Startup" else "Startups"
        st.markdown(f"#### Top Matches — {target}")
        st.caption("Real-time AI ranking. Click View to open full profile.")
        st.markdown("<br>", unsafe_allow_html=True)

        if not matches:
            with st.container(border=True):
                st.markdown(
                    f"<div style='text-align:center;padding:32px 0'>"
                    f"<div style='font-size:1.8rem;margin-bottom:10px;opacity:.4'>◎</div>"
                    f"<div style='font-weight:700;color:#f1f5f9;margin-bottom:6px'>"
                    f"No {target} yet</div>"
                    f"<div style='color:#475569;font-size:.83rem'>"
                    f"Invite {target.lower()} to join StartMatch</div></div>",
                    unsafe_allow_html=True)
        else:
            for rank,(m,score) in enumerate(matches[:3],1):
                mc,sc2 = m.get('sector','Other'), sector_color(m.get('sector','Other'))
                with st.container(border=True):
                    r1,r2 = st.columns([5,1])
                    with r1:
                        st.markdown(
                            f'<div style="display:flex;align-items:center;gap:10px">'
                            f'{avatar_html(m.get("name","?"), m.get("sector","Other"), 38)}'
                            f'<div><div style="font-weight:700;color:#f1f5f9;font-size:.95rem">'
                            f'{m.get("name","—")}</div>'
                            f'<div style="font-size:.78rem;color:#475569">'
                            f'{m.get("firm","") or m.get("founder","") or ""}'
                            f'</div></div></div>',
                            unsafe_allow_html=True)
                        st.markdown(
                            f'<div style="margin-top:6px">{sec_pill(m.get("sector","—"))} '
                            f'{stage_pill(m.get("stage","—"))}</div>',
                            unsafe_allow_html=True)
                    with r2:
                        st.markdown(
                            f'<div style="text-align:right;padding-top:4px">'
                            f'{score_html(score, large=True)}</div>',
                            unsafe_allow_html=True)
                    st.progress(max(0.0, min(score/100, 1.0)))
                    if st.button("View Profile", key=f"dash_v_{m['id']}_{rank}",
                                 use_container_width=True):
                        st.session_state.drilldown_id    = m['id']
                        st.session_state.drilldown_score = score
                        st.session_state.drilldown_role  = ("Investor" if u['role']=="Startup"
                                                             else "Startup")
                        st.rerun()

    with right:
        st.markdown("#### Market Pulse")
        st.caption("Platform-wide sector distribution.")
        BG = "#13131f"
        PIE_C = ["#f59e0b","#818cf8","#2dd4bf","#34d399","#f87171",
                 "#c084fc","#38bdf8","#a3e635","#fb923c","#fbbf24"]
        s_df = pd.DataFrame(all_s).rename(columns={'sector':'Sector'}) if all_s else pd.DataFrame()
        i_df = pd.DataFrame(all_i).rename(columns={'sector':'Sector'}) if all_i else pd.DataFrame()
        if not s_df.empty and 'Sector' in s_df.columns:
            d = s_df['Sector'].value_counts().reset_index()
            d.columns = ['Sector','Count']
            fig = go.Figure(go.Pie(
                labels=d['Sector'], values=d['Count'], hole=.55,
                marker=dict(colors=PIE_C[:len(d)], line=dict(color='#0d0d14',width=2)),
                textfont=dict(size=10, color='#f1f5f9'),
                showlegend=True,
            ))
            fig.update_layout(
                paper_bgcolor=BG, plot_bgcolor=BG, font_color='#94a3b8',
                margin=dict(t=8,b=8,l=8,r=8), height=200,
                legend=dict(font=dict(size=9,color='#94a3b8'),
                            bgcolor='rgba(0,0,0,0)', orientation='v',
                            x=1.02, y=0.5),
                annotations=[dict(text="Sectors", x=0.5, y=0.5,
                                  font_size=11, showarrow=False,
                                  font_color='#64748b')]
            )
            st.plotly_chart(fig, use_container_width=True)

        if not i_df.empty and 'Sector' in i_df.columns:
            d2 = i_df['Sector'].value_counts().reset_index()
            d2.columns = ['Sector','Investors']
            fig2 = go.Figure(go.Bar(
                x=d2['Investors'], y=d2['Sector'], orientation='h',
                marker=dict(color=d2['Investors'],
                            colorscale=[[0,"#1a1a2e"],[1,"#f59e0b"]],
                            showscale=False),
                text=d2['Investors'], textposition='outside',
                textfont=dict(size=9, color='#64748b'),
            ))
            fig2.update_layout(
                title=dict(text="Investors by Sector",
                           font=dict(size=11,color='#94a3b8'), x=0),
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(tickfont=dict(size=9,color='#94a3b8'), autorange='reversed'),
                plot_bgcolor=BG, paper_bgcolor=BG,
                margin=dict(t=28,b=4,l=4,r=30), height=180,
                showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PROFILE TAB
# ═══════════════════════════════════════════════════════════════════════════════
def profile_tab():
    u  = st.session_state.user
    e  = get_me()
    if not e: st.error("Profile not found."); return
    sc = e.get('sector','Other'); clr = sector_color(sc)

    st.markdown(
        f'<div style="background:linear-gradient(135deg,{clr}0d 0%,#13131f 60%),'
        f'#13131f;border:1px solid {clr}22;border-radius:14px;'
        f'padding:28px 32px;margin-bottom:20px">'
        f'<div style="display:flex;align-items:center;gap:20px">'
        f'{avatar_html(e["name"], sc, 72)}'
        f'<div style="flex:1">'
        f'<h1 style="margin:0 0 6px;font-size:1.8rem;line-height:1.1">{e["name"]}</h1>'
        f'<div style="color:#94a3b8;font-size:.88rem;margin-bottom:10px">'
        f'{"Founded by "+e["founder"] if u["role"]=="Startup" and e.get("founder") else e.get("firm","")}'
        f'</div>'
        f'<div style="display:flex;gap:7px;flex-wrap:wrap">'
        f'{sec_pill(sc)}{stage_pill(e.get("stage",""))}'
        f'<span style="background:#1a1a2e;color:#64748b;border:1px solid #2a2a42;'
        f'border-radius:5px;padding:2px 9px;font-size:.72rem">📍 {e.get("location","—")}</span>'
        f'{"<span style=\\'background:#1a1a2e;color:#64748b;border:1px solid #2a2a42;border-radius:5px;padding:2px 9px;font-size:.72rem\\'>"+e["business_model"]+"</span>" if e.get("business_model") else ""}'
        f'</div></div>'
        f'</div></div>',
        unsafe_allow_html=True)

    ec = st.columns([6,1])[1]
    with ec:
        if st.button("Edit Profile", use_container_width=True):
            st.session_state.edit_mode=True; st.rerun()

    col_l, col_r = st.columns([3,2], gap="large")

    if u['role'] == "Startup":
        with col_l:
            with st.container(border=True):
                st.markdown(lbl("Pitch & Description"), unsafe_allow_html=True)
                st.markdown(
                    f'<p style="color:#cbd5e1;line-height:1.7;font-size:.92rem">'
                    f'{e.get("description","—")}</p>', unsafe_allow_html=True)
            if e.get('target_market'):
                with st.container(border=True):
                    st.markdown(lbl("Target Market"), unsafe_allow_html=True)
                    st.markdown(
                        f'<p style="color:#cbd5e1;font-size:.9rem">'
                        f'{e["target_market"]}</p>', unsafe_allow_html=True)
            links = []
            if e.get('website'): links.append(f'[Website]({e["website"]})')
            if e.get('linkedin'): links.append(f'[LinkedIn]({e["linkedin"]})')
            if links: st.markdown("  ·  ".join(links))

        with col_r:
            with st.container(border=True):
                st.markdown(lbl("Key Metrics"), unsafe_allow_html=True)
                rev = e.get('revenue',0) or 0
                mrr = e.get('mrr',0) or 0
                gr  = e.get('growth_rate',0) or 0
                rw  = e.get('runway',0) or 0
                br  = e.get('burn_rate',0) or 0
                ts  = e.get('team_size',0) or 0
                metrics = [
                    ("Annual Revenue", fmt_m(rev) if rev>0 else "Pre-revenue"),
                    ("MRR",            fmt_m(mrr)  if mrr>0 else "—"),
                    ("MoM Growth",     f"{gr:.1f}%" if gr>0 else "—"),
                    ("Runway",         f"{rw}mo" if rw>0 else "—"),
                    ("Monthly Burn",   fmt_m(br)  if br>0 else "—"),
                    ("Team Size",      f"{ts} people" if ts>0 else "—"),
                    ("Country",        e.get('country','—') or '—'),
                ]
                for mk,mv in metrics:
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;'
                        f'align-items:center;padding:8px 0;border-bottom:1px solid #1a1a2e">'
                        f'<span style="font-size:.8rem;color:#64748b;font-weight:600;'
                        f'text-transform:uppercase;letter-spacing:.06em">{mk}</span>'
                        f'<span style="font-size:.9rem;font-weight:700;color:#f1f5f9">'
                        f'{mv}</span></div>', unsafe_allow_html=True)

    else:
        with col_l:
            with st.container(border=True):
                st.markdown(lbl("Investment Thesis"), unsafe_allow_html=True)
                st.markdown(
                    f'<p style="color:#cbd5e1;line-height:1.7;font-size:.92rem">'
                    f'{e.get("thesis","—")}</p>', unsafe_allow_html=True)
            if e.get('notable_investments'):
                with st.container(border=True):
                    st.markdown(lbl("Notable Investments"), unsafe_allow_html=True)
                    for inv_name in e['notable_investments'].split(','):
                        n = inv_name.strip()
                        if n:
                            st.markdown(
                                f'<span style="background:#1a1a2e;color:#94a3b8;'
                                f'border:1px solid #2a2a42;border-radius:5px;'
                                f'padding:3px 10px;font-size:.82rem;margin:0 5px 5px 0;'
                                f'display:inline-block">{n}</span>',
                                unsafe_allow_html=True)
            links = []
            if e.get('website'): links.append(f'[Website]({e["website"]})')
            if e.get('linkedin'): links.append(f'[LinkedIn]({e["linkedin"]})')
            if links: st.markdown("  ·  ".join(links))

        with col_r:
            with st.container(border=True):
                st.markdown(lbl("Fund Profile"), unsafe_allow_html=True)
                fs  = e.get('fund_size',0) or 0
                ts2 = e.get('ticket_size',0) or 0
                pc  = e.get('portfolio_count',0) or 0
                ipy = e.get('investments_per_year',0) or 0
                metrics = [
                    ("Fund Size",      fmt_m(fs)  if fs>0 else "—"),
                    ("Ticket Size",    fmt_m(ts2) if ts2>0 else "—"),
                    ("Portfolio Cos.", str(pc) if pc>0 else "—"),
                    ("Deals / Year",   str(ipy) if ipy>0 else "—"),
                    ("Co-invest",      e.get('co_invest_pref','—') or '—'),
                    ("Decision Time",  e.get('decision_timeline','—') or '—'),
                    ("Geo Focus",      (e.get('geo_focus','—') or '—')[:28]),
                ]
                for mk,mv in metrics:
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;'
                        f'align-items:center;padding:8px 0;border-bottom:1px solid #1a1a2e">'
                        f'<span style="font-size:.8rem;color:#64748b;font-weight:600;'
                        f'text-transform:uppercase;letter-spacing:.06em">{mk}</span>'
                        f'<span style="font-size:.9rem;font-weight:700;color:#f1f5f9">'
                        f'{mv}</span></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MATCHES TAB  — with filter bar
# ═══════════════════════════════════════════════════════════════════════════════
def matches_tab():
    u      = st.session_state.user
    target = "Investors" if u['role'] == "Startup" else "Startups"

    st.markdown(f"## Top 5 Matches — {target}")
    st.caption("Ranked by AI semantic similarity. Use filters to narrow the field.")

    # ── Filter bar ────────────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(
            '<span style="font-size:.68rem;font-weight:700;color:#f59e0b;'
            'text-transform:uppercase;letter-spacing:.09em">Filter Matches</span>',
            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        fc1, fc2, fc3, fc4, fc5 = st.columns([2, 2, 2, 2, 1])

        f_sector   = fc1.selectbox("Sector",         ["All"] + SECTORS,  key="mf_sector")
        f_stage    = fc2.selectbox("Stage",           ["All"] + STAGES,   key="mf_stage")
        f_biz_model= fc3.selectbox("Business Model",  ["All"] + BIZ_MODELS, key="mf_bm")
        f_location = fc4.text_input("Location (city)", placeholder="e.g. London", key="mf_loc")

        with fc5:
            st.markdown("<br>", unsafe_allow_html=True)
            reset = st.button("Reset", use_container_width=True, key="mf_reset")
            if reset:
                for k in ("mf_sector","mf_stage","mf_bm","mf_loc"):
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

    # Determine whether any filter is active
    filters_active = (
        f_sector    != "All" or
        f_stage     != "All" or
        f_biz_model != "All" or
        bool(f_location.strip())
    )

    st.markdown("---")

    # ── Compute matches ───────────────────────────────────────────────────────
    with st.spinner("Computing matches…"):
        if filters_active:
            matches, total_before, total_after = compute_filtered_matches(
                u,
                f_sector    = f_sector    if f_sector    != "All" else None,
                f_stage     = f_stage     if f_stage     != "All" else None,
                f_location  = f_location.strip() or None,
                f_biz_model = f_biz_model if f_biz_model != "All" else None,
            )
        else:
            raw = compute_matches(u)
            matches      = raw
            total_before = len(registered_opposite(u['role']))
            total_after  = total_before

    # ── Results header ────────────────────────────────────────────────────────
    if filters_active:
        active_labels = []
        if f_sector    != "All":       active_labels.append(f"Sector: **{f_sector}**")
        if f_stage     != "All":       active_labels.append(f"Stage: **{f_stage}**")
        if f_biz_model != "All":       active_labels.append(f"Model: **{f_biz_model}**")
        if f_location.strip():         active_labels.append(f"Location: **{f_location.strip()}**")
        st.markdown(
            f'<div style="background:rgba(245,158,11,.07);border:1px solid '
            f'rgba(245,158,11,.2);border-radius:8px;padding:10px 16px;margin-bottom:16px">'
            f'<span style="font-size:.82rem;color:#fbbf24">Filters active — </span>'
            f'<span style="font-size:.82rem;color:#94a3b8">'
            f'{"  ·  ".join(active_labels)}</span>'
            f'<span style="font-size:.82rem;color:#475569;margin-left:12px">'
            f'{total_after} of {total_before} {target.lower()} match your criteria</span>'
            f'</div>',
            unsafe_allow_html=True)

    # ── Empty states ──────────────────────────────────────────────────────────
    if total_before == 0:
        # Nobody on the platform at all
        with st.container(border=True):
            st.markdown(
                f"<div style='text-align:center;padding:56px 0'>"
                f"<div style='font-size:2.4rem;opacity:.25;margin-bottom:12px'>◎</div>"
                f"<div style='font-size:1.1rem;font-weight:700;color:#f1f5f9;margin-bottom:8px'>"
                f"No {target} on the platform yet</div>"
                f"<div style='color:#475569;font-size:.88rem;max-width:360px;margin:0 auto'>"
                f"Share StartMatch with {target.lower()} to unlock AI-powered matching."
                f"</div></div>",
                unsafe_allow_html=True)
        return

    if filters_active and total_after == 0:
        # Filters too narrow
        active_filters_str = ", ".join([
            v for v in [
                f_sector    if f_sector    != "All" else "",
                f_stage     if f_stage     != "All" else "",
                f_biz_model if f_biz_model != "All" else "",
                f_location.strip(),
            ] if v
        ])
        with st.container(border=True):
            st.markdown(
                f"<div style='text-align:center;padding:48px 20px'>"
                f"<div style='font-size:2rem;opacity:.3;margin-bottom:12px'>🔍</div>"
                f"<div style='font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:8px'>"
                f"No {target.lower()} match these filters</div>"
                f"<div style='color:#64748b;font-size:.85rem;max-width:400px;margin:0 auto;line-height:1.6'>"
                f"Your current filter combination <span style='color:#fbbf24'>"
                f"({active_filters_str})</span> returned no results from "
                f"the {total_before} registered {target.lower()}.<br><br>"
                f"Try broadening one or more filters, or click <strong>Reset</strong> "
                f"to see all matches.</div></div>",
                unsafe_allow_html=True)
        return

    if not matches:
        with st.container(border=True):
            st.markdown(
                f"<div style='text-align:center;padding:56px 0'>"
                f"<div style='font-size:2.4rem;opacity:.25;margin-bottom:12px'>◎</div>"
                f"<div style='font-size:1.1rem;font-weight:700;color:#f1f5f9;margin-bottom:8px'>"
                f"No matches found</div>"
                f"<div style='color:#475569;font-size:.88rem;max-width:360px;margin:0 auto'>"
                f"Try adjusting or resetting your filters."
                f"</div></div>",
                unsafe_allow_html=True)
        return

    # ── Match cards ───────────────────────────────────────────────────────────
    if not filters_active:
        st.caption("Showing unfiltered top 5 — use the filters above to narrow results.")

    m_role = "Investor" if u['role'] == "Startup" else "Startup"
    for rank,(m,score) in enumerate(matches, 1):
        sc_col  = sector_color(m.get('sector','Other'))
        excerpt = (m.get('thesis') or m.get('description') or '')[:160]

        with st.container(border=True):
            top_l, top_r = st.columns([6,1])
            with top_l:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:12px">'
                    f'<div style="color:#334155;font-size:.75rem;font-weight:700;'
                    f'min-width:22px">#{rank}</div>'
                    f'{avatar_html(m.get("name","?"), m.get("sector","Other"), 46)}'
                    f'<div>'
                    f'<div style="font-size:1.02rem;font-weight:700;color:#f8fafc">'
                    f'{m.get("name","—")}</div>'
                    f'<div style="font-size:.8rem;color:#475569;margin-top:1px">'
                    f'{m.get("firm","") or m.get("founder","") or ""}'
                    f'</div></div></div>',
                    unsafe_allow_html=True)
                st.markdown(
                    f'<div style="margin-top:8px;display:flex;align-items:center;gap:6px">'
                    f'{sec_pill(m.get("sector","—"))} {stage_pill(m.get("stage","—"))}'
                    f'<span style="color:#334155;font-size:.77rem">'
                    f'📍 {m.get("location","—")}</span></div>',
                    unsafe_allow_html=True)
            with top_r:
                st.markdown(
                    f'<div style="text-align:right;padding-top:6px">'
                    f'{score_ring_svg(score, 58)}</div>',
                    unsafe_allow_html=True)

            st.progress(max(0.0, min(score/100, 1.0)))

            bot_l, bot_r = st.columns([5,1])
            with bot_l:
                if excerpt:
                    st.markdown(
                        f'<p style="color:#475569;font-size:.82rem;'
                        f'line-height:1.55;margin:4px 0 0">{excerpt}…</p>',
                        unsafe_allow_html=True)
            with bot_r:
                if st.button("View", key=f"mv_{m['id']}_{rank}",
                             use_container_width=True):
                    st.session_state.drilldown_id    = m['id']
                    st.session_state.drilldown_score = score
                    st.session_state.drilldown_role  = m_role
                    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# DRILLDOWN PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def drilldown_page():
    u     = st.session_state.user
    role  = st.session_state.drilldown_role
    score = st.session_state.drilldown_score or 0
    eid   = st.session_state.drilldown_id
    m     = get_startup(eid) if role=="Startup" else get_investor(eid)
    me    = get_me()

    if not m:
        st.error("Profile not found.")
        if st.button("Back"): st.session_state.drilldown_id=None; st.rerun()
        return

    render_header()
    if st.button("← Back to Matches"):
        st.session_state.drilldown_id=None; st.rerun()

    s_e  = me if u['role']=="Startup" else m
    inv_e= m  if u['role']=="Startup" else me
    sc   = m.get('sector','Other'); clr = sector_color(sc)

    st.markdown("<br>", unsafe_allow_html=True)

    score_label = "Strong Fit" if score>=70 else ("Moderate Fit" if score>=50 else "Weak Fit")
    score_clr   = "#34d399" if score>=70 else ("#fbbf24" if score>=50 else "#f87171")
    st.markdown(
        f'<div style="background:linear-gradient(135deg,{clr}0d 0%,#13131f 60%),'
        f'#13131f;border:1px solid {clr}22;border-radius:14px;padding:24px 28px;'
        f'margin-bottom:20px;display:flex;align-items:center;gap:20px">'
        f'{score_ring_svg(score, 80)}'
        f'<div style="flex:1">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">'
        f'{avatar_html(m["name"], sc, 52)}'
        f'<div>'
        f'<h2 style="margin:0 0 2px">{m.get("name","—")}</h2>'
        f'<div style="color:#475569;font-size:.85rem">'
        f'{m.get("firm","") or m.get("founder","") or ""}</div>'
        f'</div></div>'
        f'<div style="display:flex;gap:7px;flex-wrap:wrap;margin-top:8px">'
        f'{sec_pill(sc)}{stage_pill(m.get("stage",""))}'
        f'<span style="background:{score_clr}18;color:{score_clr};'
        f'border:1px solid {score_clr}35;border-radius:5px;padding:2px 9px;'
        f'font-size:.72rem;font-weight:700">{score_label}</span>'
        f'</div></div></div>',
        unsafe_allow_html=True)

    sec_match = (s_e or {}).get('sector') == (inv_e or {}).get('sector')
    istg = [x.strip() for x in ((inv_e or {}).get('stage') or '').split(',')]
    stg_match = (s_e or {}).get('stage') in istg
    loc_match = ((s_e or {}).get('location','') or '').lower().strip() == \
                ((inv_e or {}).get('location','') or '').lower().strip()
    tick = (inv_e or {}).get('ticket_size',0) or 0
    lo,hi= STAGE_TICKET.get((s_e or {}).get('stage',''), (0, float('inf')))
    if hi==float('inf'): hi=max(tick*2,1)
    in_range = lo<=tick<=hi

    q1,q2,q3,q4 = st.columns(4)
    q1.metric("Sector Match",   "Yes ✓" if sec_match else "No ✗",
              delta="Aligned"  if sec_match else "Mismatch",
              delta_color="normal" if sec_match else "inverse")
    q2.metric("Stage Fit",      "Yes ✓" if stg_match else "No ✗",
              delta="Aligned"  if stg_match else "Mismatch",
              delta_color="normal" if stg_match else "inverse")
    q3.metric("Same Region",    "Yes ✓" if loc_match else "No ✗",
              delta="Local"    if loc_match else "Remote",
              delta_color="normal" if loc_match else "off")
    q4.metric("Ticket Range",   "Yes ✓" if in_range else "No ✗",
              delta="In range" if in_range else "Out of range",
              delta_color="normal" if in_range else "inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(lbl("AI Match Summary"), unsafe_allow_html=True)
        st.markdown(
            f'<p style="color:#cbd5e1;line-height:1.75;font-size:.92rem;margin:0">'
            f'{gen_summary(me or {}, m, u["role"], score)}</p>',
            unsafe_allow_html=True)

    BG = "#13131f"; GRID = "#1a1a2e"; TC = "#475569"
    cc1,cc2 = st.columns(2)

    with cc1:
        st.markdown("#### Compatibility Breakdown")
        rd   = radar_scores(s_e or {}, inv_e or {}, score)
        cats = list(rd.keys()); vals = list(rd.values())
        fig  = go.Figure(go.Scatterpolar(
            r=vals+[vals[0]], theta=cats+[cats[0]], fill='toself',
            fillcolor='rgba(245,158,11,.1)',
            line=dict(color='#f59e0b', width=2),
            marker=dict(color='#fbbf24', size=6),
        ))
        fig.update_layout(
            polar=dict(
                bgcolor=BG,
                radialaxis=dict(visible=True, range=[0,100], gridcolor=GRID,
                                tickfont=dict(size=7,color=TC), linecolor=GRID),
                angularaxis=dict(gridcolor=GRID, tickfont=dict(size=9.5,color='#94a3b8'),
                                 linecolor=GRID),
            ),
            paper_bgcolor=BG, showlegend=False, height=260,
            margin=dict(t=20,b=20,l=40,r=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    with cc2:
        st.markdown("#### Score vs Other Matches")
        all_m = compute_matches(u)
        if all_m:
            mnames  = [(mx.get('name') or '?')[:18] for mx,_ in all_m]
            mscores = [sv for _,sv in all_m]
            colors  = ['#f59e0b' if mx.get('id')==eid else '#1e1e2e' for mx,_ in all_m]
            borders = ['#fbbf24' if mx.get('id')==eid else '#2a2a42' for mx,_ in all_m]
            fig2 = go.Figure(go.Bar(
                x=mscores, y=mnames, orientation='h',
                marker=dict(color=colors, line=dict(color=borders, width=1.5)),
                text=[f"{sv}%" for sv in mscores], textposition='outside',
                textfont=dict(size=10, color='#94a3b8'),
            ))
            fig2.update_layout(
                xaxis=dict(range=[0,118], showgrid=False, zeroline=False,
                           showticklabels=False),
                yaxis=dict(autorange='reversed', tickfont=dict(size=9.5,color='#94a3b8')),
                plot_bgcolor=BG, paper_bgcolor=BG, font_color='#f1f5f9',
                showlegend=False, height=260, margin=dict(t=20,b=20,l=4,r=44),
            )
            st.plotly_chart(fig2, use_container_width=True)

    with st.container(border=True):
        st.markdown(lbl("Score Breakdown"), unsafe_allow_html=True)
        reasons = {
            "Sector":   "Same sector = full credit" if sec_match else "Sectors differ",
            "Stage":    "Stage in investor's target list" if stg_match else "Stage not targeted",
            "Location": "Same region" if loc_match else "Different regions",
            "Semantic": f"{score}% cosine similarity — pitch vs thesis",
            "Scale":    "Ticket size fits stage norms" if in_range else "Ticket outside stage range",
        }
        for sig,val in radar_scores(s_e or {}, inv_e or {}, score).items():
            vc = "#34d399" if val>=70 else ("#fbbf24" if val>=50 else "#f87171")
            sc1,sc2,sc3 = st.columns([2,3,4])
            sc1.markdown(f'<span style="font-size:.85rem;font-weight:700;color:#e2e8f0">{sig}</span>',
                         unsafe_allow_html=True)
            sc2.progress(max(0.0, min(val/100, 1.0)))
            sc3.caption(reasons.get(sig,''))

    flags = gen_red_flags(s_e or {}, inv_e or {})
    if flags:
        with st.container(border=True):
            st.markdown(
                '<span style="font-size:.68rem;font-weight:700;color:#f87171;'
                'text-transform:uppercase;letter-spacing:.09em">'
                'Potential Mismatches</span>', unsafe_allow_html=True)
            for fl in flags:
                st.markdown(
                    f'<div style="background:rgba(248,113,113,.07);border:1px solid '
                    f'rgba(248,113,113,.2);border-radius:7px;padding:9px 14px;'
                    f'margin-bottom:6px;font-size:.85rem;color:#fca5a5">{fl}</div>',
                    unsafe_allow_html=True)

    their_txt = m.get('thesis','') if role=="Investor" else m.get('description','')
    my_txt    = (me or {}).get('description','') if u['role']=="Startup" \
                else (me or {}).get('thesis','')
    kw = kw_overlap(my_txt, their_txt)
    if kw:
        with st.container(border=True):
            st.markdown(lbl("Shared Themes"), unsafe_allow_html=True)
            st.markdown(" ".join(tag_html(k) for k in kw), unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(lbl("Recommended Next Steps"), unsafe_allow_html=True)
        for i,step in enumerate(gen_next_steps(me or {}, m, u['role']),1):
            st.markdown(
                f'<div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:11px">'
                f'<div style="width:22px;height:22px;border-radius:50%;flex-shrink:0;'
                f'background:linear-gradient(135deg,#92400e,#f59e0b);'
                f'display:flex;align-items:center;justify-content:center;'
                f'font-size:.68rem;font-weight:900;color:#0a0a0f">{i}</div>'
                f'<p style="margin:0;font-size:.88rem;color:#cbd5e1;line-height:1.65">'
                f'{step}</p></div>',
                unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(lbl("Reach Out"), unsafe_allow_html=True)
        mn  = (me or {}).get('name','')
        tn  = m.get('name','')
        mf  = (me or {}).get('firm','')
        if u['role']=="Startup":
            subj = f"Partnership Inquiry from {mn}"
            body = (f"Hi {tn},%0A%0AI found your profile on StartMatch and see "
                    f"strong alignment with {mn}.%0A%0AI'd love a brief intro call."
                    f"%0A%0ABest,%0A{mn}")
        else:
            subj = f"Investment Inquiry — {tn}"
            body = (f"Hi {tn} team,%0A%0AI found your profile on StartMatch. "
                    f"Our thesis aligns closely with what you are building."
                    f"%0A%0AWould love to connect.%0A%0ABest,%0A{mn}"
                    f"{' — '+mf if mf else ''}")
        st.caption(f"Pre-drafted introduction to {tn}. Opens your email client.")
        st.link_button("Send Introduction Email",
                       f"mailto:?subject={subj.replace(' ','%20')}&body={body}")

    with st.expander("Full Profile Details"):
        if role == "Investor":
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Firm",      m.get('firm','—'))
            c2.metric("Sector",    m.get('sector','—'))
            c3.metric("Location",  m.get('location','—'))
            c4.metric("Ticket",    fmt_m(m.get('ticket_size',0) or 0))
            c5,c6,c7,c8 = st.columns(4)
            c5.metric("Fund Size",    fmt_m(m.get('fund_size',0) or 0))
            c6.metric("Portfolio",    str(m.get('portfolio_count',0) or 0))
            c7.metric("Deals/Year",   str(m.get('investments_per_year',0) or 0))
            c8.metric("Co-invest",    m.get('co_invest_pref','—') or '—')
            st.markdown("**Investment Thesis**")
            st.write(m.get('thesis','—'))
            if m.get('notable_investments'): st.caption(f"Notable: {m['notable_investments']}")
            if m.get('geo_focus'): st.caption(f"Geo: {m['geo_focus']}")
            if m.get('website'): st.markdown(f"[Website]({m['website']})")
            if m.get('linkedin'): st.markdown(f"[LinkedIn]({m['linkedin']})")
        else:
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Sector",   m.get('sector','—'))
            c2.metric("Stage",    m.get('stage','—'))
            c3.metric("Location", m.get('location','—'))
            rev = m.get('revenue',0) or 0
            c4.metric("Revenue",  fmt_m(rev) if rev>0 else "Pre-revenue")
            c5,c6,c7,c8 = st.columns(4)
            c5.metric("MRR",      fmt_m(m.get('mrr',0) or 0))
            c6.metric("Growth",   f"{m.get('growth_rate',0) or 0:.1f}%/mo")
            c7.metric("Runway",   f"{m.get('runway',0) or 0}mo")
            c8.metric("Team",     str(m.get('team_size',0) or 0))
            st.markdown(f"**Founder:** {m.get('founder','—')}")
            st.write(m.get('description','—'))
            if m.get('target_market'): st.caption(f"Market: {m['target_market']}")
            if m.get('website'): st.markdown(f"[Website]({m['website']})")
            if m.get('linkedin'): st.markdown(f"[LinkedIn]({m['linkedin']})")

# ═══════════════════════════════════════════════════════════════════════════════
# MARKET STATS TAB
# ═══════════════════════════════════════════════════════════════════════════════
def stats_tab():
    u  = st.session_state.user
    me = get_me()
    my_sector = (me or {}).get('sector','')
    my_stage  = (me or {}).get('stage','')

    try:
        seed_s = pd.read_csv("data/startups.csv");  seed_s.columns = seed_s.columns.str.strip()
        seed_i = pd.read_csv("data/investors.csv"); seed_i.columns = seed_i.columns.str.strip()
        for df,rn in [(seed_s,{'sector':'Sector','stage':'Stage','location':'Location'}),
                      (seed_i,{'sector':'Sector','stage':'Stage','location':'Location'})]:
            for old,new in rn.items():
                if new not in df.columns and old in df.columns:
                    df.rename(columns={old:new}, inplace=True)
    except Exception:
        seed_s, seed_i = pd.DataFrame(), pd.DataFrame()

    def to_s(rows):
        if not rows: return pd.DataFrame(columns=['Sector','Stage','Location'])
        return pd.DataFrame(rows).rename(columns={'sector':'Sector','stage':'Stage','location':'Location'})
    def to_i(rows):
        if not rows: return pd.DataFrame(columns=['Sector','Stage','Location'])
        return pd.DataFrame(rows).rename(columns={'sector':'Sector','stage':'Stage','location':'Location'})

    reg_s  = to_s(all_startups());  reg_i = to_i(all_investors())
    scols  = ['Sector','Stage','Location']
    all_s  = pd.concat([seed_s[scols] if not seed_s.empty and all(c in seed_s for c in scols)
                        else pd.DataFrame(), reg_s[scols] if not reg_s.empty else pd.DataFrame()],
                       ignore_index=True)
    all_i  = pd.concat([seed_i[scols] if not seed_i.empty and all(c in seed_i for c in scols)
                        else pd.DataFrame(), reg_i[scols] if not reg_i.empty else pd.DataFrame()],
                       ignore_index=True)

    st.markdown("## Market Intelligence")
    st.markdown("---")
    st.info(market_summary(all_s, all_i, my_sector, u['role']))
    st.markdown("<br>", unsafe_allow_html=True)

    BG   = "#13131f"; GRID = "#1a1a2e"; TC = "#475569"
    AMBER_SCALE = [[0,"#1a1a2e"],[0.5,"#92400e"],[1,"#f59e0b"]]
    PIE_C = ["#f59e0b","#818cf8","#2dd4bf","#34d399","#f87171",
             "#c084fc","#38bdf8","#a3e635","#fb923c","#fbbf24"]

    def bar(df, col, yl, title):
        if df.empty or col not in df.columns: return None
        d = df[col].value_counts().reset_index(); d.columns=[col,yl]
        f = go.Figure(go.Bar(
            x=d[col], y=d[yl],
            marker=dict(color=d[yl], colorscale=AMBER_SCALE, showscale=False),
            text=d[yl], textposition='outside',
            textfont=dict(size=10, color='#64748b'),
        ))
        f.update_layout(
            xaxis=dict(tickfont=dict(size=9,color=TC), showgrid=False),
            yaxis=dict(tickfont=dict(size=9,color=TC), gridcolor=GRID, gridwidth=0.5),
            plot_bgcolor=BG, paper_bgcolor=BG, showlegend=False,
            margin=dict(t=8,b=8,l=4,r=4), height=220,
        )
        return f

    def donut(df, col, title):
        if df.empty or col not in df.columns: return None
        d = df[col].value_counts().reset_index(); d.columns=[col,'Count']
        f = go.Figure(go.Pie(
            labels=d[col], values=d['Count'], hole=.5,
            marker=dict(colors=PIE_C[:len(d)], line=dict(color='#0d0d14',width=2)),
            textfont=dict(size=9,color='#f1f5f9'), showlegend=True,
        ))
        f.update_layout(
            paper_bgcolor=BG, font_color='#94a3b8',
            legend=dict(font=dict(size=8,color='#94a3b8'), bgcolor='rgba(0,0,0,0)',
                        orientation='v', x=1.0, y=0.5),
            margin=dict(t=8,b=8,l=8,r=8), height=220,
        )
        return f

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.markdown("#### Startups by Sector")
        ci = chart_insight(all_s, "Sector", "startups",
                           my_sector if u['role']=="Startup" else None)
        if ci: st.caption(ci)
        f = bar(all_s,"Sector","Count","")
        if f: st.plotly_chart(f, use_container_width=True)
    with r1c2:
        st.markdown("#### Stage Distribution")
        ci = chart_insight(all_s, "Stage", "startups",
                           my_stage if u['role']=="Startup" else None)
        if ci: st.caption(ci)
        f = donut(all_s,"Stage","")
        if f: st.plotly_chart(f, use_container_width=True)

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.markdown("#### Investors by Sector")
        ci = chart_insight(all_i,"Sector","investors",
                           my_sector if u['role']=="Investor" else None)
        if ci: st.caption(ci)
        f = bar(all_i,"Sector","Count","")
        if f: st.plotly_chart(f, use_container_width=True)
    with r2c2:
        st.markdown("#### Startups by Location")
        ci = chart_insight(all_s,"Location","startups",None)
        if ci: st.caption(ci)
        f = bar(all_s,"Location","Count","")
        if f: st.plotly_chart(f, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Your Position in the Market")
    p1,p2,p3 = st.columns(3)
    if u['role']=="Startup":
        comp = len(all_s[all_s['Sector']==my_sector]) if 'Sector' in all_s.columns and my_sector else 0
        atstg= len(all_s[all_s['Stage']==my_stage])   if 'Stage'  in all_s.columns and my_stage  else 0
        invm = len(all_i[all_i['Sector']==my_sector]) if 'Sector' in all_i.columns and my_sector else 0
        p1.metric("Startups in Your Sector",        comp)
        p2.metric("Startups at Your Stage",          atstg)
        p3.metric("Investors Targeting Your Sector", invm)
    else:
        comp = len(all_i[all_i['Sector']==my_sector]) if 'Sector' in all_i.columns and my_sector else 0
        opp  = len(all_s[all_s['Sector']==my_sector]) if 'Sector' in all_s.columns and my_sector else 0
        totl = len(all_startups())
        p1.metric("Investors in Your Sector",     comp)
        p2.metric("Startups in Your Focus",       opp)
        p3.metric("Total Registered Startups",    totl)

# ═══════════════════════════════════════════════════════════════════════════════
# EDIT PROFILE
# ═══════════════════════════════════════════════════════════════════════════════
def edit_profile_page():
    u = st.session_state.user
    e = get_me()
    if not e: st.error("Profile not found."); return
    render_header()
    st.markdown("## Edit Profile"); st.markdown("---")

    with st.container(border=True):
        if u['role']=="Startup":
            r1,r2 = st.columns(2)
            name    = r1.text_input("Company Name",  value=e.get('name',''),    key="ep_n")
            founder = r2.text_input("Founder Name",  value=e.get('founder',''), key="ep_f")
            r3,r4   = st.columns(2)
            si = SECTORS.index(e['sector']) if e.get('sector') in SECTORS else 0
            sector   = r3.selectbox("Sector", SECTORS, index=si, key="ep_sec")
            sti= STAGES.index(e['stage']) if e.get('stage') in STAGES else 0
            stage    = r4.selectbox("Stage", STAGES, index=sti, key="ep_stg")
            r5,r6   = st.columns(2)
            location = r5.text_input("City",     value=e.get('location',''), key="ep_loc")
            country  = r6.text_input("Country",  value=e.get('country',''),  key="ep_cty")
            r7,r8   = st.columns(2)
            bmi = BIZ_MODELS.index(e['business_model']) if e.get('business_model') in BIZ_MODELS else 0
            biz_model    = r7.selectbox("Business Model", BIZ_MODELS, index=bmi, key="ep_bm")
            target_market= r8.text_input("Target Market", value=e.get('target_market',''), key="ep_tm")
            website  = st.text_input("Website", value=e.get('website',''),  key="ep_web")
            linkedin = st.text_input("LinkedIn", value=e.get('linkedin',''), key="ep_li")
            desc     = st.text_area("Pitch / Description", value=e.get('description',''),
                                    height=130, key="ep_desc")
            st.caption(f"{len(desc)} chars")
            st.markdown("---")
            r9,r10,r11 = st.columns(3)
            revenue    = r9.number_input("Annual Revenue ($)", min_value=0,
                                         value=int(e.get('revenue') or 0), step=10000, key="ep_rev")
            mrr        = r10.number_input("MRR ($)", min_value=0,
                                          value=int(e.get('mrr') or 0), step=1000, key="ep_mrr")
            team_size  = r11.number_input("Team Size", min_value=0,
                                          value=int(e.get('team_size') or 0), step=1, key="ep_ts")
            r12,r13,r14 = st.columns(3)
            growth_rate = r12.number_input("MoM Growth (%)", min_value=0.0,
                                           value=float(e.get('growth_rate') or 0), step=0.5, key="ep_gr")
            runway      = r13.number_input("Runway (months)", min_value=0,
                                           value=int(e.get('runway') or 0), step=1, key="ep_rw")
            burn_rate   = r14.number_input("Monthly Burn ($)", min_value=0,
                                           value=int(e.get('burn_rate') or 0), step=5000, key="ep_br")
            if st.button("Save Changes", use_container_width=True):
                upd_startup({'id':e['id'],'name':name,'founder':founder,'sector':sector,
                             'stage':stage,'location':location,'description':desc,
                             'revenue':revenue,'website':website,'team_size':team_size,
                             'linkedin':linkedin,'target_market':target_market,
                             'business_model':biz_model,'country':country,'mrr':mrr,
                             'growth_rate':growth_rate,'runway':runway,'burn_rate':burn_rate})
                st.success("Profile updated."); st.session_state.edit_mode=False; st.rerun()
        else:
            r1,r2 = st.columns(2)
            name = r1.text_input("Full Name",  value=e.get('name',''), key="ep_n")
            firm = r2.text_input("Firm / Fund",value=e.get('firm',''), key="ep_firm")
            r3,r4 = st.columns(2)
            si = SECTORS.index(e['sector']) if e.get('sector') in SECTORS else 0
            sector   = r3.selectbox("Primary Sector", SECTORS, index=si, key="ep_sec")
            location = r4.text_input("City", value=e.get('location',''), key="ep_loc")
            curr_stgs = [s.strip() for s in (e.get('stage') or '').split(',') if s.strip() in STAGES]
            stage_sel = st.multiselect("Preferred Stages", STAGES, default=curr_stgs, key="ep_stg")
            r5,r6 = st.columns(2)
            bmi2 = (["Any"]+BIZ_MODELS).index(e['business_model_pref']) \
                   if e.get('business_model_pref') in ["Any"]+BIZ_MODELS else 0
            bm_pref = r5.selectbox("Preferred Biz Model", ["Any"]+BIZ_MODELS,
                                   index=bmi2, key="ep_bm")
            coi = CO_INVEST.index(e['co_invest_pref']) if e.get('co_invest_pref') in CO_INVEST else 0
            co_inv  = r6.selectbox("Co-invest Pref", CO_INVEST, index=coi, key="ep_ci")
            r7,r8 = st.columns(2)
            dti = DECISION_TL.index(e['decision_timeline']) \
                  if e.get('decision_timeline') in DECISION_TL else 0
            dtl     = r7.selectbox("Decision Timeline", DECISION_TL, index=dti, key="ep_dtl")
            geo_cur = [g.strip() for g in (e.get('geo_focus') or '').split(',')
                       if g.strip() in GEO_REGIONS]
            geo     = r8.multiselect("Geographic Focus", GEO_REGIONS,
                                     default=geo_cur, key="ep_geo")
            website = st.text_input("Website", value=e.get('website',''), key="ep_web")
            linkedin= st.text_input("LinkedIn", value=e.get('linkedin',''), key="ep_li")
            notable = st.text_input("Notable Investments",
                                    value=e.get('notable_investments',''), key="ep_ni")
            thesis  = st.text_area("Investment Thesis", value=e.get('thesis',''),
                                   height=130, key="ep_thesis")
            st.caption(f"{len(thesis)} chars")
            st.markdown("---")
            r9,r10,r11 = st.columns(3)
            fund_size = r9.number_input("Fund Size ($)", min_value=0,
                                        value=int(e.get('fund_size') or 0),
                                        step=10_000_000, key="ep_fs")
            ticket    = r10.number_input("Ticket Size ($)", min_value=0,
                                         value=int(e.get('ticket_size') or 0),
                                         step=50_000, key="ep_tick")
            portco    = r11.number_input("Portfolio Cos.", min_value=0,
                                         value=int(e.get('portfolio_count') or 0),
                                         step=1, key="ep_pc")
            ipy = st.number_input("Deals / Year", min_value=0,
                                  value=int(e.get('investments_per_year') or 0),
                                  step=1, key="ep_ipy")
            if st.button("Save Changes", use_container_width=True):
                upd_investor({'id':e['id'],'name':name,'firm':firm,'sector':sector,
                              'stage':", ".join(stage_sel),'location':location,
                              'thesis':thesis,'ticket_size':ticket,'website':website,
                              'fund_size':fund_size,'portfolio_count':portco,
                              'notable_investments':notable,'geo_focus':", ".join(geo),
                              'co_invest_pref':co_inv,'decision_timeline':dtl,
                              'business_model_pref':bm_pref,'linkedin':linkedin,
                              'investments_per_year':ipy})
                st.success("Profile updated."); st.session_state.edit_mode=False; st.rerun()

    if st.button("Cancel"):
        st.session_state.edit_mode=False; st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.authenticated:
    if st.session_state.auth_view=="signup": signup_page()
    else:                                    login_page()
else:
    if st.session_state.edit_mode:
        edit_profile_page()
    elif st.session_state.drilldown_id:
        drilldown_page()
    else:
        render_header()
        t1,t2,t3,t4 = st.tabs(["Dashboard","Profile","Matches","Market"])
        with t1: dashboard_tab()
        with t2: profile_tab()
        with t3: matches_tab()
        with t4: stats_tab()

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>.footer{position:fixed;left:0;bottom:10px;width:100%;text-align:center;
color:#475569;font-size:.72rem;letter-spacing:.09em;pointer-events:none;
font-weight:600;font-family:'Inter',sans-serif}</style>
<div class="footer">STARTMATCH &nbsp;·&nbsp; BUILT BY U.K.B.</div>
""", unsafe_allow_html=True)
