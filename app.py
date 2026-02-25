import streamlit as st
import pandas as pd
import numpy as np
import json, hashlib, os, re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px

# ── Constants ──────────────────────────────────────────────────────────────────
USERS_FILE = "data/users.json"
STOP = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with","by",
    "from","is","are","was","were","be","been","being","have","has","had","do",
    "does","did","will","would","could","should","may","might","that","this",
    "these","those","it","its","as","into","their","our","we","they","he","she",
    "his","her","who","which","what","how","when","using","use","used","via",
    "across","through","within","between","such","also","both","each","more",
    "most","over","than","up","out","can","not","no","all","any","if","about",
    "after","before","during","new","large","high","low","key","based","scale",
}

st.set_page_config(page_title="StartMatch", layout="wide", initial_sidebar_state="collapsed")

# ── CSS — forced light, zero system-theme dependence ──────────────────────────
st.markdown("""
<style>
  /* === GLOBAL FORCE LIGHT === */
  html, body,
  [data-testid="stApp"],
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewContainer"] > section,
  .main, .block-container,
  [data-testid="stVerticalBlock"],
  [data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #f3f2ef !important;
    color: #1d2226 !important;
  }

  /* Sidebar */
  [data-testid="stSidebar"],
  [data-testid="stSidebar"] > div:first-child {
    background-color: #ffffff !important;
    border-right: 1px solid #e0ddd6 !important;
  }
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] div { color: #1d2226 !important; }

  /* All text */
  p, span, div, label, li, td, th,
  [data-testid="stMarkdownContainer"],
  [data-testid="stMarkdownContainer"] * {
    color: #1d2226 !important;
  }
  h1, h2, h3, h4, h5 {
    color: #1d2226 !important;
    font-weight: 700 !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
  }
  .stCaption, [data-testid="stCaptionContainer"] * { color: #666 !important; }

  /* Inputs */
  input[type="text"], input[type="password"], textarea,
  [data-baseweb="input"] input,
  [data-baseweb="textarea"] textarea {
    background-color: #ffffff !important;
    color: #1d2226 !important;
    border: 1px solid #c0b8ae !important;
    border-radius: 6px !important;
    font-size: .95rem !important;
  }
  input::placeholder, textarea::placeholder { color: #aaa !important; }

  /* Select boxes */
  [data-baseweb="select"] > div:first-child {
    background-color: #ffffff !important;
    border: 1px solid #c0b8ae !important;
    border-radius: 6px !important;
  }
  [data-baseweb="select"] span,
  [data-baseweb="select"] div { color: #1d2226 !important; }
  [data-baseweb="popover"] { background: #fff !important; }
  [data-baseweb="menu"] { background: #fff !important; }
  [data-baseweb="menu"] li { color: #1d2226 !important; }

  /* Radio */
  [data-testid="stRadio"] label p { color: #1d2226 !important; }

  /* Buttons */
  .stButton > button {
    background: #ffffff !important;
    color: #0a66c2 !important;
    border: 1.5px solid #0a66c2 !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
    font-size: .87rem !important;
    padding: 6px 18px !important;
    transition: all .18s ease !important;
  }
  .stButton > button:hover {
    background: #0a66c2 !important;
    color: #ffffff !important;
  }
  .stButton > button:focus:not(:active) {
    box-shadow: 0 0 0 3px rgba(10,102,194,.25) !important;
  }

  /* Link button */
  div[data-testid="stLinkButton"] a {
    background: #0a66c2 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 20px !important;
    padding: 8px 22px !important;
    font-weight: 600 !important;
    font-size: .87rem !important;
    text-decoration: none !important;
    display: inline-block !important;
    transition: background .18s !important;
  }
  div[data-testid="stLinkButton"] a:hover { background: #004182 !important; }

  /* Metrics */
  [data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #e0ddd6 !important;
    border-radius: 8px !important;
    padding: 16px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.04) !important;
  }
  [data-testid="stMetricLabel"] p {
    font-size: .70rem !important;
    font-weight: 700 !important;
    color: #666 !important;
    text-transform: uppercase !important;
    letter-spacing: .07em !important;
  }
  [data-testid="stMetricValue"] {
    color: #1d2226 !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
  }

  /* Alerts */
  [data-testid="stAlert"] { border-radius: 8px !important; }
  [data-testid="stAlert"] p { color: inherit !important; }

  /* Tabs */
  button[data-baseweb="tab"] {
    color: #555 !important;
    font-weight: 500 !important;
    background: transparent !important;
  }
  button[data-baseweb="tab"][aria-selected="true"] {
    color: #0a66c2 !important;
    font-weight: 700 !important;
  }

  /* Expander */
  [data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #e0ddd6 !important;
    border-radius: 8px !important;
  }
  [data-testid="stExpander"] summary { color: #1d2226 !important; }

  /* Dividers */
  hr { border-color: #e0ddd6 !important; margin: 16px 0 !important; }

  /* Hide Streamlit chrome */
  #MainMenu, footer, [data-testid="stDecoration"] { display: none !important; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: #f3f2ef; }
  ::-webkit-scrollbar-thumb { background: #c0b8ae; border-radius: 3px; }

  /* === COMPONENT CLASSES === */
  .card {
    background: #ffffff;
    border: 1px solid #e0ddd6;
    border-radius: 8px;
    padding: 22px 26px;
    margin-bottom: 14px;
    box-shadow: 0 1px 4px rgba(0,0,0,.04);
  }
  .match-card {
    background: #ffffff;
    border: 1px solid #e0ddd6;
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 2px;
    transition: box-shadow .18s;
  }
  .match-card:hover { box-shadow: 0 4px 14px rgba(0,0,0,.09); }

  /* Hover tooltip wrapper */
  .has-tip { position: relative; display: block; }
  .has-tip .tip-text {
    display: none;
    position: absolute;
    bottom: calc(100% + 8px);
    left: 0; right: 0;
    background: #1d2226;
    color: #f3f2ef !important;
    font-size: .80rem !important;
    line-height: 1.55;
    border-radius: 6px;
    padding: 10px 14px;
    z-index: 9999;
    box-shadow: 0 6px 16px rgba(0,0,0,.18);
    pointer-events: none;
  }
  .has-tip:hover .tip-text { display: block; }

  /* Action cards (home page) */
  .action-card {
    background: #ffffff;
    border: 1px solid #e0ddd6;
    border-radius: 10px;
    padding: 28px 20px 20px;
    text-align: center;
    transition: all .2s ease;
    min-height: 168px;
  }
  .action-card:hover {
    box-shadow: 0 6px 20px rgba(10,102,194,.1);
    border-color: #0a66c2;
    transform: translateY(-2px);
  }
  .ac-icon  { font-size: 1.9rem; margin-bottom: 12px; }
  .ac-title { font-size: 1rem; font-weight: 700; color: #1d2226 !important; margin-bottom: 6px; }
  .ac-desc  { font-size: .82rem; color: #666 !important; line-height: 1.5; }

  /* Saved strip */
  .saved-strip {
    background: #e8f2fd;
    border: 1px solid #b3d4f5;
    border-radius: 8px;
    padding: 12px 18px;
    margin-bottom: 8px;
  }
  .saved-strip strong, .saved-strip span { color: #1d2226 !important; }

  /* Badges */
  .badge-high { background:#057642; color:#fff !important; border-radius:4px; padding:3px 10px; font-size:.77rem; font-weight:700; }
  .badge-mid  { background:#b45309; color:#fff !important; border-radius:4px; padding:3px 10px; font-size:.77rem; font-weight:700; }
  .badge-low  { background:#b91c1c; color:#fff !important; border-radius:4px; padding:3px 10px; font-size:.77rem; font-weight:700; }

  .tag  { background:#e8f2fd; color:#0a66c2 !important; border-radius:4px;  padding:3px 9px;  font-size:.77rem; margin:0 5px 5px 0; display:inline-block; }
  .pill { background:#f0f0f0; color:#444   !important; border-radius:20px; padding:3px 10px; font-size:.77rem; margin:0 4px 4px 0; display:inline-block; }

  .section-label {
    font-size:.70rem; font-weight:700; color:#666 !important;
    text-transform:uppercase; letter-spacing:.08em;
    margin-bottom:6px; display:block;
  }

  /* Auth */
  .auth-logo {
    font-size: 2rem; font-weight: 800;
    color: #0a66c2 !important;
    text-align: center; margin-bottom: 4px; letter-spacing: -.02em;
  }
  .auth-tagline {
    font-size: .88rem; color: #666 !important;
    text-align: center; margin-bottom: 26px;
  }
</style>
""", unsafe_allow_html=True)

