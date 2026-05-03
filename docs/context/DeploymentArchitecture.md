# CrisisGrid AI — Deployment Architecture

## Purpose

This document defines how CrisisGrid AI should be deployed for the IBM Bob Dev Day Hackathon MVP and how it can evolve into a production-ready system.

The deployment plan is designed for:

- solo developer execution
- fast local development
- simple demo readiness
- IBM Cloud alignment
- safe handling of credentials
- optional production-style deployment

---

## Deployment Philosophy

For the hackathon, the priority is:

```text
Working demo first → clean deployment second → production scaling later
```

Do not over-engineer deployment before the core crisis flow works.

The demo must clearly show:

```text
Citizen report → agent processing → alert → dispatch simulation → dashboard
```

---

# 1. Recommended Deployment Stages

## Stage 1 — Local Development

Use this while building quickly.

```text
Frontend: React / Next.js local dev server
Backend: FastAPI local server
Database: PostgreSQL via Docker
Optional: Cloudant remote IBM Cloud service
```

## Stage 2 — Demo Deployment

Use this when preparing for judges.

```text
Frontend: Vercel / Netlify / static hosting
Backend: IBM Code Engine / Render / Railway / local exposed demo
Database: PostgreSQL managed or Docker local
Cloudant: IBM Cloudant if available
```

## Stage 3 — Future Production

Use this after hackathon.

```text
Frontend: CDN/static hosting
Backend: containerized services
Database: managed PostgreSQL + PostGIS
Cloudant: raw report/audit/event storage
Queue: Redis / Pub/Sub
Observability: logs, traces, metrics
```

---

# 2. MVP Deployment Architecture

```text
┌────────────────────────────┐
│ Frontend Web App           │
│ React / Next.js            │
│ Citizen UI + Dashboard     │
└──────────────┬─────────────┘
               │ HTTP REST
               ↓
┌────────────────────────────┐
│ FastAPI Backend            │
│ API + Agent Orchestrator   │
│ Verification + GeoRisk     │
│ Alerts + Dispatch Logs     │
└──────────────┬─────────────┘
               ↓
┌────────────────────────────┐
│ Database Layer             │
│ PostgreSQL                 │
│ Optional IBM Cloudant      │
└────────────────────────────┘
```

---

# 3. Local Development Deployment

## Recommended Local Tools

- Docker
- Docker Compose
- Python 3.11+
- Node.js 20+
- PostgreSQL
- Optional Redis
- Optional IBM Cloudant remote instance

---

## Local Docker Compose

Recommended local services:

```text
backend
frontend
postgres
redis optional
```

Example structure:

```text
infrastructure/docker/docker-compose.yml
```

---

## Example Docker Compose

```yaml
version: "3.9"

services:
  postgres:
    image: postgres:16
    container_name: crisisgrid-postgres
    environment:
      POSTGRES_DB: crisisgrid
      POSTGRES_USER: crisisgrid
      POSTGRES_PASSWORD: crisisgrid_password
    ports:
      - "5432:5432"
    volumes:
      - crisisgrid_pgdata:/var/lib/postgresql/data

  backend:
    build:
      context: ../../services/backend
      dockerfile: Dockerfile
    container_name: crisisgrid-backend
    env_file:
      - ../../.env
    ports:
      - "8000:8000"
    depends_on:
      - postgres

  frontend:
    build:
      context: ../../apps/web-dashboard
      dockerfile: Dockerfile
    container_name: crisisgrid-frontend
    env_file:
      - ../../.env
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  crisisgrid_pgdata:
```

---

# 4. Backend Deployment

## Recommended Backend

Use **FastAPI** packaged as a Docker container.

## Backend Runtime

```text
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Backend Deployment Options

### Option 1 — IBM Code Engine

Best IBM-aligned option.

Use when you have IBM Cloud access and enough time.

Benefits:

- IBM ecosystem alignment
- container-based deployment
- serverless style
- good for hackathon narrative

### Option 2 — Render / Railway

Good fallback if IBM setup takes too long.

### Option 3 — Local Demo

Acceptable fallback if cloud deployment becomes a blocker.

Use:

- localhost
- screen recording
- ngrok/cloudflared if needed

---

# 5. IBM Code Engine Deployment

## Why Use It

IBM Code Engine is available in the hackathon guide as one of the IBM Cloud services.

It can deploy the FastAPI backend container and strengthen IBM alignment.

---

## High-Level Steps

1. Build backend Docker image
2. Push image to container registry
3. Create Code Engine project
4. Deploy container as an application
5. Add environment variables
6. Test `/health`
7. Connect frontend to deployed backend URL

---

## Important Note for IBM Bob

IBM Bob may not directly access your IBM Cloud dashboard.

If Bob cannot deploy directly, it should guide you through:

- creating a Code Engine project
- building the container
- pushing the image
- configuring environment variables
- checking logs
- testing endpoints

Bob should provide commands and UI steps, not ask for real secrets.

---

# 6. Frontend Deployment

## Recommended Frontend

Use React / Next.js for the MVP.

## Frontend Options

### Option 1 — Vercel

Fastest for Next.js.

### Option 2 — Netlify

Good for static frontend builds.

### Option 3 — IBM Code Engine

Good for IBM-aligned full-stack deployment if containerized.

### Option 4 — Local Demo

Fastest fallback.

---

## Frontend Environment Variables

```text
NEXT_PUBLIC_API_BASE_URL=
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=
```

Never expose private backend secrets in frontend variables.

Only expose values intended for browser use.

---

# 7. Database Deployment

## Option 1 — Local PostgreSQL

Best for fastest build.

Use Docker Compose.

```text
postgresql://crisisgrid:crisisgrid_password@localhost:5432/crisisgrid
```

## Option 2 — Managed PostgreSQL

Use if available.

Good for public demos.

## Option 3 — IBM Cloudant

Use for:

- raw report JSON
- agent payload logs
- AI verification metadata
- audit events

## Option 4 — Hybrid

Recommended for IBM narrative:

```text
PostgreSQL = structured incident intelligence
Cloudant = raw reports and AI processing payloads
```

---

# 8. Cloudant Deployment

## Purpose

Cloudant can store raw incoming crisis reports and agent logs as flexible JSON documents.

## Example Cloudant Databases

```text
crisis_reports_raw
agent_payload_logs
audit_events
```

## Example Cloudant Document

```json
{
  "_id": "raw-report-REP-001",
  "type": "raw_report",
  "report_id": "REP-001",
  "payload": {
    "crisis_type": "FIRE",
    "description": "Smoke and flames near building",
    "latitude": -1.2921,
    "longitude": 36.8219
  },
  "created_at": "2026-05-01T10:20:00Z"
}
```

---

# 9. Environment Configuration

Use `.env` locally.

Use platform environment variables in deployed environments.

## Required `.env`

```text
APP_ENV=local
API_PORT=8000

