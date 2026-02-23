# StartupMatch - Project Summary

## Overview

**Project Name:** StartupMatch  
**Goal:** A platform that connects investors with startups using intelligent matching algorithms, enabling bidirectional discovery and seamless communication.

**Current Status:** MVP Complete (Rules-based matching, ready for ML enhancement)

---

## Architecture

```
startupmatch/
├── backend/                    # Flask API (Python)
│   ├── app.py                  # Entry point, routes registration
│   ├── auth.py                 # JWT auth, CSV data handlers
│   ├── matching.py             # Rules-based scoring algorithm
│   ├── routes/
│   │   ├── auth_routes.py      # /api/auth/*
│   │   ├── investor_routes.py  # /api/investor/*
│   │   └── startup_routes.py   # /api/startup/*
│   └── data/                   # CSV storage (to migrate to DB)
│       ├── investors.csv
│       ├── startups.csv
│       └── matches.csv
├── frontend/                   # React + Vite
│   └── src/
│       ├── pages/              # Login, Register, Dashboards
│       ├── App.jsx             # Main app with routing
│       ├── api.js             # API client
│       └── App.css            # Styling
├── model/                     # Jupyter notebooks for ML
│   ├── matching_model.ipynb   # PyTorch + Gradient Boosting
│   └── training_guide.ipynb   # Training instructions
└── requirements.txt           # Python dependencies
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React 18 + Vite | Fast, lightweight UI |
| Backend | Flask (Python) | REST API |
| Storage | CSV files | Simple data persistence (MVP) |
| Auth | JWT (PyJWT) | Stateless authentication |
| ML Framework | PyTorch + scikit-learn | Model training |
| Deployment | Local (Docker planned) | Development environment |

---

## Matching Algorithm

### Current Implementation (Rules-Based)

**Score Formula:**
```
Total Score = 0.40 × Sector_Match 
            + 0.25 × Stage_Match 
            + 0.15 × Location_Match 
            + 0.20 × Funding_Match
```

**Component Scoring:**

| Component | Logic |
|-----------|-------|
| **Sector Match** | 1.0 if startup sector in investor's preferred sectors, else 0.0 |
| **Stage Match** | 1.0 if exact match, decreases by 0.25 per stage difference |
| **Location Match** | 1.0 if match or "Global", else 0.3 |
| **Funding Match** | 1.0 if within range, proportional score otherwise |

**Stages Order:** Pre-Seed → Seed → Series A → Series B → Series C → Growth

### Future Implementation (ML-Based)

- **Architecture:** Neural Network (64→32→16→1) + Gradient Boosting ensemble
- **Input Features:** 8 numerical features (sector_match, stage_match, location_match, funding_match, team_size, revenue, growth_rate)
- **Output:** Match probability (0-1)
- **Training:** Supervised learning with labeled successful/failed matches

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup/investor` | Register new investor |
| POST | `/api/auth/signup/startup` | Register new startup |
| POST | `/api/auth/login` | Login (returns JWT) |
| GET | `/api/auth/verify` | Verify token validity |

### Investor

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/investor/profile` | Get investor profile |
| PUT | `/api/investor/profile` | Update profile |
| GET | `/api/investor/matches?top=N` | Get top N matching startups |
| GET | `/api/investor/all` | List all investors (public) |

### Startup

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/startup/profile` | Get startup profile |
| PUT | `/api/startup/profile` | Update profile |
| GET | `/api/startup/matches?top=N` | Get top N matching investors |
| GET | `/api/startup/all` | List all startups (public) |

---

## Data Models

### Investor Profile
```json
{
  "id": "abc123",
  "email": "investor@example.com",
  "name": "John Smith",
  "company": "Venture Capital LLC",
  "sectors": ["Technology", "Healthcare"],
  "stage_preference": "Series A",
  "min_check": 100000,
  "max_check": 500000,
  "locations": ["North America", "Europe"],
  "created_at": "2024-01-15T10:00:00"
}
```

