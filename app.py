import streamlit as st
import pandas as pd
import numpy as np
import sqlite3, hashlib, re, os, uuid
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px
import plotly.graph_objects as go

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
DB = "data/db.sqlite"
SECTORS = ["AI/ML","FinTech","HealthTech","EdTech","CleanTech","Cybersecurity",
           "AgriTech","HR Tech","Manufacturing","Logistics","Mental Health",
           "SaaS","E-commerce","Web3","Other"]
STAGES  = ["Pre-Seed","Seed","Series A","Series B","Series C+"]
STAGE_TICKET = {
    "Pre-Seed": (0, 500_000),
    "Seed":     (100_000, 2_000_000),
    "Series A": (1_000_000, 10_000_000),
    "Series B": (5_000_000, 30_000_000),
    "Series C+": (20_000_000, 200_000_000),
}
STOP = {"a","an","the","and","or","but","in","on","at","to","for","of","with",
        "by","from","is","are","was","were","be","been","have","has","had",
        "do","does","did","will","would","could","should","may","might","that",
        "this","these","those","it","its","as","into","their","our","we","they",
        "using","use","used","via","across","through","within","between","such",
        "also","both","each","more","most","over","than","up","out","can","not",
        "no","all","any","if","about","after","before","during","new","large",
        "high","low","key","based","build","built","help","helps","scale",
        "company","startup","investor","fund","capital","growth","platform",
        "tech","technology","solution","solutions","provides","provide"}

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="StartMatch", layout="wide",
                   initial_sidebar_state="collapsed")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
.main, .block-container,
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"] {
  background-color: #0f0f1a !important;
  color: #e2e8f0 !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Sidebar */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
  background: #0a0a14 !important;
  border-right: 1px solid #1e1e3a !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] div { color: #94a3b8 !important; }
[data-testid="stSidebar"] .stButton > button {
  background: #1e1e3a !important; color: #94a3b8 !important;
  border: 1px solid #2a2a4a !important; border-radius: 8px !important;
  font-weight: 500 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: #2a2a4a !important; color: #e2e8f0 !important;
}

