# CrisisGrid AI — CI/CD Pipeline

## Purpose

This document defines the CI/CD pipeline strategy for CrisisGrid AI.

The pipeline is designed for:

- solo hackathon development
- fast feedback
- safe code changes
- basic automated testing
- optional deployment
- clear judging readiness

The goal is not enterprise-level DevOps.

The goal is to prevent the demo from breaking.

---

## CI/CD Philosophy

For the hackathon:

```text
Automate checks first.
Automate deployment only if time allows.
```

A stable local demo is better than a broken cloud deployment.

---

# 1. Pipeline Objectives

The CI/CD pipeline should:

- verify backend code runs
- verify frontend builds
- run critical tests
- catch missing dependencies
- reduce last-minute demo risk
- prevent accidental secret leaks
- support optional container deployment

---

# 2. Recommended Pipeline Stages

```text
1. Checkout code
2. Backend dependency install
3. Backend lint / formatting check
4. Backend tests
5. Frontend dependency install
6. Frontend type check
7. Frontend build
8. Docker build optional
9. Deployment optional
```

---

# 3. MVP CI Pipeline

For MVP, implement one GitHub Actions workflow:

```text
.github/workflows/ci.yml
```

This should run on:

```text
push to main
pull_request
```

Even as a solo developer, this helps catch broken commits.

---

# 4. GitHub Actions CI Example

```yaml
name: CrisisGrid CI

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  backend-checks:
    name: Backend Checks
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: crisisgrid_test
          POSTGRES_USER: crisisgrid
          POSTGRES_PASSWORD: crisisgrid_password
        ports:
          - 5432:5432
        options: >-
          --health-cmd="pg_isready -U crisisgrid"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5

    env:
      APP_ENV: test
      DATABASE_URL: postgresql://crisisgrid:crisisgrid_password@localhost:5432/crisisgrid_test
      AUTH_MODE: demo
      JWT_SECRET: test_secret
      CLOUDANT_ENABLED: false
      WATSONX_ENABLED: false
      WEATHER_ENABLED: false
      ENABLE_SIMULATED_VERIFICATION: true
      ENABLE_SIMULATED_DISPATCH: true

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install backend dependencies
        run: |
          cd services/backend
          pip install -r requirements.txt

      - name: Run backend tests
        run: |
          cd services/backend
          pytest

  frontend-checks:
    name: Frontend Checks
    runs-on: ubuntu-latest

    env:
      NEXT_PUBLIC_API_BASE_URL: http://localhost:8000/api/v1

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install frontend dependencies
        run: |
          cd apps/web-app
          npm install

      - name: Type check
        run: |
          cd apps/web-app
          npm run typecheck --if-present

      - name: Build frontend
        run: |
          cd apps/web-app
          npm run build
```

---

# 5. Backend CI Checks

## Required

```text
pip install -r requirements.txt
pytest
```

## Optional

```text
ruff check .
black --check .
mypy .
```

## Recommended for MVP

Start with:

```text
pytest
```

Add linting only if it does not slow you down.

---

# 6. Frontend CI Checks

## Required

```text
npm install
npm run build
```

## Optional

```text
npm run lint
npm run typecheck
npm test
```

## Recommended for MVP

Use:

```text
npm run build
```

because it catches many TypeScript and Next.js errors.

---

# 7. Docker Build Pipeline Optional

If Dockerfiles are ready, add Docker build checks.

```yaml
docker-build:
  name: Docker Build
  runs-on: ubuntu-latest

  steps:
    - uses: actions/checkout@v4

    - name: Build backend image
      run: |
        docker build -t crisisgrid-backend ./services/backend

    - name: Build frontend image
      run: |
        docker build -t crisisgrid-frontend ./apps/web-app
```

This verifies the app can be containerized.

---

# 8. Secret Scanning

## Required Practice

Do not commit secrets.

Use:

```text
.env.example
```

not:

```text
.env
```

## Optional CI Secret Scan

If time allows, add a secret scanning tool.

Options:

```text
gitleaks
trufflehog
```

## Manual MVP Check

Before submission:

```bash
grep -R "API_KEY" .
grep -R "password" .
grep -R "secret" .
```

Review results manually.

---

# 9. Deployment Pipeline Options

## Option 1 — Manual Deployment

Recommended for hackathon.

Why:

