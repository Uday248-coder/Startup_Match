# StartMatch — Architecture

## What This Is

StartMatch is a full-stack matchmaking platform that connects startups with investors using AI-powered semantic matching. The idea is simple: instead of keyword filters or manual browsing, both sides fill out a profile and the system figures out who actually fits who — using real NLP, not just "you're both in FinTech."

This document covers how the app is structured, how the matching works under the hood, what's in the database, and where things are headed.

---

## Project Structure

```
startupmatch/
├── app.py                  # Everything — single-file Streamlit app
├── data/
│   ├── db.sqlite           # SQLite database (users, startups, investors)
│   ├── startups.csv        # Seed data for market stats charts
│   └── investors.csv       # Seed data for market stats charts
└── requirements.txt
```

This is intentionally a single-file architecture right now. The whole app — routing, database, UI, matching logic — lives in `app.py`. It's not the most scalable pattern long-term, but it's clean for an MVP and easy to reason about. When the time comes to split it up, the logical seams are already there.

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| UI + Routing | Streamlit | Fast iteration, Python-native, no frontend build step |
| Database | SQLite (via `sqlite3`) | Zero config, file-based, easy to migrate later |
| AI Matching | `sentence-transformers` (`all-MiniLM-L6-v2`) | Lightweight, runs locally, good enough for semantic similarity |
| Similarity | `sklearn.metrics.pairwise.cosine_similarity` | Standard, fast |
| Charts | Plotly (`graph_objects`) | Full control over styling in dark theme |
| Data | Pandas | Seed data loading and market stats aggregation |
| Auth | SHA-256 password hashing + Streamlit session state | Simple, stateless |

---

## Application Layers

The app is organized into logical layers even though they all live in one file:

```
┌─────────────────────────────────────────────────┐
│                   Router                         │
│  (session state decides what page renders)       │
├─────────────────────────────────────────────────┤
│                 Page Functions                   │
│  login_page / signup_page / dashboard_tab /      │
│  profile_tab / matches_tab / stats_tab /         │
│  drilldown_page / edit_profile_page              │
├─────────────────────────────────────────────────┤
│              Matching Engine                     │
│  compute_matches()  ←  unfiltered top 5          │
│  compute_filtered_matches()  ←  with field filters│
│  radar_scores()  ←  per-dimension breakdown      │
│  gen_summary() / gen_red_flags() / gen_next_steps│
├─────────────────────────────────────────────────┤
│               AI / NLP Layer                     │
│  SentenceTransformer (cached via @st.cache_resource) │
│  emb() / embs()  →  cosine_similarity            │
├─────────────────────────────────────────────────┤
│               Data Layer (CRUD)                  │
│  SQLite via get_con() + qry()                    │
│  ins_startup / ins_investor / upd_* / get_*      │
└─────────────────────────────────────────────────┘
```

---

## Database Schema

Three tables. Simple.

### `startups`

| Column | Type | Notes |
|---|---|---|
| `id` | TEXT PK | UUID |
| `name` | TEXT | Company name |
| `founder` | TEXT | |
| `sector` | TEXT | One of 15 predefined sectors |
| `stage` | TEXT | Pre-Seed → Series C+ |
| `location` | TEXT | City |
| `description` | TEXT | Main input for AI matching |
| `revenue` | REAL | Annual revenue |
| `website` | TEXT | |
| `team_size` | INTEGER | |
| `linkedin` | TEXT | |
| `target_market` | TEXT | |
| `business_model` | TEXT | B2B, B2C, SaaS, etc. |
| `country` | TEXT | Country of incorporation |
| `mrr` | REAL | Monthly recurring revenue |
| `growth_rate` | REAL | MoM growth % |
| `runway` | INTEGER | Months of runway |
| `burn_rate` | REAL | Monthly burn |

### `investors`