/* Text */
p, span, div, label, li, td, th,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] * { color: #e2e8f0 !important; }
h1, h2, h3, h4 {
  color: #f8fafc !important;
  font-weight: 700 !important;
  font-family: 'Inter', sans-serif !important;
}
.stCaption, [data-testid="stCaptionContainer"] * { color: #64748b !important; }

/* Cards */
.card {
  background: #16162a;
  border: 1px solid #1e1e3a;
  border-radius: 14px;
  padding: 24px 28px;
  margin-bottom: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,.3);
}
.match-card {
  background: #16162a;
  border: 1px solid #1e1e3a;
  border-radius: 14px;
  padding: 20px 24px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all .2s ease;
  position: relative;
  overflow: hidden;
}
.match-card::before {
  content: '';
  position: absolute; left:0; top:0; bottom:0; width:4px;
  background: linear-gradient(180deg, #6366f1, #a855f7);
  border-radius: 14px 0 0 14px;
}
.match-card:hover {
  border-color: #6366f1;
  box-shadow: 0 0 0 1px #6366f1, 0 8px 30px rgba(99,102,241,.2);
  transform: translateY(-1px);
}

/* Tooltip */
.has-tip { position: relative; }
.has-tip .tip {
  display: none; position: absolute;
  bottom: calc(100% + 8px); left:0; right:0;
  background: #1e1e3a;
  color: #e2e8f0 !important;
  font-size: .82rem !important;
  border-radius: 10px; padding: 12px 16px;
  z-index: 9999; line-height: 1.65;
  border: 1px solid #2a2a4a;
  box-shadow: 0 12px 40px rgba(0,0,0,.5);
  pointer-events: none;
}
.has-tip:hover .tip { display: block; }

/* Buttons */
.stButton > button {
  background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  font-size: .875rem !important;
  padding: 8px 20px !important;
  transition: all .2s !important;
  box-shadow: 0 2px 12px rgba(99,102,241,.35) !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
  box-shadow: 0 4px 20px rgba(99,102,241,.5) !important;
  transform: translateY(-1px) !important;
}

/* Link button */
div[data-testid="stLinkButton"] a {
  background: linear-gradient(135deg, #f97316, #ea580c) !important;
  color: #ffffff !important; border: none !important;
  border-radius: 10px !important; padding: 9px 22px !important;
  font-weight: 600 !important; font-size: .875rem !important;
  text-decoration: none !important;
  box-shadow: 0 2px 12px rgba(249,115,22,.4) !important;
  transition: all .2s !important; display: inline-block !important;
}
div[data-testid="stLinkButton"] a:hover {
  box-shadow: 0 4px 20px rgba(249,115,22,.55) !important;
  transform: translateY(-1px) !important;
}

/* Inputs */
input[type="text"], input[type="password"], input[type="number"], textarea,
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea {
  background: #0f0f1a !important;
  color: #e2e8f0 !important;
  border: 1.5px solid #1e1e3a !important;
  border-radius: 10px !important;
  font-size: .95rem !important;
  transition: border-color .15s !important;
}
input:focus, textarea:focus {
  border-color: #6366f1 !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,.2) !important;
  outline: none !important;
}
input::placeholder, textarea::placeholder { color: #374151 !important; }

/* Select */
[data-baseweb="select"] > div:first-child {
  background: #0f0f1a !important;
  border: 1.5px solid #1e1e3a !important;
  border-radius: 10px !important;
}
[data-baseweb="select"] span,
[data-baseweb="select"] div { color: #e2e8f0 !important; }
[data-baseweb="popover"],
[data-baseweb="menu"] { background: #16162a !important; border: 1px solid #1e1e3a !important; }
[data-baseweb="menu"] li { color: #e2e8f0 !important; }
[data-baseweb="menu"] li:hover { background: #1e1e3a !important; }

/* Multiselect tags */
[data-baseweb="tag"] {
  background: #6366f1 !important; border-radius: 6px !important;
}
[data-baseweb="tag"] span { color: #fff !important; }

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: #16162a !important; border-radius: 12px !important;
  padding: 5px !important; border: 1px solid #1e1e3a !important;
  gap: 4px !important;
}
button[data-baseweb="tab"] {
  border-radius: 8px !important; font-weight: 500 !important;
  font-size: .9rem !important; color: #64748b !important;
  background: transparent !important; padding: 9px 22px !important;
  transition: all .15s !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
  background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
  color: #ffffff !important; font-weight: 700 !important;
  box-shadow: 0 2px 12px rgba(99,102,241,.4) !important;
}

/* Metrics */
[data-testid="stMetric"] {
  background: #16162a !important; border: 1px solid #1e1e3a !important;
  border-radius: 12px !important; padding: 16px 18px !important;
  box-shadow: 0 4px 16px rgba(0,0,0,.25) !important;
}
[data-testid="stMetricLabel"] p {
  font-size: .70rem !important; font-weight: 700 !important;
  color: #64748b !important; text-transform: uppercase !important;
  letter-spacing: .07em !important;
}
[data-testid="stMetricValue"] {
  color: #f8fafc !important; font-size: 1.05rem !important; font-weight: 700 !important;
}

/* Alerts */
[data-testid="stAlert"] { border-radius: 10px !important; }
[data-testid="stAlert"] p { color: inherit !important; }

/* Badges */
.badge-high { background:linear-gradient(135deg,#059669,#047857); color:#fff !important; border-radius:6px; padding:4px 10px; font-size:.77rem; font-weight:700; }
.badge-mid  { background:linear-gradient(135deg,#d97706,#b45309); color:#fff !important; border-radius:6px; padding:4px 10px; font-size:.77rem; font-weight:700; }
.badge-low  { background:linear-gradient(135deg,#dc2626,#b91c1c); color:#fff !important; border-radius:6px; padding:4px 10px; font-size:.77rem; font-weight:700; }

.tag  { background:rgba(99,102,241,.2); color:#a5b4fc !important; border-radius:6px; padding:3px 9px; font-size:.77rem; margin:0 5px 5px 0; display:inline-block; font-weight:600; border:1px solid rgba(99,102,241,.3); }
.pill { background:#1e1e3a; color:#94a3b8 !important; border-radius:20px; padding:3px 11px; font-size:.77rem; margin:0 4px 4px 0; display:inline-block; border:1px solid #2a2a4a; }

.section-label {
  font-size:.70rem; font-weight:700; color:#64748b !important;
  text-transform:uppercase; letter-spacing:.09em;
  margin-bottom:8px; display:block;
}

/* Auth page */
.auth-logo {
  font-size:2.4rem; font-weight:900; letter-spacing:-.04em;
  background:linear-gradient(135deg,#6366f1 0%,#a855f7 50%,#ec4899 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  text-align:center; margin-bottom:4px;
}
.auth-sub {
  text-align:center; color:#64748b !important;
  font-size:.88rem; margin-bottom:28px;
}

/* Scrollbar */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#0a0a14; }
::-webkit-scrollbar-thumb { background:#1e1e3a; border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:#2a2a4a; }

/* Radio */
[data-testid="stRadio"] label p { color: #e2e8f0 !important; }

/* Expander */
[data-testid="stExpander"] {
  background: #16162a !important; border: 1px solid #1e1e3a !important;
  border-radius: 10px !important;
}
[data-testid="stExpander"] summary { color: #e2e8f0 !important; }

hr { border-color: #1e1e3a !important; }
#MainMenu, footer, [data-testid="stDecoration"],
[data-testid="stToolbar"] { display:none !important; }
</style>
""", unsafe_allow_html=True)

# ── DATABASE ──────────────────────────────────────────────────────────────────
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
            revenue REAL DEFAULT 0, website TEXT
        );
        CREATE TABLE IF NOT EXISTS investors (
            id TEXT PRIMARY KEY, name TEXT, firm TEXT, sector TEXT,
            stage TEXT, location TEXT, thesis TEXT,
            ticket_size REAL DEFAULT 0, website TEXT
        );
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL, role TEXT NOT NULL, entity_id TEXT NOT NULL
        );
    """)
    con.commit(); con.close()

init_db()

# ── CRUD ──────────────────────────────────────────────────────────────────────
def q(sql, params=(), many=False, write=False):
    con = get_con()
    cur = con.execute(sql, params)
    if write: con.commit(); con.close(); return None
    res = cur.fetchall() if many else cur.fetchone()
    con.close()
    return [dict(r) for r in res] if many else (dict(res) if res else None)

def get_startup(eid):   return q("SELECT * FROM startups  WHERE id=?", (eid,))
def get_investor(eid):  return q("SELECT * FROM investors WHERE id=?", (eid,))
def all_startups():     return q("SELECT * FROM startups",  many=True) or []
def all_investors():    return q("SELECT * FROM investors", many=True) or []
def get_user(u):        return q("SELECT * FROM users WHERE username=?", (u,))

def ins_startup(d):
    q("INSERT INTO startups VALUES(?,?,?,?,?,?,?,?,?)",
      (d['id'],d['name'],d['founder'],d['sector'],d['stage'],
       d['location'],d['description'],d['revenue'],d['website']), write=True)

def ins_investor(d):
    q("INSERT INTO investors VALUES(?,?,?,?,?,?,?,?,?)",
      (d['id'],d['name'],d['firm'],d['sector'],d['stage'],
       d['location'],d['thesis'],d['ticket_size'],d['website']), write=True)

def ins_user(username, pw, role, eid):
    q("INSERT INTO users VALUES(?,?,?,?)", (username,pw,role,eid), write=True)

def upd_startup(d):
    q("""UPDATE startups SET name=?,founder=?,sector=?,stage=?,
         location=?,description=?,revenue=?,website=? WHERE id=?""",
      (d['name'],d['founder'],d['sector'],d['stage'],d['location'],
       d['description'],d['revenue'],d['website'],d['id']), write=True)

def upd_investor(d):
    q("""UPDATE investors SET name=?,firm=?,sector=?,stage=?,
         location=?,thesis=?,ticket_size=?,website=? WHERE id=?""",
      (d['name'],d['firm'],d['sector'],d['stage'],d['location'],
       d['thesis'],d['ticket_size'],d['website'],d['id']), write=True)

def registered_opposite(role):
    """Return registered entities of the opposite role."""
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
    ph  = ",".join("?"*len(ids))
    return q(f"SELECT * FROM {tbl} WHERE id IN ({ph})", ids, many=True) or []

# ── MODEL ─────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading AI model...")
def model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def emb(text):
    return model().encode([text or ""], convert_to_numpy=True)[0]

def emb_many(texts):
    return model().encode([t or "" for t in texts], convert_to_numpy=True)

# ── MATCH ENGINE ──────────────────────────────────────────────────────────────
def compute_matches(user):
    role  = user['role']
    me    = get_startup(user['entity_id']) if role=="Startup" else get_investor(user['entity_id'])
    if not me: return []
    corpus = registered_opposite(role)
    if not corpus: return []
    my_text     = me.get('description') if role=="Startup" else me.get('thesis')
    my_emb      = emb(my_text or "")
    c_texts     = [(e.get('thesis') if role=="Startup" else e.get('description')) or "" for e in corpus]
    sims        = cosine_similarity([my_emb], emb_many(c_texts))[0]
    top         = np.argsort(sims)[::-1][:5]
    return [(corpus[i], round(float(sims[i])*100, 1)) for i in top]

def radar_scores(startup, investor, nlp_score):
    sector_fit = 100.0 if (startup.get('sector') or '') == (investor.get('sector') or '') else 15.0
    inv_stages = [s.strip() for s in (investor.get('stage') or '').split(',')]
    stage_fit  = 100.0 if startup.get('stage') in inv_stages else 20.0
    loc_fit    = 100.0 if (startup.get('location','') or '').lower().strip() == \
                          (investor.get('location','') or '').lower().strip() else 35.0
    ticket = investor.get('ticket_size', 0) or 0
    lo, hi = STAGE_TICKET.get(startup.get('stage',''), (0, float('inf')))
    if hi == float('inf'): hi = max(ticket * 2, 1)
    if lo <= ticket <= hi:  scale = 100.0
    elif ticket < lo and lo > 0: scale = max(10.0, 100 - ((lo-ticket)/lo)*90)
    else: scale = max(10.0, 100 - ((ticket-hi)/max(hi,1))*60)
    return {"Sector Fit":     round(sector_fit,1),
            "Stage Fit":      round(stage_fit,1),
            "Location":       round(loc_fit,1),
            "Semantic Match": round(nlp_score,1),
            "Scale Fit":      round(scale,1)}

def keywords(a, b, n=7):
    tok  = lambda t: {w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', t or '') if w.lower() not in STOP}
    pool = tok(a) & tok(b)
    if not pool: pool = tok(b)
    return sorted(pool)[:n]

def sbadge(s):
    cls = "badge-high" if s>=70 else ("badge-mid" if s>=50 else "badge-low")
    return f'<span class="{cls}">{s}%</span>'

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

# ── SESSION DEFAULTS ──────────────────────────────────────────────────────────
DEFS = dict(authenticated=False, user=None, auth_view="login",
            drilldown_id=None, drilldown_score=None, drilldown_role=None,
            edit_mode=False)
for k, v in DEFS.items():
    if k not in st.session_state: st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────────────────────────────────────
def auth_logo():
    st.markdown('<div class="auth-logo">StartMatch</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">AI-powered startup and investor matching</div>',
                unsafe_allow_html=True)

def login_page():
    _, c, _ = st.columns([1, 1.3, 1])
    with c:
        auth_logo()
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Sign in")
        u  = st.text_input("Username", placeholder="Enter your username", key="li_u")
        pw = st.text_input("Password", type="password",
                           placeholder="Enter your password", key="li_p")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Sign In", use_container_width=True):
                row = get_user(u.strip())
                if row and row['password'] == hash_pw(pw):
                    st.session_state.authenticated = True
                    st.session_state.user = row
                    st.rerun()
                else: st.error("Incorrect username or password.")
        with c2:
            if st.button("Create Account", use_container_width=True):
                st.session_state.auth_view = "signup"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#374151;font-size:.76rem;"
                    "margin-top:12px'>By continuing you agree to StartMatch Terms of Service</p>",
                    unsafe_allow_html=True)

def signup_page():
    _, c, _ = st.columns([1, 2.4, 1])
    with c:
        auth_logo()
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Create your account")
        role = st.radio("I am a", ["Startup","Investor"], horizontal=True, key="su_role")
        st.markdown("---")

        if role == "Startup":
            r1c1, r1c2 = st.columns(2)
            name    = r1c1.text_input("Company Name *", placeholder="e.g. NeuralCart", key="su_n")
            founder = r1c2.text_input("Founder Name *", placeholder="e.g. Priya Sharma", key="su_f")
            r2c1, r2c2 = st.columns(2)
            sector   = r2c1.selectbox("Sector *", SECTORS, key="su_sec")
            stage    = r2c2.selectbox("Funding Stage *", STAGES, key="su_stg")
            r3c1, r3c2 = st.columns(2)
            location = r3c1.text_input("Location *", placeholder="e.g. San Francisco", key="su_loc")
            revenue  = r3c2.number_input("Annual Revenue ($)", min_value=0, value=0,
                                         step=10000, key="su_rev")
            website  = st.text_input("Website URL", placeholder="https://...", key="su_web")
            st.markdown('<span class="section-label" style="margin-top:4px;display:block">'
                        'Pitch / Description *</span>', unsafe_allow_html=True)
            desc = st.text_area("", placeholder="What does your company do? What problem do you solve? "
                                "Describe your technology, target market, and traction. "
                                "More detail = better AI matches.",
                                height=110, key="su_desc", label_visibility="collapsed")
            st.caption(f"{len(desc)} characters")

        else:
            r1c1, r1c2 = st.columns(2)
            name = r1c1.text_input("Full Name *", placeholder="e.g. Sarah Chen", key="su_n")
            firm = r1c2.text_input("Firm / Fund Name *", placeholder="e.g. Sequoia Capital", key="su_firm")
            r2c1, r2c2 = st.columns(2)
            sector   = r2c1.selectbox("Primary Sector Focus *", SECTORS, key="su_sec")
            location = r2c2.text_input("Location *", placeholder="e.g. Menlo Park", key="su_loc")
            stage_sel = st.multiselect("Preferred Investment Stages *", STAGES,
                                       default=["Seed"], key="su_stg")
            stage = ", ".join(stage_sel)
            r3c1, r3c2 = st.columns(2)
            ticket  = r3c1.number_input("Typical Ticket Size ($)", min_value=0,
                                        value=500000, step=50000, key="su_tick")
            website = r3c2.text_input("LinkedIn / Website", placeholder="https://...", key="su_web")
            st.markdown('<span class="section-label" style="margin-top:4px;display:block">'
                        'Investment Thesis *</span>', unsafe_allow_html=True)
            thesis = st.text_area("", placeholder="Describe the kinds of companies you invest in, "
                                  "your thesis, what sectors and problems excite you. "
                                  "Used directly by the AI matching engine.",
                                  height=110, key="su_thesis", label_visibility="collapsed")
            st.caption(f"{len(thesis)} characters")

        st.markdown("---")
        st.markdown('<span class="section-label">Credentials</span>', unsafe_allow_html=True)
        cr1, cr2, cr3 = st.columns(3)
        uname = cr1.text_input("Username *", placeholder="Pick a username", key="su_u")
        pw1   = cr2.text_input("Password *", type="password",
                               placeholder="Min. 6 characters", key="su_p1")
        pw2   = cr3.text_input("Confirm Password *", type="password", key="su_p2")

        if st.button("Create Account", use_container_width=True):
            errs = []
            if not name.strip(): errs.append("Name is required.")
            if role=="Startup" and not founder.strip(): errs.append("Founder name is required.")
            if role=="Investor" and not firm.strip():   errs.append("Firm name is required.")
            if not location.strip(): errs.append("Location is required.")
            if role=="Startup" and not desc.strip():    errs.append("Description is required.")
            if role=="Investor" and not thesis.strip(): errs.append("Investment thesis is required.")
            if role=="Investor" and not stage_sel:      errs.append("Select at least one stage.")
            if not uname.strip(): errs.append("Username is required.")
            if len(pw1) < 6:      errs.append("Password must be at least 6 characters.")
            if pw1 != pw2:        errs.append("Passwords do not match.")
            if get_user(uname.strip()): errs.append("Username already taken.")
            if errs:
                for e in errs: st.error(e)
            else:
                eid = str(uuid.uuid4())
                if role == "Startup":
                    ins_startup({'id':eid,'name':name.strip(),'founder':founder.strip(),
                                 'sector':sector,'stage':stage,'location':location.strip(),
                                 'description':desc.strip(),'revenue':revenue,
                                 'website':website.strip()})
                else:
                    ins_investor({'id':eid,'name':name.strip(),'firm':firm.strip(),
                                  'sector':sector,'stage':stage,'location':location.strip(),
                                  'thesis':thesis.strip(),'ticket_size':ticket,
                                  'website':website.strip()})
                ins_user(uname.strip(), hash_pw(pw1), role, eid)
                st.success("Account created. Sign in below.")
                st.session_state.auth_view = "login"; st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Back to Sign In"):
            st.session_state.auth_view = "login"; st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def sidebar():
    u   = st.session_state.user
    me  = get_startup(u['entity_id']) if u['role']=="Startup" else get_investor(u['entity_id'])
    nm  = me['name'] if me else u['username']
    with st.sidebar:
        st.markdown(f"### {nm}")
        st.caption(f"{u['role']}  ·  @{u['username']}")
        st.markdown("---")
        if st.button("Sign Out", use_container_width=True):
            st.session_state.update(DEFS); st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  PAGES
# ─────────────────────────────────────────────────────────────────────────────
def profile_tab():
    u = st.session_state.user
    e = get_startup(u['entity_id']) if u['role']=="Startup" else get_investor(u['entity_id'])
    if not e: st.error("Profile not found."); return

    hc, ec = st.columns([5,1])
    with hc:
        st.markdown(f"# {e['name']}")
        sub = e.get('firm','') if u['role']=="Investor" else e.get('founder','')
        st.markdown(f"<p style='color:#64748b;margin-top:-12px'>{u['role']}"
                    f"{ ' — ' + sub if sub else ''}</p>", unsafe_allow_html=True)
    with ec:
        st.markdown("<div style='margin-top:20px'>", unsafe_allow_html=True)
        if st.button("Edit Profile", use_container_width=True):
            st.session_state.edit_mode = True; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

    if u['role'] == "Startup":
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Sector",   e.get('sector','—'))
        c2.metric("Stage",    e.get('stage','—'))
        c3.metric("Location", e.get('location','—'))
        rev = e.get('revenue',0) or 0
        c4.metric("Revenue", f"${rev:,.0f}" if rev>0 else "Pre-revenue")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Pitch / Description</span>', unsafe_allow_html=True)
        st.write(e.get('description','—'))
        if e.get('website'):
            st.markdown(f"[Visit Website]({e['website']})")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Firm",     e.get('firm','—'))
        c2.metric("Sector",   e.get('sector','—'))
        c3.metric("Location", e.get('location','—'))
        c4.metric("Ticket",   f"${e.get('ticket_size',0):,.0f}")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        stages = e.get('stage','')
        if stages:
            pills = " ".join(f'<span class="pill">{s.strip()}</span>' for s in stages.split(','))
            st.markdown('<span class="section-label">Preferred Stages</span>', unsafe_allow_html=True)
            st.markdown(f"<p style='margin:0 0 14px'>{pills}</p>", unsafe_allow_html=True)
        st.markdown('<span class="section-label">Investment Thesis</span>', unsafe_allow_html=True)
        st.write(e.get('thesis','—'))
        if e.get('website'):
            st.markdown(f"[LinkedIn / Website]({e['website']})")
        st.markdown('</div>', unsafe_allow_html=True)


def edit_profile_tab():
    u = st.session_state.user
    e = get_startup(u['entity_id']) if u['role']=="Startup" else get_investor(u['entity_id'])
    if not e: st.error("Profile not found."); return

    st.markdown("# Edit Profile"); st.markdown("---")
    st.markdown('<div class="card">', unsafe_allow_html=True)

    if u['role'] == "Startup":
        r1,r2 = st.columns(2)
        name    = r1.text_input("Company Name", value=e.get('name',''), key="ep_n")
        founder = r2.text_input("Founder Name", value=e.get('founder',''), key="ep_f")
        r3,r4 = st.columns(2)
        sec_idx = SECTORS.index(e['sector']) if e.get('sector') in SECTORS else 0
        sector  = r3.selectbox("Sector", SECTORS, index=sec_idx, key="ep_sec")
        stg_idx = STAGES.index(e['stage']) if e.get('stage') in STAGES else 0
        stage   = r4.selectbox("Stage", STAGES, index=stg_idx, key="ep_stg")
        r5,r6 = st.columns(2)
        location = r5.text_input("Location", value=e.get('location',''), key="ep_loc")
        revenue  = r6.number_input("Revenue ($)", min_value=0,
                                   value=int(e.get('revenue') or 0), step=10000, key="ep_rev")
        website = st.text_input("Website", value=e.get('website',''), key="ep_web")
        desc    = st.text_area("Pitch / Description", value=e.get('description',''),
                               height=140, key="ep_desc")
        st.caption(f"{len(desc)} characters")
        if st.button("Save Changes", use_container_width=True):
            upd_startup({'id':e['id'],'name':name,'founder':founder,'sector':sector,
                         'stage':stage,'location':location,'description':desc,
                         'revenue':revenue,'website':website})
            st.success("Saved."); st.session_state.edit_mode=False; st.rerun()
    else:
        r1,r2 = st.columns(2)
        name = r1.text_input("Full Name", value=e.get('name',''), key="ep_n")
        firm = r2.text_input("Firm Name", value=e.get('firm',''), key="ep_firm")
        r3,r4 = st.columns(2)
        sec_idx = SECTORS.index(e['sector']) if e.get('sector') in SECTORS else 0
        sector   = r3.selectbox("Sector", SECTORS, index=sec_idx, key="ep_sec")
        location = r4.text_input("Location", value=e.get('location',''), key="ep_loc")
        curr_stgs = [s.strip() for s in (e.get('stage') or '').split(',') if s.strip() in STAGES]
        stage_sel = st.multiselect("Preferred Stages", STAGES, default=curr_stgs, key="ep_stg")
        r5,r6 = st.columns(2)
        ticket  = r5.number_input("Ticket Size ($)", min_value=0,
                                  value=int(e.get('ticket_size') or 0), step=50000, key="ep_tick")
        website = r6.text_input("Website / LinkedIn", value=e.get('website',''), key="ep_web")
        thesis  = st.text_area("Investment Thesis", value=e.get('thesis',''),
                               height=140, key="ep_thesis")
        st.caption(f"{len(thesis)} characters")
        if st.button("Save Changes", use_container_width=True):
            upd_investor({'id':e['id'],'name':name,'firm':firm,'sector':sector,
                          'stage':", ".join(stage_sel),'location':location,
                          'thesis':thesis,'ticket_size':ticket,'website':website})
            st.success("Saved."); st.session_state.edit_mode=False; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Cancel"):
        st.session_state.edit_mode=False; st.rerun()


def matches_tab():
    u       = st.session_state.user
    role    = u['role']
    target  = "Investors" if role=="Startup" else "Startups"
    matches = compute_matches(u)

    st.markdown(f"### Top Matches — {target}")
    st.markdown("<p style='color:#64748b;font-size:.87rem;margin-top:-10px'>"
                "Ranked by semantic similarity. Hover a card to preview their profile. "
                "Updates in real time when you edit your profile.</p>",
                unsafe_allow_html=True)
    st.markdown("---")

    if not matches:
        st.markdown(f"""
        <div style="text-align:center;padding:64px 20px;background:#16162a;
                    border:1px dashed #2a2a4a;border-radius:16px">
          <div style="font-size:2.8rem;margin-bottom:14px;opacity:.6">—</div>
          <div style="font-size:1.1rem;font-weight:700;color:#f8fafc;margin-bottom:8px">
            No matches yet
          </div>
          <div style="color:#64748b;font-size:.9rem;max-width:360px;margin:0 auto;line-height:1.6">
            There are no registered {target} on the platform yet.<br>
            Invite them to join StartMatch to start getting AI-powered matches.
          </div>
        </div>""", unsafe_allow_html=True)
        return

    for rank, (m, score) in enumerate(matches, 1):
        is_startup = (role == "Investor")
        m_role  = "Startup" if is_startup else "Investor"
        name    = m.get('name','—')
        sector  = m.get('sector','—')
        stage   = m.get('stage','—')
        loc     = m.get('location','—')
        firm    = m.get('firm','')
        excerpt = (m.get('description') or m.get('thesis') or '')[:190]

        c_card, c_btn = st.columns([6.5, 1])
        with c_card:
            st.markdown(f"""
            <div class="has-tip">
              <div class="match-card">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap">
                  <span style="background:#1e1e3a;color:#64748b;font-size:.70rem;
                               font-weight:700;border-radius:4px;padding:2px 8px">#{rank}</span>
                  <strong style="font-size:1.02rem;color:#f8fafc">{name}</strong>
                  {'<span style="color:#64748b;font-size:.87rem">— '+firm+'</span>' if firm else ''}
                  {sbadge(score)}
                </div>
                <div style="display:flex;gap:6px;flex-wrap:wrap">
                  <span class="pill">{sector}</span>
                  <span class="pill">{stage}</span>
                  <span class="pill">{loc}</span>
                </div>
              </div>
              <div class="tip">{excerpt}{'...' if len(excerpt)==190 else ''}</div>
            </div>""", unsafe_allow_html=True)
        with c_btn:
            st.markdown("<div style='margin-top:22px'>", unsafe_allow_html=True)
            if st.button("View", key=f"v_{m['id']}_{rank}"):
                st.session_state.drilldown_id    = m['id']
                st.session_state.drilldown_score = score
                st.session_state.drilldown_role  = m_role
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def stats_tab():
    u = st.session_state.user

    try:
        seed_s = pd.read_csv("data/startups.csv")
        seed_i = pd.read_csv("data/investors.csv")
        seed_s.columns = seed_s.columns.str.strip()
        seed_i.columns = seed_i.columns.str.strip()
    except Exception:
        seed_s, seed_i = pd.DataFrame(), pd.DataFrame()

    def norm_s(rows):
        if not rows: return pd.DataFrame(columns=['Sector','Stage','Location','Revenue'])
        df = pd.DataFrame(rows).rename(columns={'sector':'Sector','stage':'Stage',
                                                  'location':'Location','revenue':'Revenue'})
        return df
    def norm_i(rows):
        if not rows: return pd.DataFrame(columns=['Sector','Stage','Location','TicketSize'])
        df = pd.DataFrame(rows).rename(columns={'sector':'Sector','stage':'Stage',
                                                  'location':'Location','ticket_size':'TicketSize'})
        return df

    reg_s_df = norm_s(all_startups())
    reg_i_df = norm_i(all_investors())
    all_s = pd.concat([seed_s, reg_s_df], ignore_index=True) if not seed_s.empty else reg_s_df
    all_i = pd.concat([seed_i, reg_i_df], ignore_index=True) if not seed_i.empty else reg_i_df

    me = (get_startup(u['entity_id']) if u['role']=="Startup"
          else get_investor(u['entity_id']))
    my_sector = (me or {}).get('sector','—')
    my_stage  = (me or {}).get('stage','—')

    st.markdown("### Market Statistics")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Registered Startups",  len(all_startups()))
    c2.metric("Registered Investors", len(all_investors()))
    c3.metric("Platform Entities",    len(all_s)+len(all_i))
    c4.metric("Your Sector",          my_sector)
    st.markdown("---")

    PAL = [[0,"#312e81"],[1,"#6366f1"]]
    LAY = dict(plot_bgcolor="#16162a", paper_bgcolor="#16162a",
               font_color="#e2e8f0", showlegend=False,
               margin=dict(t=48,b=24,l=10,r=10))
    PIE = ["#6366f1","#a855f7","#06b6d4","#f97316","#10b981","#f59e0b","#ef4444","#8b5cf6"]

    def bar(df, col, yl, title):
        if df.empty or col not in df.columns: return None
        d = df[col].value_counts().reset_index(); d.columns=[col,yl]
        f = px.bar(d, x=col, y=yl, title=title, color=yl, color_continuous_scale=PAL)
        f.update_layout(**LAY); f.update_xaxes(tickfont=dict(color="#94a3b8"))
        f.update_yaxes(tickfont=dict(color="#94a3b8")); return f

    def pie(df, col, title):
        if df.empty or col not in df.columns: return None
        d = df[col].value_counts().reset_index(); d.columns=[col,"Count"]
        f = px.pie(d, names=col, values="Count", title=title, color_discrete_sequence=PIE)
        f.update_layout(paper_bgcolor="#16162a", font_color="#e2e8f0",
                        margin=dict(t=48,b=10,l=10,r=10)); return f

    def sc(chart, col):
        if chart: col.plotly_chart(chart, use_container_width=True)

    r1c1, r1c2 = st.columns(2)
    sc(bar(all_s,"Sector","Startups","Startups by Sector"),   r1c1)
    sc(pie(all_s,"Stage","Startup Stage Distribution"),        r1c2)
    r2c1, r2c2 = st.columns(2)
    sc(bar(all_i,"Sector","Investors","Investors by Sector"),  r2c1)
    sc(bar(all_s,"Location","Startups","Startups by Location"),r2c2)

    st.markdown("---")
    st.markdown("### Your Position in the Market")
    p1,p2,p3 = st.columns(3)
    if u['role'] == "Startup":
        p1.metric("Startups in your sector", len(all_s[all_s['Sector']==my_sector]) if 'Sector' in all_s.columns else 0)
        p2.metric("Startups at your stage",  len(all_s[all_s['Stage']==my_stage])   if 'Stage'  in all_s.columns else 0)
        p3.metric("Investors targeting you",  len(all_i[all_i['Sector']==my_sector]) if 'Sector' in all_i.columns else 0)
    else:
        p1.metric("Investors in your sector",  len(all_i[all_i['Sector']==my_sector]) if 'Sector' in all_i.columns else 0)
        p2.metric("Startups in your focus",    len(all_s[all_s['Sector']==my_sector]) if 'Sector' in all_s.columns else 0)
        p3.metric("Total registered startups", len(all_startups()))


def drilldown_page():
    u     = st.session_state.user
    role  = st.session_state.drilldown_role
    score = st.session_state.drilldown_score
    eid   = st.session_state.drilldown_id
    m     = get_startup(eid) if role=="Startup" else get_investor(eid)
    me    = get_startup(u['entity_id']) if u['role']=="Startup" else get_investor(u['entity_id'])

    if not m:
        st.error("Profile not found.")
        if st.button("Back"): st.session_state.drilldown_id=None; st.rerun()
        return

    if st.button("Back to Matches"):
        st.session_state.drilldown_id=None; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    hc1, hc2 = st.columns([5,1])
    with hc1:
        st.markdown(f"# {m.get('name','—')}")
        sub = m.get('firm','') if role=="Investor" else m.get('founder','')
        if sub: st.markdown(f"<p style='color:#64748b;margin-top:-10px'>{sub}</p>",
                            unsafe_allow_html=True)
    with hc2:
        if score is not None:
            st.markdown(f"<div style='margin-top:24px;text-align:right'>"
                        f"{sbadge(score)}</div>", unsafe_allow_html=True)
    st.markdown("---")

    if role == "Investor":
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Firm",     m.get('firm','—'))
        c2.metric("Sector",   m.get('sector','—'))
        c3.metric("Location", m.get('location','—'))
        c4.metric("Ticket",   f"${m.get('ticket_size',0):,.0f}")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        stgs = m.get('stage','')
        if stgs:
            pills = " ".join(f'<span class="pill">{s.strip()}</span>' for s in stgs.split(','))
            st.markdown('<span class="section-label">Preferred Stages</span>', unsafe_allow_html=True)
            st.markdown(f"<p style='margin:0 0 14px'>{pills}</p>", unsafe_allow_html=True)
        st.markdown('<span class="section-label">Investment Thesis</span>', unsafe_allow_html=True)
        st.write(m.get('thesis','—'))
        if m.get('website'): st.markdown(f"[LinkedIn / Website]({m['website']})")
        st.markdown('</div>', unsafe_allow_html=True)
        their_text = m.get('thesis','')
        my_text    = (me or {}).get('description','')
        startup_e, investor_e = me or {}, m
    else:
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Sector",   m.get('sector','—'))
        c2.metric("Stage",    m.get('stage','—'))
        c3.metric("Location", m.get('location','—'))
        rev = m.get('revenue',0) or 0
        c4.metric("Revenue", f"${rev:,.0f}" if rev>0 else "Pre-revenue")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Founder</span>', unsafe_allow_html=True)
        st.write(m.get('founder','—'))
        st.markdown('<span class="section-label" style="margin-top:12px;display:block">'
                    'Description</span>', unsafe_allow_html=True)
        st.write(m.get('description','—'))
        if m.get('website'): st.markdown(f"[Visit Website]({m['website']})")
        st.markdown('</div>', unsafe_allow_html=True)
        their_text = m.get('description','')
        my_text    = (me or {}).get('thesis','')
        startup_e, investor_e = m, me or {}

    st.markdown("---")

    # ── Charts ────────────────────────────────────────────────────────────────
    chart_bg   = "#16162a"
    grid_color = "#1e1e3a"
    tick_color = "#64748b"

    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("#### Compatibility Breakdown")
        rd = radar_scores(startup_e, investor_e, score or 0)
        cats   = list(rd.keys())
        vals   = list(rd.values())
        fig = go.Figure(go.Scatterpolar(
            r=vals+[vals[0]], theta=cats+[cats[0]],
            fill='toself',
            fillcolor='rgba(99,102,241,0.18)',
            line=dict(color='#6366f1', width=2.5),
            marker=dict(color='#a5b4fc', size=7),
        ))
        fig.update_layout(
            polar=dict(
                bgcolor=chart_bg,
                radialaxis=dict(visible=True, range=[0,100],
                                gridcolor=grid_color, tickfont=dict(size=9,color=tick_color),
                                tickcolor=tick_color, linecolor=grid_color),
                angularaxis=dict(gridcolor=grid_color,
                                 tickfont=dict(size=10.5, color="#e2e8f0"),
                                 linecolor=grid_color),
            ),
            paper_bgcolor=chart_bg, plot_bgcolor=chart_bg,
            showlegend=False, height=300,
            margin=dict(t=20,b=20,l=50,r=50),
        )
        st.plotly_chart(fig, use_container_width=True)

    with cc2:
        st.markdown("#### Score vs Other Matches")
        all_m = compute_matches(u)
        if all_m:
            names_  = [mx.get('name','?') for mx,_ in all_m]
            scores_ = [s for _,s in all_m]
            colors_ = ['#6366f1' if mx.get('id')==eid else '#312e81' for mx,_ in all_m]
            fig2 = go.Figure(go.Bar(
                x=scores_, y=names_, orientation='h',
                marker=dict(color=colors_,
                            line=dict(color=['#a5b4fc' if mx.get('id')==eid else '#1e1e3a'
                                             for mx,_ in all_m], width=1.5)),
                text=[f"{s}%" for s in scores_],
                textposition='outside',
                textfont=dict(size=11, color='#e2e8f0'),
            ))
            fig2.update_layout(
                xaxis=dict(range=[0,115], showgrid=False, zeroline=False,
                           tickfont=dict(color=tick_color), title=""),
                yaxis=dict(autorange='reversed', tickfont=dict(color='#e2e8f0')),
                plot_bgcolor=chart_bg, paper_bgcolor=chart_bg,
                font_color='#e2e8f0', showlegend=False,
                margin=dict(t=20,b=20,l=10,r=60), height=300,
            )
            st.plotly_chart(fig2, use_container_width=True)

    # Why this match
    kw = keywords(my_text, their_text)
    if kw:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Why this match?</span>', unsafe_allow_html=True)
        tags = " ".join(f'<span class="tag">{k}</span>' for k in kw)
        st.markdown(f"<p style='color:#94a3b8;font-size:.88rem;margin-bottom:10px'>"
                    f"Semantic overlap detected across these themes:</p>{tags}",
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Reach out
    my_name    = (me or {}).get('name','')
    their_name = m.get('name','')
    if role == "Investor":
        subj = f"Partnership Inquiry from {my_name}"
        body = (f"Hi {their_name},%0A%0A"
                f"I came across your profile on StartMatch and see strong alignment "
                f"with {my_name}. I'd love a brief intro call.%0A%0ABest,%0A{my_name}")
    else:
        my_firm = (me or {}).get('firm','')
        subj = f"Investment Inquiry — {their_name}"
        body = (f"Hi {their_name} team,%0A%0A"
                f"I found your profile on StartMatch and believe there is a strong fit "
                f"with our thesis. Would love to connect.%0A%0A"
                f"Best,%0A{my_name}{' — '+my_firm if my_firm else ''}")
    mailto = f"mailto:?subject={subj.replace(' ','%20')}&body={body}"

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="section-label">Reach Out</span>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#94a3b8;font-size:.88rem;margin-bottom:14px'>"
                f"Pre-drafted introduction to {their_name}. Opens in your email client.</p>",
                unsafe_allow_html=True)
    st.link_button("Send Introduction Email", mailto)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    if st.session_state.auth_view == "signup": signup_page()
    else:                                       login_page()
else:
    sidebar()
    if st.session_state.edit_mode:
        edit_profile_tab()
    elif st.session_state.drilldown_id:
        drilldown_page()
    else:
        t1, t2, t3 = st.tabs(["Profile", "Matches", "Market Stats"])
        with t1: profile_tab()
        with t2: matches_tab()
        with t3: stats_tab()
# ── FOOTER ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 10px;
    width: 100%;
    text-align: center;
    color: #64748b;
    font-size: 0.8rem;
    letter-spacing: 0.05em;
}
</style>
<div class="footer">
    Made by UKB!
</div>
""", unsafe_allow_html=True)