# ── Data & model ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    s = pd.read_csv("data/startups.csv")
    i = pd.read_csv("data/investors.csv")
    s.columns = s.columns.str.strip()   # fix any " ID" vs "ID" whitespace
    i.columns = i.columns.str.strip()
    return s, i

@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_data
def embed_corpus(texts: tuple) -> np.ndarray:          # tuple = hashable for cache
    return load_model().encode(list(texts), convert_to_numpy=True)

def embed_single(text: str) -> np.ndarray:             # no cache → real-time
    return load_model().encode([text], convert_to_numpy=True)[0]

startups, investors = load_data()
s_embs = embed_corpus(tuple(startups["Description"].tolist()))
i_embs = embed_corpus(tuple(investors["Thesis"].tolist()))

# ── Auth helpers ───────────────────────────────────────────────────────────────
def load_users() -> list:
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(u: list):
    with open(USERS_FILE, "w") as f:
        json.dump(u, f, indent=2)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def get_user(username: str):
    return next((u for u in load_users() if u["username"] == username), None)

def update_user(updated: dict):
    users = load_users()
    for idx, u in enumerate(users):
        if u["username"] == updated["username"]:
            users[idx] = updated
            break
    save_users(users)
    st.session_state.user = updated

# ── Match & util helpers ───────────────────────────────────────────────────────
def get_current_text(u: dict) -> str:
    if u.get("custom_text"):
        return u["custom_text"]
    if u["role"] == "Startup":
        return startups[startups["ID"] == u["linked_id"]].iloc[0]["Description"]
    return investors[investors["ID"] == u["linked_id"]].iloc[0]["Thesis"]