- fewer moving parts
- easier to debug
- avoids last-minute CI failures

Flow:

```text
run tests
build frontend
build backend container
deploy manually
```

---

## Option 2 — Semi-Automated Deployment

Use CI for tests and build only.

Deploy manually to:

- IBM Code Engine
- Vercel
- Render
- Railway
- local demo

---

## Option 3 — Full Automated Deployment

Only if time allows.

Not required for MVP.

---

# 10. IBM Code Engine Deployment Workflow Optional

If using IBM Code Engine, create:

```text
.github/workflows/deploy-code-engine.yml
```

But for the hackathon, manual deployment is safer.

## High-Level Steps

```text
1. Build backend Docker image
2. Push image to container registry
3. Deploy to IBM Code Engine
4. Set environment variables
5. Test /health
```

## Important

Do not store IBM Cloud API keys directly in the repo.

Use GitHub Actions secrets if automating.

---

# 11. Vercel / Netlify Frontend Deployment

For fastest frontend deployment:

```text
Connect GitHub repo
Set root directory: apps/web-app
Set NEXT_PUBLIC_API_BASE_URL
Deploy
```

If deployment fails, use local frontend for demo.

---

# 12. Environments

## local

Developer machine.

```text
APP_ENV=local
```

## test

CI environment.

```text
APP_ENV=test
```

## demo

Judging/demo environment.

```text
APP_ENV=demo
```

## production

Future only.

```text
APP_ENV=production
```

---

# 13. Branching Strategy

Since this is solo:

```text
main
feature/*
```

Recommended:

- Keep `main` stable
- Create feature branches only for larger changes
- Merge often
- Avoid long-lived branches

Examples:

```text
feature/report-flow
feature/agent-orchestrator
feature/dashboard
feature/demo-polish
```

---

# 14. Commit Message Standard

Use simple conventional commits.

Examples:

```text
feat: add crisis report endpoint
feat: implement verification agent
feat: add georisk radius logic
feat: create dashboard incident queue
fix: prevent low confidence dispatch
docs: add system architecture
test: add fire threshold test
chore: add docker compose
```

---

# 15. Pull Request Strategy

Since you are solo, PRs are optional.

If you use PRs, keep them focused.

Example PRs:

```text
PR 1: backend report submission
PR 2: agent pipeline and credibility scoring
PR 3: frontend report flow
PR 4: dashboard and alerts
PR 5: documentation and demo polish
```

---

# 16. Release Checklist

Before final submission:

## Code

- backend starts
- frontend starts
- tests pass
- frontend builds
- seed data works
- no secrets committed

## Demo

- fire demo works
- flood demo works
- wildlife demo works or is ready as optional
- dashboard shows agent logs
- alerts display clearly
- dispatch simulation visible

## Hackathon Deliverables

- demo video ready
- written problem statement
- written solution statement
- Bob usage statement
- code repository
- `bob_sessions/` folder included
- exported Bob reports included
- Bob session screenshots included

---

# 17. CI/CD Folder Structure

```text
.github/
└── workflows/
    ├── ci.yml
    └── deploy-code-engine.yml optional
```

---

# 18. Local Pre-Commit Checklist

Before pushing:

```bash
cd services/backend
pytest

cd ../../apps/web-app
npm run build
```

Also check:

```text
.env is not staged
bob_sessions folder has exports
README still accurate
```

---

# 19. Bob Usage for CI/CD

Use IBM Bob to:

- generate GitHub Actions workflow
- create Dockerfiles
- debug failed CI logs
- generate deployment instructions
- produce `.env.example`
- write README deployment section

## Bob Prompt Example

```text
Using the CrisisGrid AI monorepo structure, generate a GitHub Actions CI workflow that:
1. runs FastAPI backend tests
2. builds the Next.js frontend
3. uses PostgreSQL service for tests
4. does not expose secrets
```

---

# 20. Fallback Plan

If CI/CD becomes a blocker:

Do not waste hackathon time.

Fallback to:

```text
manual local run
manual tests
screen-recorded demo
clear README
Bob session proof
```

This is acceptable as long as the product flow works.

---

## Final CI/CD Principle

The pipeline exists to protect the demo.

Do not build DevOps complexity that prevents product completion.

For the hackathon, the winning path is:

```text
working MVP + passing basic checks + clear demo + Bob proof
```