DATABASE_URL=postgresql://crisisgrid:crisisgrid_password@localhost:5432/crisisgrid

CLOUDANT_URL=
CLOUDANT_API_KEY=
CLOUDANT_DB_REPORTS=crisis_reports_raw
CLOUDANT_DB_AGENT_LOGS=agent_payload_logs

WATSONX_API_KEY=
WATSONX_PROJECT_ID=
IBM_CLOUD_API_KEY=

WEATHER_API_KEY=
GOOGLE_MAPS_API_KEY=
SMS_API_KEY=

JWT_SECRET=replace_with_secure_value
```

---

# 10. Secrets Management

## Rules

Never commit:

```text
.env
service-account.json
credentials.json
*.pem
*.key
```

## Required `.gitignore`

```text
.env
.env.*
!.env.example
service-account.json
credentials.json
*.pem
*.key
node_modules/
__pycache__/
.venv/
dist/
build/
```

## IBM Bob Rule

Do not paste real credentials into Bob prompts.

Use placeholders and ask Bob to guide setup.

---

# 11. CI/CD Deployment

For MVP, keep CI/CD lightweight.

## Recommended GitHub Actions

```text
lint backend
test backend
build backend container
lint frontend
build frontend
```

Full automated deployment is optional.

---

## MVP GitHub Actions Example

```yaml
name: CrisisGrid CI

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  backend-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install backend dependencies
        run: |
          cd services/backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd services/backend
          pytest

  frontend-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install frontend dependencies
        run: |
          cd apps/web-dashboard
          npm install
      - name: Build frontend
        run: |
          cd apps/web-dashboard
          npm run build
```

---

# 12. Observability

## MVP Observability

Use simple structured logs.

Log:

- report submitted
- agent started
- agent completed
- confidence changed
- alert created
- dispatch simulated
- error occurred

## Recommended Log Format

```json
{
  "event": "agent_completed",
  "agent_name": "verification_agent",
  "report_id": "REP-001",
  "confidence_after": 0.72,
  "duration_ms": 240
}
```

---

# 13. Health Checks

Backend should expose:

```text
GET /health
```

Response:

```json
{
  "status": "UP",
  "service": "crisisgrid-api",
  "version": "1.0.0"
}
```

Optional:

```text
GET /health/db
GET /health/cloudant
```

---

# 14. Demo Deployment Strategy

## Best Demo Setup

Use:

```text
Frontend: deployed or local
Backend: deployed on IBM Code Engine or local
Database: local PostgreSQL or managed PostgreSQL
Cloudant: optional IBM Cloudant
```

## Backup Demo Plan

Always prepare a local backup.

If cloud deployment fails:

- run backend locally
- run frontend locally
- use seeded demo data
- record demo video
- show Bob session reports

---

# 15. Deployment Priority for Solo Build

## Must Have

- local backend running
- local frontend running
- PostgreSQL running
- seed data
- `/health` endpoint
- `.env.example`
- deployment instructions in README

## Should Have

- Docker Compose
- deployed frontend
- deployed backend
- Cloudant integration

## Nice to Have

- IBM Code Engine deployment
- GitHub Actions CI
- Redis queue
- managed PostgreSQL
- custom domain

## Skip for MVP

- Kubernetes
- Terraform
- autoscaling configuration
- multi-region deployment
- full production monitoring
- blue/green deployment

---

# 16. Production Evolution

Future production architecture:

```text
Frontend CDN
    ↓
API Gateway
    ↓
Backend Services
    ↓
Agent Workers
    ↓
Queue System
    ↓
PostgreSQL + PostGIS
    ↓
Cloudant / Object Storage / Analytics
```

## Future Enhancements

- Redis or Pub/Sub for async agent execution
- object storage for media
- PostGIS for accurate geospatial queries
- observability platform
- managed secrets
- production IAM
- real SMS/email integrations
- disaster recovery backups

---

# 17. Deployment Documentation Bob Should Generate

Use IBM Bob to generate:

- Dockerfiles
- docker-compose.yml
- README deployment instructions
- `.env.example`
- Code Engine deployment guide
- database migration guide
- seed script guide
- troubleshooting guide

Save Bob outputs and reports in:

```text
bob_sessions/
```

---

# 18. Final Deployment Principle

The deployment should support the story, not distract from it.

For the hackathon, success means:

```text
A judge can open the app, submit a crisis report, see agents process it,
view an alert, and see simulated dispatch logs.
```

That is more important than having a perfect enterprise deployment.