def compute_matches(u: dict) -> list:
    my_emb = embed_single(get_current_text(u))
    if u["role"] == "Startup":
        sims   = cosine_similarity([my_emb], i_embs)[0]
        corpus, role = investors, "Investor"
    else:
        sims   = cosine_similarity([my_emb], s_embs)[0]
        corpus, role = startups, "Startup"
    top = np.argsort(sims)[::-1][:5]
    return [(corpus.iloc[i], round(float(sims[i]) * 100, 1), role) for i in top]

def shared_keywords(a: str, b: str, n: int = 7) -> list[str]:
    tok  = lambda t: {w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', t) if w.lower() not in STOP}
    pool = tok(a) & tok(b)
    if not pool: pool = tok(b)
    return sorted(pool)[:n]

def score_badge(s: float) -> str:
    cls = "badge-high" if s >= 70 else ("badge-mid" if s >= 50 else "badge-low")
    return f'<span class="{cls}">{s}% match</span>'

def get_my_row():
    u  = st.session_state.user
    df = startups if u["role"] == "Startup" else investors
    return df[df["ID"] == u["linked_id"]].iloc[0]

def get_entity_row(eid: str, role: str):
    df   = startups if role == "Startup" else investors
    rows = df[df["ID"] == eid]
    return rows.iloc[0] if not rows.empty else None

def toggle_bookmark(entity_id: str):
    u  = dict(st.session_state.user)
    bm = u.get("bookmarks", [])
    if entity_id in bm: bm.remove(entity_id)
    else:               bm.append(entity_id)
    u["bookmarks"] = bm
    update_user(u)

def nav(page: str):
    st.session_state.page         = page
    st.session_state.drilldown_id = None
    st.rerun()

# ── Session defaults ───────────────────────────────────────────────────────────
DEFAULTS = dict(
    authenticated=False, user=None, page="home",
    auth_view="login", drilldown_id=None,
    drilldown_score=None, drilldown_role=None,
)
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────────────────────────────────────
def auth_header():
    _, mid, _ = st.columns([1, 1.6, 1])
    with mid:
        st.markdown('<div class="auth-logo">StartMatch</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-tagline">AI-powered startup and investor matching</div>',
                    unsafe_allow_html=True)
    return mid

def login_page():
    mid = auth_header()
    with mid:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Sign in")
        username = st.text_input("Username", key="li_user", placeholder="Your username")
        password = st.text_input("Password", type="password", key="li_pw",
                                 placeholder="Your password")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Sign In", use_container_width=True):
                u = get_user(username.strip())
                if u and u["password"] == hash_pw(password):
                    st.session_state.authenticated = True
                    st.session_state.user          = u
                    st.session_state.page          = "home"
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")
        with c2:
            if st.button("Create Account", use_container_width=True):
                st.session_state.auth_view = "signup"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align:center;color:#999;font-size:.76rem;margin-top:14px'>"
            "By continuing you agree to StartMatch Terms of Service.</p>",
            unsafe_allow_html=True,
        )