| Column | Type | Notes |
|---|---|---|
| `id` | TEXT PK | UUID |
| `name` | TEXT | |
| `firm` | TEXT | Fund name |
| `sector` | TEXT | Primary focus sector |
| `stage` | TEXT | Comma-separated list e.g. "Seed, Series A" |
| `location` | TEXT | City |
| `thesis` | TEXT | Main input for AI matching |
| `ticket_size` | REAL | Typical check size |
| `website` | TEXT | |
| `fund_size` | REAL | |
| `portfolio_count` | INTEGER | |
| `notable_investments` | TEXT | Comma-separated company names |
| `geo_focus` | TEXT | Comma-separated regions |
| `co_invest_pref` | TEXT | Lead / Follow / Either |
| `decision_timeline` | TEXT | |
| `business_model_pref` | TEXT | |
| `linkedin` | TEXT | |
| `investments_per_year` | INTEGER | |

### `users`

| Column | Type | Notes |
|---|---|---|
| `username` | TEXT PK | |
| `password` | TEXT | SHA-256 hash |
| `role` | TEXT | "Startup" or "Investor" |
| `entity_id` | TEXT | FK → `startups.id` or `investors.id` |

The `users` table is the auth layer. It links credentials to a profile. One user = one entity. No admin role yet.

---

## Matching Engine

This is the core of the product. There are two matching functions:

### `compute_matches(user)` — Unfiltered

Runs against the full registered opposite side. Returns top 5 by cosine similarity.

```
1. Load my profile (startup or investor)
2. Load all registered counterparts
3. Build text:
     - startup  → description
     - investor → thesis
4. Encode all texts with SentenceTransformer
5. cosine_similarity(my_embedding, all_embeddings)
6. argsort descending → top 5
```

### `compute_filtered_matches(user, f_sector, f_stage, f_location, f_biz_model)` — Filtered

Same as above but pre-filters the corpus before embedding. Returns `(results, total_before, total_after)` so the UI can show "3 of 12 investors match your filters."

Filter logic by role:

**If I'm a Startup, filtering Investors:**
- `f_sector` → `investor.sector == f_sector`
- `f_stage` → `f_stage in investor.stage.split(',')`
- `f_location` → substring match on `investor.location`
- `f_biz_model` → `investor.business_model_pref in ('Any', f_biz_model)`

**If I'm an Investor, filtering Startups:**
- `f_sector` → `startup.sector == f_sector`
- `f_stage` → `startup.stage == f_stage`
- `f_location` → substring match on `startup.location`
- `f_biz_model` → `startup.business_model == f_biz_model`

### `radar_scores(startup, investor, nlp_score)` — Per-Dimension Breakdown

Used in the drilldown page to power the radar chart. Five dimensions:

```
Total Score = 0.40 × Semantic (cosine similarity × 100)
            + 0.25 × Sector   (100 if match, else 15)
            + 0.20 × Stage    (100 if in list, else 20)
            + 0.10 × Location (100 if same city, else 35)
            + 0.05 × Scale    (ticket size vs stage norms)
```

Stage → ticket size ranges used for Scale scoring:

| Stage | Expected Ticket Range |
|---|---|
| Pre-Seed | $0 – $500K |
| Seed | $100K – $2M |
| Series A | $1M – $10M |
| Series B | $5M – $30M |
| Series C+ | $20M – $200M |

---

## AI Model

Using `all-MiniLM-L6-v2` from `sentence-transformers`. It's a 22M parameter model that maps sentences to 384-dimensional embeddings.

Why this model:
- Small enough to run locally without a GPU
- Fast enough that matching doesn't feel slow in Streamlit
- Good enough semantic quality for startup/investor thesis matching
- Cached with `@st.cache_resource` so it only loads once per session

The model is never fine-tuned — it runs zero-shot. The thesis and description fields are the only text inputs. Better descriptions → better match scores. This is explained to users in the signup flow.

```python
@st.cache_resource(show_spinner="Loading AI model…")
def get_model():
    return SentenceTransformer("all-MiniLM-L6-v2")
```

---

## Auth Flow

No JWT, no OAuth. Session-state based auth:

```
1. User enters username + password
2. SHA-256 hash of password compared to stored hash
3. On success → st.session_state.authenticated = True
                 st.session_state.user = row (dict from users table)
4. All pages check st.session_state.authenticated before rendering
5. Sign Out → st.session_state.update(DEFS) → rerun
```

Passwords are hashed before storage. No plaintext anywhere. Good enough for an MVP — would need proper bcrypt + salting before any real production deployment.

