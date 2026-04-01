# 🎯 LeadAura — B2B Lead Intelligence Platform
> Identify, score and enrich high-value B2B leads automatically

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

## What is LeadAura
LeadAura is a fully automated B2B lead intelligence platform. Any company can configure it with their own Ideal Client Profile (ICP). It automatically finds, scores and enriches companies. It exposes a REST API and a visual dashboard.

## Live Dashboard
![LeadAura Dashboard](dashboard/screenshot.png)

## Features
- 🔍 Automated company discovery from public sources
- 🧠 Intelligent lead scoring engine (0-100) based on custom ICP
- ✨ Company enrichment — tech stack, keywords, email patterns, social links
- 🎯 Priority classification — High / Medium / Low
- ⚡ FastAPI REST backend with 6 endpoints
- 📊 Beautiful real-time dashboard with charts
- 🔥 Firebase Firestore cloud database — free and scalable
- ⚙️ Fully configurable ICP — any company can adapt it in 1 file
- 🚀 One-click pipeline runner from the dashboard

## Tech Stack
| Layer | Technology | Language |
| --- | --- | --- |
| Database | Firebase Firestore | Python |
| Backend API | FastAPI + Uvicorn | Python 3.11+ |
| Scraping | Requests + BeautifulSoup | Python |
| Dashboard | HTML + CSS + JavaScript + Chart.js | JavaScript |
| Environment | Python venv | |
| Hosting (DB) | Google Firebase (free tier) | |

## Architecture
```text
[Public Web Sources]
        ↓
[Ingestion Layer — Scrapers & API Collectors]
        ↓
[Firebase Firestore — raw_companies]
        ↓
[Lead Scoring Engine — score 0 to 100]
        ↓
[Firebase Firestore — scored_leads]
        ↓
[Enrichment Layer — tech stack, emails, keywords]
        ↓
[Firebase Firestore — enriched_leads]
        ↓
[FastAPI Backend — REST API]
        ↓
[Dashboard — Charts, Tables, Search, Filters]
```

## Project Structure
```text
leadaura/
├── ingestion/              # Scrapers and data collectors
│   ├── scrapers/           # Web scrapers
│   └── api_collectors/     # Free API data collectors
├── enrichment/             # Company enrichment logic
├── scoring/                # Lead scoring engine
├── api/                    # FastAPI backend
├── dashboard/              # Web dashboard
├── config/                 # ICP config and Firebase config
├── firebase/               # Firebase credentials (gitignored)
├── data/                   # Raw and staging data
└── pipelines/              # Airflow DAGs (future)
```

## Quick Start Guide

**Step 1 — Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/leadaura.git
cd leadaura
```

**Step 2 — Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

**Step 3 — Set up Firebase**
- Create a project at console.firebase.google.com
- Enable Firestore Database
- Generate a Service Account Key
- Save it as `firebase/serviceAccountKey.json`

**Step 4 — Configure your ICP**
Edit `config/icp_config.json`:
```json
{
  "icp": {
    "target_industries": ["SaaS", "FinTech"],
    "min_employees": 10,
    "max_employees": 200,
    "target_locations": ["France", "Germany", "UAE"]
  }
}
```

**Step 5 — Set up environment variables**
Create a `.env` file:
```env
FIREBASE_CREDENTIALS_PATH=firebase/serviceAccountKey.json
```

**Step 6 — Run the pipeline**
```bash
python ingestion/run_ingestion.py
python scoring/run_scoring.py
python enrichment/run_enrichment.py
```

**Step 7 — Start the API**
```bash
cd api
python run_api.py
```
- API runs at: http://localhost:8000
- API docs at: http://localhost:8000/docs

**Step 8 — Open the dashboard**
Open `dashboard/index.html` directly in your browser.

## API Endpoints
| Method | Endpoint | Description |
| --- | --- | --- |
| GET | / | API status and info |
| GET | /leads | Get all leads with optional filters |
| GET | /leads?priority=High | Filter by priority |
| GET | /leads?industry=SaaS | Filter by industry |
| GET | /leads?location=UAE | Filter by location |
| GET | /top-leads | Get top 20 High priority leads |
| GET | /stats | Get dashboard statistics |
| GET | /search?q=keyword | Search leads by keyword |
| POST | /run-pipeline | Trigger the full pipeline |

## Configuration
The ICP config file controls scoring weights and targets:
- `target_industries` — which industries to target
- `min_employees` / `max_employees` — company size range
- `target_locations` — which countries to target
- `keywords` — keywords to look for in company descriptions
- `scoring_weights` — how much each factor contributes to the score

## Scoring System
| Factor | Points | Condition |
| --- | --- | --- |
| Industry match | 30 | Company is in target industries |
| Size match | 25 | Employee count in target range |
| Location match | 20 | Company is in target locations |
| Tech stack detected | 15 | Tech keywords found on website |
| Keyword match | 10 | ICP keywords found in description |
| **Total** | **100** | |

Priority:
- 🟢 High — score ≥ 70
- 🟡 Medium — score ≥ 40
- 🔴 Low — score < 40

## Security Notes
- Never commit `firebase/serviceAccountKey.json` to GitHub
- Never commit `.env` to GitHub
- Both are already in `.gitignore`

## License
MIT License — free to use, modify and distribute

## Built by
Built with ❤️ by [Your Name]
Powered by LeadAura v1.0.0