def signup_page():
    mid = auth_header()
    with mid:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Create your account")

        role      = st.radio("I am a", ["Startup", "Investor"], horizontal=True, key="su_role")
        df        = startups if role == "Startup" else investors
        taken     = {u["linked_id"] for u in load_users()}
        available = df[~df["ID"].isin(taken)]

        if available.empty:
            st.warning("All profiles for this role are already claimed.")
        else:
            entity    = st.selectbox(f"Select your {role.lower()} profile",
                                     available["Name"].tolist(), key="su_entity")
            entity_id = available[available["Name"] == entity]["ID"].values[0]
            username  = st.text_input("Username", key="su_user", placeholder="Choose a username")
            pw        = st.text_input("Password", type="password", key="su_pw",
                                      placeholder="At least 6 characters")
            pw2       = st.text_input("Confirm password", type="password", key="su_pw2")

            if st.button("Register", use_container_width=True):
                if not username.strip() or not pw:
                    st.error("All fields are required.")
                elif len(pw) < 6:
                    st.error("Password must be at least 6 characters.")
                elif pw != pw2:
                    st.error("Passwords do not match.")
                elif get_user(username.strip()):
                    st.error("Username already taken. Try another.")
                else:
                    users = load_users()
                    users.append(dict(
                        username=username.strip(), password=hash_pw(pw),
                        role=role, linked_id=entity_id,
                        custom_text="", bookmarks=[],
                    ))
                    save_users(users)
                    st.success("Account created. Sign in below.")
                    st.session_state.auth_view = "login"
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Back to Sign In"):
            st.session_state.auth_view = "login"
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def sidebar():
    u   = st.session_state.user
    row = get_my_row()
    with st.sidebar:
        st.markdown(f"### {row['Name']}")
        st.caption(f"{u['role']}  ·  @{u['username']}")
        st.markdown("---")
        for key, label in [
            ("home",         "Home"),
            ("profile",      "My Profile"),
            ("edit_profile", "Edit Profile"),
            ("matches",      "My Matches"),
            ("insights",     "Market Insights"),
        ]:
            if st.button(label, use_container_width=True, key=f"sb_{key}"):
                nav(key)
        if u["role"] == "Investor":
            bm = u.get("bookmarks", [])
            st.markdown("---")
            st.caption(f"Saved startups: {len(bm)}")
        st.markdown("---")
        if st.button("Sign Out", use_container_width=True):
            st.session_state.update(DEFAULTS)
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  PAGES
# ─────────────────────────────────────────────────────────────────────────────
def home_page():
    u       = st.session_state.user
    row     = get_my_row()
    matches = compute_matches(u)
    best    = matches[0][1] if matches else 0.0

    st.markdown(f"# Welcome back, {row['Name']}")
    st.markdown(
        f"<p style='color:#666;margin-top:-10px;font-size:.93rem'>"
        f"{u['role']}  ·  @{u['username']}</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Startups on Platform",  len(startups))
    c2.metric("Investors on Platform", len(investors))
    c3.metric("Your Best Match",       f"{best}%")
    c4.metric("Your Sector",           row.get("Sector", "—"))

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    cards = [
        ("col1", "home_p",  "profile",   "&#128100;", "My Profile",
         "View your public profile and current pitch."),
        ("col2", "home_m",  "matches",   "&#127919;", "My Matches",
         "Your top 5 AI-ranked matches based on semantic fit."),
        ("col3", "home_i",  "insights",  "&#128200;", "Market Insights",
         "Explore investor trends and the startup landscape."),
    ]
    for col_obj, btn_key, dest, icon, title, desc in [
        (col1, "home_p", "profile",  "&#128100;", "My Profile",       "View your public profile and current pitch."),
        (col2, "home_m", "matches",  "&#127919;", "My Matches",        "Top 5 AI-ranked matches based on semantic fit."),
        (col3, "home_i", "insights", "&#128200;", "Market Insights",   "Explore investor trends and startup landscape."),
    ]:
        with col_obj:
            st.markdown(f"""
            <div class="action-card">
              <div class="ac-icon">{icon}</div>
              <div class="ac-title">{title}</div>
              <div class="ac-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Open {title}", use_container_width=True, key=btn_key):
                nav(dest)

    st.markdown("---")
    st.markdown("### Your Top Match")
    if matches:
        m_row, score, m_role = matches[0]
        firm_html = f" &mdash; {m_row['Firm']}" if "Firm" in m_row.index else ""
        excerpt   = m_row.get("Thesis", m_row.get("Description", ""))[:180]
        c_i, c_b  = st.columns([5, 1])
        with c_i:
            st.markdown(f"""
            <div class="match-card">
              <strong style="font-size:1.05rem">{m_row['Name']}</strong>{firm_html}
              &nbsp;&nbsp;{score_badge(score)}
              <br><small style="color:#666;display:block;margin-top:5px">
                {m_row.get('Sector','—')} &nbsp;&middot;&nbsp; {m_row.get('Location','—')}
              </small>
              <small style="color:#888;display:block;margin-top:6px">{excerpt}&hellip;</small>
            </div>""", unsafe_allow_html=True)
        with c_b:
            st.markdown("<div style='margin-top:22px'>", unsafe_allow_html=True)
            if st.button("View", key="home_top_view"):
                st.session_state.drilldown_id    = m_row["ID"]
                st.session_state.drilldown_score = score
                st.session_state.drilldown_role  = m_role
                st.session_state.page            = "drilldown"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def profile_page():
    u   = st.session_state.user
    row = get_my_row()
    is_edited = bool(u.get("custom_text"))

    st.markdown(f"# {row['Name']}")
    st.markdown(f"<p style='color:#666;margin-top:-10px'>{u['role']}</p>", unsafe_allow_html=True)
    if is_edited:
        st.info("Custom pitch is active and being used for match scoring.")
    st.markdown("---")

    if u["role"] == "Startup":
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Sector",   row["Sector"])
        c2.metric("Stage",    row["Stage"])
        c3.metric("Location", row["Location"])
        rev = row["Revenue"]
        c4.metric("Revenue", f"${rev:,.0f}" if rev > 0 else "Pre-revenue")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Founder</span>', unsafe_allow_html=True)
        st.markdown(f"<p style='margin:0 0 16px'>{row['Founder']}</p>", unsafe_allow_html=True)
        st.markdown('<span class="section-label">About / Pitch</span>', unsafe_allow_html=True)
        st.write(get_current_text(u))
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Firm",        row["Firm"])
        c2.metric("Sector",      row["Sector"])
        c3.metric("Location",    row["Location"])
        c4.metric("Ticket Size", f"${row['TicketSize']:,.0f}")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Investment Stages</span>', unsafe_allow_html=True)
        pills = " ".join(f'<span class="pill">{s.strip()}</span>' for s in row["Stage"].split(","))
        st.markdown(f"<p style='margin:0 0 16px'>{pills}</p>", unsafe_allow_html=True)
        st.markdown('<span class="section-label">Investment Thesis</span>', unsafe_allow_html=True)
        st.write(get_current_text(u))
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Edit Profile"):
        nav("edit_profile")


def edit_profile_page():
    u       = st.session_state.user
    row     = get_my_row()
    field   = "Description" if u["role"] == "Startup" else "Thesis"
    original = row[field]

    st.markdown("# Edit Profile")
    st.markdown("---")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        f'<span class="section-label">Your {field}</span>'
        f'<p style="color:#666;font-size:.85rem;margin-bottom:12px">'
        f'This text is used in real-time for match scoring.</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<span class="section-label">Original (from data)</span>', unsafe_allow_html=True)
    st.markdown(
        f"<blockquote style='border-left:3px solid #e0ddd6;padding:8px 14px;"
        f"color:#888;margin:0 0 16px;font-size:.88rem'>{original}</blockquote>",
        unsafe_allow_html=True,
    )
    current  = u.get("custom_text") or original
    new_text = st.text_area(f"Custom {field}", value=current, height=150, key="edit_ta")
    st.caption(f"{len(new_text)} characters")
    st.markdown('</div>', unsafe_allow_html=True)

    c1, c2, _ = st.columns([1.2, 1.4, 4])
    with c1:
        if st.button("Save Changes", use_container_width=True):
            updated = dict(u)
            updated["custom_text"] = new_text.strip()
            update_user(updated)
            st.success("Saved. Match scores are now updated.")
    with c2:
        if st.button("Reset to Original", use_container_width=True):
            updated = dict(u)
            updated["custom_text"] = ""
            update_user(updated)
            st.success("Reset to original.")
            st.rerun()


def matches_page():
    u         = st.session_state.user
    matches   = compute_matches(u)
    bookmarks = u.get("bookmarks", [])
    target    = "Investors" if u["role"] == "Startup" else "Startups"

    st.markdown(f"# Top 5 Matching {target}")
    st.markdown(
        "<p style='color:#666;margin-top:-10px;font-size:.88rem'>"
        "Scores are computed in real-time from your current profile text. "
        "Hover a card to preview their pitch.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Saved startups banner (investors only)
    if u["role"] == "Investor" and bookmarks:
        st.markdown("### Saved Startups")
        for eid in bookmarks:
            brow = get_entity_row(eid, "Startup")
            if brow is None: continue
            bc, bb = st.columns([5, 1])
            with bc:
                st.markdown(f"""
                <div class="saved-strip">
                  <strong>{brow['Name']}</strong>
                  <span style="color:#555;font-size:.85rem">
                    &nbsp;&middot;&nbsp; {brow['Sector']}
                    &nbsp;&middot;&nbsp; {brow['Stage']}
                    &nbsp;&middot;&nbsp; {brow['Location']}
                  </span>
                </div>""", unsafe_allow_html=True)
            with bb:
                if st.button("View", key=f"bm_v_{eid}"):
                    st.session_state.drilldown_id    = eid
                    st.session_state.drilldown_score = None
                    st.session_state.drilldown_role  = "Startup"
                    st.session_state.page            = "drilldown"
                    st.rerun()
        st.markdown("---")

    st.markdown("### AI-Ranked Matches")
    for rank, (m_row, score, m_role) in enumerate(matches, 1):
        excerpt   = m_row.get("Thesis", m_row.get("Description", ""))[:170]
        firm_html = f" &mdash; {m_row['Firm']}" if "Firm" in m_row.index else ""
        is_bm     = m_row["ID"] in bookmarks

        if u["role"] == "Investor":
            c_card, c_view, c_bm = st.columns([6, 1, 1])
        else:
            _cols = st.columns([6, 1])
            c_card, c_view, c_bm = _cols[0], _cols[1], None

        with c_card:
            st.markdown(f"""
            <div class="has-tip">
              <div class="match-card">
                <span style="color:#888;font-size:.73rem;font-weight:700">#{rank}</span>
                &nbsp;&nbsp;
                <strong style="font-size:1.04rem">{m_row['Name']}</strong>{firm_html}
                &nbsp;&nbsp;{score_badge(score)}
                <br>
                <span style="color:#555;font-size:.84rem;display:block;margin-top:7px">
                  {m_row.get('Sector','—')}
                  &nbsp;&middot;&nbsp; {m_row.get('Location','—')}
                  &nbsp;&middot;&nbsp; {m_row.get('Stage','—')}
                </span>
              </div>
              <div class="tip-text">{excerpt}&hellip;</div>
            </div>""", unsafe_allow_html=True)

        with c_view:
            st.markdown("<div style='margin-top:22px'>", unsafe_allow_html=True)
            if st.button("View", key=f"v_{m_row['ID']}_{rank}"):
                st.session_state.drilldown_id    = m_row["ID"]
                st.session_state.drilldown_score = score
                st.session_state.drilldown_role  = m_role
                st.session_state.page            = "drilldown"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        if u["role"] == "Investor" and c_bm is not None:
            with c_bm:
                st.markdown("<div style='margin-top:22px'>", unsafe_allow_html=True)
                if st.button("Saved" if is_bm else "Save",
                             key=f"bm_{m_row['ID']}_{rank}"):
                    toggle_bookmark(m_row["ID"])
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


def drilldown_page():
    u      = st.session_state.user
    my_row = get_my_row()
    role   = st.session_state.drilldown_role
    score  = st.session_state.drilldown_score
    entity = get_entity_row(st.session_state.drilldown_id, role)

    if entity is None:
        st.error("Profile not found.")
        if st.button("Back"): nav("matches")
        return

    if st.button("Back to Matches"):
        nav("matches")

    st.markdown(f"# {entity['Name']}")
    if score is not None:
        st.markdown(score_badge(score), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    if role == "Investor":
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Firm",        entity["Firm"])
        c2.metric("Sector",      entity["Sector"])
        c3.metric("Location",    entity["Location"])
        c4.metric("Ticket Size", f"${entity['TicketSize']:,.0f}")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Investment Stages</span>', unsafe_allow_html=True)
        pills = " ".join(f'<span class="pill">{s.strip()}</span>'
                         for s in entity["Stage"].split(","))
        st.markdown(f"<p style='margin:0 0 16px'>{pills}</p>", unsafe_allow_html=True)
        st.markdown('<span class="section-label">Investment Thesis</span>', unsafe_allow_html=True)
        st.write(entity["Thesis"])
        st.markdown('</div>', unsafe_allow_html=True)
        their_text = entity["Thesis"]
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Sector",   entity["Sector"])
        c2.metric("Stage",    entity["Stage"])
        c3.metric("Location", entity["Location"])
        rev = entity["Revenue"]
        c4.metric("Revenue", f"${rev:,.0f}" if rev > 0 else "Pre-revenue")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Founder</span>', unsafe_allow_html=True)
        st.markdown(f"<p style='margin:0 0 16px'>{entity['Founder']}</p>", unsafe_allow_html=True)
        st.markdown('<span class="section-label">Description</span>', unsafe_allow_html=True)
        st.write(entity["Description"])
        st.markdown('</div>', unsafe_allow_html=True)
        their_text = entity["Description"]

    # Why this match
    if score is not None:
        kw = shared_keywords(get_current_text(u), their_text)
        if kw:
            tags = " ".join(f'<span class="tag">{k}</span>' for k in kw)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<span class="section-label">Why this match?</span>', unsafe_allow_html=True)
            st.markdown(
                f"<p style='color:#555;margin-bottom:10px;font-size:.9rem'>"
                f"Semantic overlap across these themes:</p>{tags}",
                unsafe_allow_html=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)

    # Reach out
    my_name, their_name = my_row["Name"], entity["Name"]
    if role == "Investor":
        subj = f"Partnership Inquiry from {my_name}"
        body = (
            f"Hi {their_name},%0A%0A"
            f"I came across your investment profile on StartMatch and see strong alignment with {my_name}.%0A%0A"
            f"We are a {my_row['Stage']} company in the {my_row['Sector']} space. "
            f"I'd love a brief introductory call to explore fit.%0A%0A"
            f"Best regards,%0A{my_name}"
        )
    else:
        subj = f"Investment Inquiry — {their_name}"
        body = (
            f"Hi {their_name} team,%0A%0A"
            f"Our thesis aligns closely with what {their_name} is building in the "
            f"{entity['Sector']} space. Would love to connect.%0A%0A"
            f"Best regards,%0A{my_name} — {my_row['Firm']}"
        )
    mailto = f"mailto:?subject={subj.replace(' ','%20')}&body={body}"

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="section-label">Reach Out</span>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:#555;font-size:.9rem;margin-bottom:14px'>"
        f"Pre-drafted introduction to {their_name}. Opens in your email client.</p>",
        unsafe_allow_html=True,
    )
    st.link_button("Send Introduction Email", mailto)
    st.markdown('</div>', unsafe_allow_html=True)


def insights_page():
    u = st.session_state.user
    st.markdown("# Market Insights")
    st.markdown("---")

    with st.expander("Filters", expanded=False):
        fc1, fc2 = st.columns(2)
        with fc1:
            all_sec = sorted(set(startups["Sector"].tolist() + investors["Sector"].tolist()))
            sel_sec = st.multiselect("Sectors", all_sec, key="f_sec")
        with fc2:
            all_stg = sorted(startups["Stage"].unique())
            sel_stg = st.multiselect("Startup Stages", all_stg, key="f_stg")

    sf = startups.copy()
    iv = investors.copy()
    if sel_sec:
        sf = sf[sf["Sector"].isin(sel_sec)]
        iv = iv[iv["Sector"].isin(sel_sec)]
    if sel_stg:
        sf = sf[sf["Stage"].isin(sel_stg)]

    PAL = [[0,"#bdd7f5"],[1,"#0a66c2"]]
    LAY = dict(plot_bgcolor="#fff", paper_bgcolor="#fff", font_color="#1d2226",
               showlegend=False, margin=dict(t=50,b=24,l=10,r=10))
    PIE_COLS = ["#0a66c2","#57a4f0","#003d82","#bdd7f5","#6fb3ff"]

    def bar(df, x, y, title):
        d = df[x].value_counts().reset_index(); d.columns = [x, y]
        f = px.bar(d, x=x, y=y, title=title, color=y, color_continuous_scale=PAL)
        f.update_layout(**LAY); return f

    def bar_agg(df, grp, val, agg, title):
        d = df.groupby(grp)[val].agg(agg).reset_index(); d.columns = [grp, val]
        f = px.bar(d, x=grp, y=val, title=title, color=val, color_continuous_scale=PAL)
        f.update_layout(**LAY); return f

    def pie(df, names, title):
        d = df[names].value_counts().reset_index(); d.columns = [names, "Count"]
        f = px.pie(d, names=names, values="Count", title=title, color_discrete_sequence=PIE_COLS)
        f.update_layout(paper_bgcolor="#fff", font_color="#1d2226",
                        margin=dict(t=50,b=10,l=10,r=10))
        return f

    # Role-framed: most relevant charts first
    if u["role"] == "Startup":
        st.markdown("### Investor Landscape")
        c1, c2 = st.columns(2)
        c1.plotly_chart(bar(iv, "Sector", "Investors", "Investors by Sector"), use_container_width=True)
        c2.plotly_chart(bar_agg(iv, "Sector", "TicketSize", "mean", "Avg Ticket by Sector"), use_container_width=True)

        st.markdown("### Startup Landscape")
        c3, c4 = st.columns(2)
        c3.plotly_chart(pie(sf, "Stage", "Stage Distribution"), use_container_width=True)
        c4.plotly_chart(bar(sf, "Location", "Startups", "Startups by Location"), use_container_width=True)
    else:
        st.markdown("### Startup Landscape")
        c1, c2 = st.columns(2)
        c1.plotly_chart(bar(sf, "Sector", "Startups", "Startups by Sector"), use_container_width=True)
        c2.plotly_chart(pie(sf, "Stage", "Stage Distribution"), use_container_width=True)

        c3, c4 = st.columns(2)
        c3.plotly_chart(bar_agg(sf, "Sector", "Revenue", "mean", "Avg Revenue by Sector"), use_container_width=True)
        c4.plotly_chart(bar(sf, "Location", "Startups", "Startups by Location"), use_container_width=True)

        st.markdown("### Investor Landscape")
        c5, c6 = st.columns(2)
        c5.plotly_chart(bar(iv, "Sector", "Investors", "Investors by Sector"), use_container_width=True)
        c6.plotly_chart(bar_agg(iv, "Sector", "TicketSize", "mean", "Avg Ticket by Sector"), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    if st.session_state.auth_view == "signup":
        signup_page()
    else:
        login_page()
else:
    sidebar()
    {
        "home":         home_page,
        "profile":      profile_page,
        "edit_profile": edit_profile_page,
        "matches":      matches_page,
        "drilldown":    drilldown_page,
        "insights":     insights_page,
    }.get(st.session_state.page, home_page)()