---

## Page Routing

Streamlit doesn't have a real router so routing is handled manually via session state flags:

```
authenticated == False  →  login_page() or signup_page()

authenticated == True:
  edit_mode == True         →  edit_profile_page()
  drilldown_id is not None  →  drilldown_page()
  else                      →  tabbed layout:
                                 Dashboard / Profile / Matches / Market
```

The signup flow has its own internal state machine using `signup_step` (1, 2, 3) and `signup_data` (accumulates across steps).

---

## UI Architecture

Pure CSS dark theme. No external component library. Everything is styled via a large `st.markdown("""<style>...</style>""")` block injected at startup.

Design decisions worth noting:
- Sidebar is fully hidden via CSS (`display:none`) — not just collapsed
- All custom cards use `st.container(border=True)` as the base and get styled via the global CSS
- SVG score rings are generated programmatically in Python and injected as HTML
- Sector colors are consistent across all components via `SECTOR_COLORS` dict
- The header renders outside the tab system and is shared across all logged-in pages

---

## Data Flow — New User Registration

```
signup_page (step 1) → collect role, name, sector, stage, location
         ↓
signup_page (step 2) → collect description/thesis, website, linkedin, biz model
         ↓
signup_page (step 3) → collect financials + credentials
         ↓
ins_startup() or ins_investor()
  → INSERT INTO startups/investors
  → INSERT INTO users (hashed password)
         ↓
st.session_state.auth_view = "login"
→ user redirected to sign in
```

---

## Data Flow — Match Computation

```
User lands on Matches tab
         ↓
compute_filtered_matches() or compute_matches()
         ↓
get_me() → load my profile from DB
registered_opposite() → load all counterparts who have accounts
         ↓
Apply field filters (if any)
         ↓
emb(my_text) → 384-dim vector
embs([counterpart texts]) → matrix
cosine_similarity → scores array
argsort → top 5
         ↓
Render match cards with score rings
         ↓
User clicks "View" → drilldown_id set → rerun
         ↓
drilldown_page() renders:
  - radar_scores() → 5-axis breakdown
  - gen_summary() → rule-based text summary
  - gen_red_flags() → mismatch warnings
  - gen_next_steps() → actionable advice
  - kw_overlap() → shared keyword tags
```

---

## Current Status

| Feature | Status |
|---|---|
| Streamlit single-file architecture | ✅ Done |
| SQLite persistence | ✅ Done |
| Multi-step signup (startup + investor) | ✅ Done |
| SHA-256 auth | ✅ Done |
| Semantic matching (MiniLM) | ✅ Done |
| Radar chart score breakdown | ✅ Done |
| AI-generated match summaries | ✅ Done (rule-based) |
| Red flags + next steps | ✅ Done |
| Market intelligence tab | ✅ Done |
| Profile edit | ✅ Done |
| Field-based filtered matching | ✅ Done |
| Sidebar removed, sign-out in header | ✅ Done |
| Messaging / DMs | 📋 Planned |
| Fine-tuned matching model | 📋 Planned |
| PostgreSQL migration | 📋 Planned |
| Multi-user admin view | 📋 Planned |
| Email notifications on match | 📋 Planned |

---

## Known Limitations

- **Single-file app** — works fine at this scale, will need to be split into modules as the codebase grows
- **SQLite** — not suitable for concurrent writes at scale; migration to PostgreSQL is the obvious next step
- **No fine-tuning** — the MiniLM model is used zero-shot; match quality would improve significantly with domain-specific fine-tuning on real startup/investor corpus
- **Password hashing** — SHA-256 without salt is fine for a demo, not for production; needs bcrypt
- **No rate limiting** — the matching runs on every tab switch; should be cached per user session
- **Seed CSVs** — market stats tab falls back gracefully if CSVs aren't present, but the data is static

---

## Maybe Future

1. Split `app.py` into `db.py`, `matching.py`, `ui/` modules
2. Swap SQLite for PostgreSQL when deploying to production
3. Collect real match outcome data to fine-tune the embedding model
4. Add bcrypt for password hashing
5. Add a messaging layer between matched parties
6. Cache match results per session instead of recomputing on every render

---

*Built by U.K.B.*
