import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(page_title="StartMatch", page_icon="🚀", layout="wide")

# ── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    startups  = pd.read_csv("data/startups.csv")
    investors = pd.read_csv("data/investors.csv")
    return startups, investors

# ── Load Model (cached so it only downloads once) ────────────────────────────
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

# ── Embedding helpers ─────────────────────────────────────────────────────────
@st.cache_data
def embed_texts(texts: list[str]) -> np.ndarray:
    model = load_model()
    return model.encode(texts, convert_to_numpy=True)

def top5_matches(query_emb, corpus_embs, corpus_df, label_col):
    sims = cosine_similarity([query_emb], corpus_embs)[0]
    idx  = np.argsort(sims)[::-1][:5]
    results = corpus_df.iloc[idx].copy()
    results["Confidence Score"] = (sims[idx] * 100).round(1)
    return results

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .metric-card{background:#1e1e2e;border-radius:12px;padding:16px 20px;margin-bottom:10px;}
  .match-card {background:#2a2a3d;border-left:4px solid #7c3aed;border-radius:8px;
               padding:14px 18px;margin-bottom:10px;}
  .score-badge{background:#7c3aed;color:#fff;border-radius:20px;padding:2px 10px;
               font-weight:700;font-size:.85rem;}
  h1{color:#a78bfa;}
</style>
""", unsafe_allow_html=True)

# ── Load everything ───────────────────────────────────────────────────────────
startups, investors = load_data()
startup_embs  = embed_texts(startups["Description"].tolist())
investor_embs = embed_texts(investors["Thesis"].tolist())

# ── Sidebar: Role & Login ─────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/rocket.png", width=60)
    st.title("StartMatch 🚀")
    st.markdown("---")

    role = st.radio("I am a …", ["Startup", "Investor"], horizontal=True)

    if role == "Startup":
        names = startups["Name"].tolist()
        selected_name = st.selectbox("Select your startup", names)
        user_row = startups[startups["Name"] == selected_name].iloc[0]
    else:
        names = investors["Name"].tolist()
        selected_name = st.selectbox("Select your profile", names)
        user_row = investors[investors["Name"] == selected_name].iloc[0]

    st.markdown("---")
    st.caption("Powered by sentence-transformers · all-MiniLM-L6-v2")

# ── Main Layout ───────────────────────────────────────────────────────────────
st.title("StartMatch — AI Investor × Startup Connector")
tab1, tab2, tab3 = st.tabs(["👤 My Profile", "🎯 Top 5 Matches", "📊 Market Insights"])

# ── TAB 1: Profile ────────────────────────────────────────────────────────────
with tab1:
    st.subheader(f"{'🏢' if role == 'Startup' else '💼'} {user_row['Name']}")
    cols = st.columns(3)

    if role == "Startup":
        cols[0].metric("Sector",   user_row["Sector"])
        cols[1].metric("Stage",    user_row["Stage"])
        cols[2].metric("Location", user_row["Location"])
        st.markdown("**Founder**"); st.write(user_row["Founder"])
        st.markdown("**Description**"); st.info(user_row["Description"])
        rev = user_row["Revenue"]
        st.metric("Annual Revenue", f"${rev:,.0f}" if rev > 0 else "Pre-revenue")
    else:
        cols[0].metric("Firm",     user_row["Firm"])
        cols[1].metric("Sector",   user_row["Sector"])
        cols[2].metric("Location", user_row["Location"])
        st.markdown("**Investment Stages**"); st.write(user_row["Stage"])
        st.markdown("**Investment Thesis**"); st.info(user_row["Thesis"])
        st.metric("Ticket Size", f"${user_row['TicketSize']:,.0f}")

# ── TAB 2: Matches ────────────────────────────────────────────────────────────
with tab2:
    if role == "Startup":
        st.subheader(f"Top 5 Investors for {user_row['Name']}")
        idx = startups[startups["Name"] == user_row["Name"]].index[0]
        matches = top5_matches(startup_embs[idx], investor_embs, investors, "Name")
        for _, m in matches.iterrows():
            score_color = "#22c55e" if m["Confidence Score"] >= 70 else \
                          "#f59e0b" if m["Confidence Score"] >= 50 else "#ef4444"
            st.markdown(f"""
            <div class="match-card">
              <b>{m['Name']}</b> — {m['Firm']}
              &nbsp;<span class="score-badge" style="background:{score_color}">
                {m['Confidence Score']}%
              </span>
              <br><small>📍 {m['Location']} · Ticket: ${m['TicketSize']:,} · Stages: {m['Stage']}</small>
              <br><small style="color:#a0a0b0">{m['Thesis'][:160]}…</small>
            </div>""", unsafe_allow_html=True)
    else:
        st.subheader(f"Top 5 Startups for {user_row['Name']}")
        idx = investors[investors["Name"] == user_row["Name"]].index[0]
        matches = top5_matches(investor_embs[idx], startup_embs, startups, "Name")
        for _, m in matches.iterrows():
            score_color = "#22c55e" if m["Confidence Score"] >= 70 else \
                          "#f59e0b" if m["Confidence Score"] >= 50 else "#ef4444"
            rev_str = f"${m['Revenue']:,.0f}" if m["Revenue"] > 0 else "Pre-revenue"
            st.markdown(f"""
            <div class="match-card">
              <b>{m['Name']}</b> — {m['Sector']}
              &nbsp;<span class="score-badge" style="background:{score_color}">
                {m['Confidence Score']}%
              </span>
              <br><small>📍 {m['Location']} · {m['Stage']} · Revenue: {rev_str}</small>
              <br><small style="color:#a0a0b0">{m['Description'][:160]}…</small>
            </div>""", unsafe_allow_html=True)

# ── TAB 3: Insights ───────────────────────────────────────────────────────────
with tab3:
    st.subheader("📊 Investor Interest by Sector")
    sector_counts = investors["Sector"].value_counts().reset_index()
    sector_counts.columns = ["Sector", "Number of Investors"]
    fig1 = px.bar(
        sector_counts, x="Sector", y="Number of Investors",
        color="Number of Investors", color_continuous_scale="Purples",
        title="How many investors focus on each sector?"
    )
    fig1.update_layout(plot_bgcolor="#1e1e2e", paper_bgcolor="#1e1e2e",
                       font_color="#e2e8f0", showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Startup Stage Distribution")
        stage_counts = startups["Stage"].value_counts().reset_index()
        stage_counts.columns = ["Stage", "Count"]
        fig2 = px.pie(stage_counts, names="Stage", values="Count",
                      color_discrete_sequence=px.colors.sequential.Purpor)
        fig2.update_layout(plot_bgcolor="#1e1e2e", paper_bgcolor="#1e1e2e",
                           font_color="#e2e8f0")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("Average Investor Ticket by Sector")
        ticket_avg = investors.groupby("Sector")["TicketSize"].mean().reset_index()
        ticket_avg.columns = ["Sector", "Avg Ticket ($)"]
        fig3 = px.bar(ticket_avg, x="Sector", y="Avg Ticket ($)",
                      color="Avg Ticket ($)", color_continuous_scale="Teal")
        fig3.update_layout(plot_bgcolor="#1e1e2e", paper_bgcolor="#1e1e2e",
                           font_color="#e2e8f0", showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("🗺️ Startup Geography")
    loc_counts = startups["Location"].value_counts().reset_index()
    loc_counts.columns = ["Location", "Count"]
    fig4 = px.bar(loc_counts, x="Location", y="Count",
                  color="Count", color_continuous_scale="Magenta")
    fig4.update_layout(plot_bgcolor="#1e1e2e", paper_bgcolor="#1e1e2e",
                       font_color="#e2e8f0", showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)