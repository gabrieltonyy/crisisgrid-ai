# 🚨 CrisisGrid AI

**AI-powered emergency response coordination for faster, trusted crisis decisions in Kenya.**

CrisisGrid AI turns citizen reports into verified crisis intelligence, clustered incidents, safety alerts, and simulated dispatch workflows for authorities.

## Problem

Emergency teams often receive fragmented reports from citizens, social channels, and field operators. The signal is noisy, location data is inconsistent, and response teams need confidence before acting. Delays cost lives.

## Solution

CrisisGrid AI provides a role-based emergency platform where citizens submit reports, AI agents verify and score the information, related reports are clustered into incidents, and authorities receive actionable dashboards, alerts, and simulated dispatch logs.

## Live Demo

| Service | Link |
| --- | --- |
| Frontend | https://crisisgrid-ai.vercel.app/ |
| Backend | https://crisisgrid-backend-dlyj.onrender.com/ |
| API Docs | https://crisisgrid-backend-dlyj.onrender.com/docs |

## Key Features

| Area | What it does |
| --- | --- |
| Citizen reporting | Submit geolocated crisis reports with descriptions and optional media URLs. |
| AI verification | Scores confidence, severity, urgency, and recommended action. |
| Incident clustering | Groups nearby related reports into operational incidents. |
| Public alerts | Generates crisis alerts and citizen safety advisories. |
| Authority console | Tracks reports, incidents, dispatch status, and active alerts. |
| Demo auth | JWT login, protected routes, role-based navigation, and seeded demo users. |

## User Roles

| Role | Capabilities |
| --- | --- |
| Citizen | Register, log in, submit reports, view My Reports, check alerts and advisories. |
| Authority | Access the operations console, review incidents, alerts, reports, and dispatch logs. |
| Admin | Full demo command-center access for judging and system review. |

## How It Works

1. Citizen submits a geolocated crisis report.
2. AI verifies the report and scores confidence/severity.
3. Related reports cluster into incidents.
4. Alerts are generated for affected areas.
5. Dispatch is simulated for the relevant authority.
6. Citizens receive advisories and can track their reports.

## Tech Stack

| Layer | Tools |
| --- | --- |
| Backend | FastAPI, PostgreSQL, SQLAlchemy, Pydantic, JWT |
| Frontend | Next.js 14, TypeScript, Ant Design, React Query, Zustand |
| AI and data | IBM watsonx.ai, IBM Cloudant |
| Deployment | Render backend, Vercel frontend |

## Architecture

```text
Citizen Portal / Admin Console
          |
      Next.js 14
          |
      FastAPI API
          |
PostgreSQL + Cloudant audit/raw payload storage
          |
Verification, clustering, alert, dispatch, advisory services
          |
IBM watsonx.ai for AI-assisted crisis reasoning
```

## Folder Structure

```text
.
├── Buildproject/
│   ├── backend/        # FastAPI API, models, schemas, services, tests, seed script
│   └── frontend/       # Next.js app, auth pages, protected layouts, API clients
├── docs/               # Architecture, planning, demo, security, and IBM context
├── README.md
└── INSTRUCTIONS.md
```

## Local Setup

### Backend

```bash
cd Buildproject/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
cp .env.example .env
docker compose up -d postgres
cd backend
python -m app.db.init_db
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd Buildproject/frontend
npm install
cp .env.example .env.local
npm run dev
```

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection string. |
| `JWT_SECRET` | Secret used to sign JWT access tokens. |
| `FRONTEND_ORIGINS` | Comma-separated CORS allowlist. |
| `NEXT_PUBLIC_API_BASE_URL` | Frontend API base, usually `/api/v1` locally through Next rewrites. |
| `BACKEND_API_URL` | Backend URL used by Next.js rewrites. |
| `WATSONX_*` | IBM watsonx.ai configuration. |
| `CLOUDANT_*` | IBM Cloudant raw report and audit storage configuration. |

## Seed Data

```bash
cd Buildproject/backend
python scripts/seed_data.py
```

Demo password for all seeded accounts: `Password123!`

| Role | Email |
| --- | --- |
| Citizen | `citizen.demo01@demo.crisisgrid.ai` |
| Authority | `authority.demo01@demo.crisisgrid.ai` |
| Admin | `admin.demo01@demo.crisisgrid.ai` |

## Testing

```bash
cd Buildproject/frontend
npm run lint
npm run build

cd ../backend
python -m compileall app
pytest
```

## Security Notes

- JWT tokens are attached as `Authorization: Bearer <token>`.
- Frontend protected routes enforce Citizen, Authority, and Admin access.
- CORS is environment-driven through `FRONTEND_ORIGINS`.
- Passwords are hashed with bcrypt.
- Demo dispatch is simulated; do not use this MVP for real emergency response.

## Known Limitations

- Dispatch integrations are simulated.
- AI verification can run in simulated mode when IBM credentials are not configured.
- No production-grade OAuth/SSO or refresh-token rotation yet.
- Database migrations are not fully formalized with Alembic in this hackathon build.

## Roadmap

- Add real authority integrations and notification providers.
- Add richer incident clustering and duplicate detection.
- Add live map overlays for risk radius and responder status.
- Add audit dashboards backed by Cloudant.
- Add production OAuth/SSO and stronger rate limiting.

## IBM Hackathon Context

CrisisGrid AI demonstrates how IBM watsonx.ai and IBM Cloudant can support a multi-agent public safety workflow: verify reports, preserve raw/audit data, explain crisis decisions, and coordinate faster citizen-to-authority response.
