# CrisisGrid AI Instructions

Practical setup, demo, QA, and deployment guide for developers and operators.

## Prerequisites

| Tool | Recommended |
| --- | --- |
| Node.js | 18+ |
| npm | 9+ |
| Python | 3.11+ |
| PostgreSQL | 14+ |
| Docker | Optional, for local PostgreSQL |

## Clone And Enter Repo

```bash
git clone <repo-url>
cd IBM-Hack
```

## Backend Setup

```bash
cd Buildproject/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `Buildproject/.env`:

```bash
cd ..
cp .env.example .env
```

Minimum backend variables:

```bash
DATABASE_URL=postgresql://crisisgrid:crisisgrid_password@localhost:5432/crisisgrid
JWT_SECRET=replace_with_secure_random_value
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://crisisgrid-ai.vercel.app
```

## Database Setup

Using Docker:

```bash
cd Buildproject
docker compose up -d postgres
```

Initialize tables:

```bash
cd Buildproject/backend
python -m app.db.init_db
```

Reset tables only when you intentionally want to delete local data:

```bash
python -m app.db.init_db --reset
```

## Seed Data

```bash
cd Buildproject/backend
python scripts/seed_data.py
```

Seed output includes demo credentials. Default password: `Password123!`

| Role | Email |
| --- | --- |
| Citizen | `citizen.demo01@demo.crisisgrid.ai` |
| Authority | `authority.demo01@demo.crisisgrid.ai` |
| Admin | `admin.demo01@demo.crisisgrid.ai` |

## Run Backend

```bash
cd Buildproject/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Useful URLs:

| URL | Purpose |
| --- | --- |
| `http://localhost:8000/health` | Health check |
| `http://localhost:8000/api/v1/health` | API health |
| `http://localhost:8000/docs` | Swagger docs |

## Frontend Setup

```bash
cd Buildproject/frontend
npm install
cp .env.example .env.local
```

Recommended local frontend variables:

```bash
NEXT_PUBLIC_API_BASE_URL=/api/v1
BACKEND_API_URL=http://localhost:8000
NEXT_PUBLIC_DEMO_AUTH_ROLES=false
```

Run:

```bash
npm run dev
```

Open `http://localhost:3000`.

## Running Tests And Checks

Frontend:

```bash
cd Buildproject/frontend
npm run lint
npm run build
```

Backend:

```bash
cd Buildproject/backend
python -m compileall app
pytest
```

## Demo Flow

1. Log in as `citizen.demo01@demo.crisisgrid.ai`.
2. Submit a crisis report from the Citizen Portal.
3. Open My Reports and confirm the report appears from `/api/v1/reports/me`.
4. Log out.
5. Log in as `admin.demo01@demo.crisisgrid.ai`.
6. Open Command Center, Reports, Alerts, Incidents, and Dispatch.
7. Confirm a Citizen account cannot access `/admin/dashboard`.

## Deployment Notes

### Render Backend

Set environment variables:

```bash
APP_ENV=production
DATABASE_URL=<render-postgres-url>
JWT_SECRET=<strong-secret>
FRONTEND_ORIGINS=https://crisisgrid-ai.vercel.app,http://localhost:3000,http://127.0.0.1:3000
WATSONX_ENABLED=false
CLOUDANT_ENABLED=false
ENABLE_SIMULATED_VERIFICATION=true
ENABLE_SIMULATED_DISPATCH=true
```

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Vercel Frontend

Set environment variables:

```bash
NEXT_PUBLIC_API_BASE_URL=/api/v1
BACKEND_API_URL=https://crisisgrid-backend-dlyj.onrender.com
NEXT_PUBLIC_DEMO_AUTH_ROLES=false
```

The frontend uses Next.js rewrites so browser calls to `/api/v1/*` are forwarded to the backend.

## Important Commands

| Command | Purpose |
| --- | --- |
| `python -m app.db.init_db` | Create database tables. |
| `python scripts/seed_data.py` | Create 50 demo users and 300 reports. |
| `uvicorn app.main:app --reload` | Run backend locally. |
| `npm run dev` | Run frontend locally. |
| `npm run build` | Validate production frontend build. |
| `pytest` | Run backend tests. |

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `DATABASE_URL` missing | Create `Buildproject/.env` from `.env.example`. |
| CORS error in browser | Add the frontend origin to `FRONTEND_ORIGINS` and restart backend. |
| Login succeeds but API calls are unauthorized | Confirm `auth_token` exists in localStorage and API calls include `Authorization: Bearer <token>`. |
| `/reports/me` returns 401 | Log in again; the endpoint requires JWT auth. |
| Citizen can open admin URL briefly | ProtectedRoute redirects after session check; verify token role and clear stale localStorage. |
| Vercel calls wrong backend | Set `BACKEND_API_URL` to the Render backend URL and redeploy. |
| Seed fails on missing tables | Run `python -m app.db.init_db` first. |