### Startup Profile
```json
{
  "id": "xyz789",
  "email": "founder@startup.com",
  "name": "TechFlow AI",
  "description": "AI-powered workflow automation",
  "sector": "Technology",
  "stage": "Seed",
  "funding_needed": 150000,
  "location": "North America",
  "team_size": 5,
  "revenue": 50000,
  "growth_rate": 200,
  "created_at": "2024-01-10T09:00:00"
}
```

### Match Result
```json
{
  "investor_id": "abc123",
  "startup_id": "xyz789",
  "score": 0.85,
  "sector_match": 1.0,
  "stage_match": 0.75,
  "location_match": 1.0,
  "funding_match": 0.6,
  "computed_at": "2024-01-20T12:00:00"
}
```

---

## Current Progress

| Milestone | Status |
|-----------|--------|
| Project structure | ✅ Complete |
| Backend API (Flask) | ✅ Complete |
| CSV data handlers | ✅ Complete |
| JWT authentication | ✅ Complete |
| Rules-based matching | ✅ Complete |
| React frontend | ✅ Complete |
| Demo data (5 investors, 7 startups) | ✅ Complete |
| Jupyter ML notebooks | ✅ Complete |
| ML model training | ⏳ Pending (needs data) |
| Messaging system | 📋 Planned |
| Database migration (PostgreSQL) | 📋 Planned |
| Docker deployment | 📋 Planned |

---

## Dataset Requirements

### What We Need

To train the ML model effectively, we need **labeled match data**:

| Data Type | Description | Min Quantity |
|-----------|-------------|--------------|
| **Successful Matches** | Investor-startup pairs that resulted in funding | 100+ |
| **Failed Matches** | Pairs that connected but didn't result in funding | 100+ |
| **Investor Profiles** | Complete investor preferences | 50+ |
| **Startup Profiles** | Complete startup details | 100+ |

### Required CSV Format for Training

**labeled_matches.csv:**
```csv
investor_id,startup_id,success
inv_001,start_001,1
inv_002,start_001,0
inv_003,start_002,1
```

- `success = 1`: Investment occurred
- `success = 0`: Match explored but no investment

### Potential Data Sources

| Source | Type | Access |
|--------|------|--------|
| Crunchbase | Startup/Investor data | API (paid) |
| PitchBook | VC deals | Subscription |
| AngelList | Startup profiles | API |
| CB Insights | Funding rounds | Subscription |
| Kaggle Datasets | Startup/company data | Free |
| SEC EDGAR | Public filings | Free |

### Recommended Kaggle Searches
- "startup funding dataset"
- "venture capital investments"
- "company funding rounds"
- "crunchbase dataset"
- "angel investment data"

---

## How to Run

### Backend
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate (Windows)
pip install -r requirements.txt
cd backend && python app.py
```
Runs at: `http://localhost:5000`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Runs at: `http://localhost:3000`

### Demo Credentials
| User Type | Email | Password |
|-----------|-------|----------|
| Investor | investor1@demo.com | password123 |
| Startup | startup1@demo.com | password123 |

---

## Key Files for New Developers

| File | Purpose |
|------|---------|
| `backend/matching.py` | Core matching logic - start here |
| `backend/auth.py` | User management & data persistence |
| `frontend/src/pages/InvestorDashboard.jsx` | Investor UI |
| `frontend/src/pages/StartupDashboard.jsx` | Startup UI |
| `model/matching_model.ipynb` | ML training code (Kaggle-ready) |

---

## Next Steps

1. **Acquire labeled data** - Find datasets with successful investor-startup matches
2. **Train ML model** - Use `model/matching_model.ipynb` on Kaggle with GPU
3. **Integrate trained model** - Replace rules-based scoring in `backend/matching.py`
4. **Add messaging** - DM functionality between matched parties
5. **Migrate to database** - PostgreSQL or MongoDB for production
6. **Deploy** - Docker + cloud hosting

---

## Contact & Handoff

**Project Location:** `D:\StartupMatch\`

**Key Dependencies:**
- Python 3.10+
- Node.js 18+
- PyTorch (for ML training)

**Questions to Resolve:**
1. Where will production data come from?
2. What's the target user base size?
3. Preference for cloud provider (AWS, GCP, Azure)?
