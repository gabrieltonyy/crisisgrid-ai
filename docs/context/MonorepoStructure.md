# CrisisGrid AI — Monorepo Structure

## Purpose

This document defines the recommended monorepo structure for CrisisGrid AI.

The structure is optimized for:

- solo hackathon execution
- IBM Bob-assisted development
- clean separation of concerns
- fast MVP delivery
- future multi-service expansion
- easy judging and repository review

---

## Core Monorepo Principle

For the hackathon, keep the project simple but professional.

Use a structure that looks scalable, but avoid creating too many separate services too early.

Recommended approach:

```text
One main backend
One main web app
Shared schemas/docs
Infrastructure folder
Bob session evidence folder
```

---

# 1. Root Repository Structure

```text
crisisgrid-ai/
│
├── apps/
│   └── web-app/
│
├── services/
│   └── backend/
│
├── shared/
│   ├── schemas/
│   ├── constants/
│   └── examples/
│
├── infrastructure/
│   ├── docker/
│   ├── scripts/
│   └── deployment/
│
├── docs/
│   ├── product/
│   ├── architecture/
│   ├── api/
│   ├── security/
│   ├── demo/
│   └── prompts/
│
├── bob_sessions/
│
├── .env.example
├── .gitignore
├── README.md
└── docker-compose.yml
```

---

# 2. apps/web-app

## Purpose

Contains the citizen reporting interface and authority dashboard.

For solo MVP, use one React/Next.js app instead of separate citizen app and admin dashboard projects.

This reduces complexity while still allowing separate routes.

---

## Structure

```text
apps/web-app/
│
├── src/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── report/
│   │   │   └── page.tsx
│   │   ├── alerts/
│   │   │   └── page.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   └── incidents/
│   │       └── [id]/
│   │           └── page.tsx
│   │
│   ├── components/
│   │   ├── layout/
│   │   ├── map/
│   │   ├── reports/
│   │   ├── alerts/
│   │   ├── dashboard/
│   │   └── common/
│   │
│   ├── lib/
│   │   ├── api-client.ts
│   │   ├── config.ts
│   │   └── formatters.ts
│   │
│   ├── types/
│   │   └── crisisgrid.ts
│   │
│   └── styles/
│       └── globals.css
│
├── public/
├── package.json
├── next.config.js
├── tsconfig.json
└── README.md
```

---

## Web App Routes

```text
/                  → landing / live crisis map
/report            → citizen crisis report form
/alerts            → nearby alerts feed
/incidents/[id]    → incident detail page
/dashboard         → authority/admin dashboard
```

---

## Why One Web App?

Originally, CrisisGrid AI could have:

```text
mobile app
web dashboard
admin portal
```

But for a solo hackathon MVP, one responsive web app is better.

It allows you to demo:

- citizen report
- crisis map
- alert feed
- authority dashboard

without maintaining three separate frontends.

---

# 3. services/backend

## Purpose

Contains the FastAPI backend, APIs, agents, orchestration logic, database access, and integrations.

---

## Structure

```text
services/backend/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth_routes.py
│   │   │   ├── report_routes.py
│   │   │   ├── incident_routes.py
│   │   │   ├── alert_routes.py
│   │   │   ├── dispatch_routes.py
│   │   │   ├── advice_routes.py
│   │   │   ├── dashboard_routes.py
│   │   │   └── agent_run_routes.py
│   │   └── api_router.py
│   │
│   ├── agents/
│   │   ├── verification_agent.py
│   │   ├── georisk_agent.py
│   │   ├── weather_context_agent.py
│   │   ├── wildlife_agent.py
│   │   ├── alert_agent.py
│   │   ├── dispatch_agent.py
│   │   ├── advisory_agent.py
│   │   └── analytics_agent.py
│   │
│   ├── orchestrator/
│   │   └── report_orchestrator.py
│   │
│   ├── decision_engine/
│   │   ├── credibility_engine.py
│   │   ├── threshold_policy.py
│   │   └── incident_clustering.py
│   │
│   ├── schemas/
│   │   ├── common.py
│   │   ├── reports.py
│   │   ├── incidents.py
│   │   ├── alerts.py
│   │   ├── dispatch.py
│   │   ├── agents.py
│   │   └── dashboard.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── report.py
│   │   ├── incident.py
│   │   ├── alert.py
│   │   ├── dispatch_log.py
│   │   ├── agent_run.py
│   │   └── confirmation.py
│   │
│   ├── repositories/
│   │   ├── report_repository.py
│   │   ├── incident_repository.py
│   │   ├── alert_repository.py
│   │   ├── dispatch_repository.py
│   │   └── agent_run_repository.py
│   │
│   ├── integrations/
│   │   ├── cloudant_client.py
│   │   ├── weather_client.py
│   │   ├── watsonx_client.py
│   │   ├── sms_client.py
│   │   └── maps_client.py
│   │
│   ├── services/
│   │   ├── upload_service.py
│   │   ├── safety_playbook_service.py
│   │   ├── dashboard_service.py
│   │   └── seed_service.py
│   │
│   ├── database/
│   │   ├── session.py
│   │   ├── base.py
│   │   └── migrations/
│   │
│   └── utils/
│       ├── distance.py
│       ├── logger.py
│       ├── ids.py
│       └── time.py
│
├── tests/
│   ├── test_reports.py
│   ├── test_credibility_engine.py
│   ├── test_threshold_policy.py
│   ├── test_georisk_agent.py
│   └── test_advisory_agent.py
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

# 4. Agent Folder Design

## agents/

Each agent should be a focused class or function module.

Example:

```text
verification_agent.py
```

Should contain:

```python
class VerificationAgent:
    def run(self, input_data):
        ...
```

## Agents to Implement First

```text
verification_agent.py
georisk_agent.py
alert_agent.py
dispatch_agent.py
advisory_agent.py
```

## Agents to Add If Time Allows

```text
weather_context_agent.py
wildlife_agent.py
analytics_agent.py
```

---

# 5. Orchestrator Design

## orchestrator/report_orchestrator.py

This file coordinates the full report flow.

```text
submit report
→ run verification
→ run georisk
→ run context checks
→ apply credibility decision
→ create alert
→ simulate dispatch
→ generate safety advice
→ return final response
```

This file is central to the demo.

---

# 6. Decision Engine Folder

## Purpose

Keeps scoring and threshold logic separate from agents.

```text
decision_engine/
├── credibility_engine.py
├── threshold_policy.py
└── incident_clustering.py
```

## Files

### credibility_engine.py

Calculates:

```text
media evidence score
reporter trust score
cross-report score
geo/time consistency score
external signal score
final confidence score
```

### threshold_policy.py

Stores crisis-specific thresholds:

```text
FIRE alert threshold = 0.60
FIRE dispatch threshold = 0.65
FLOOD alert threshold = 0.70
```

### incident_clustering.py

Finds whether a new report belongs to an existing incident.

---

# 7. shared/

## Purpose

Contains project-wide shared definitions that can be copied or generated into backend and frontend.

```text
shared/
├── schemas/
│   ├── crisis_types.json
│   ├── incident_statuses.json
│   ├── api_examples.json
│   └── shared_contracts.md
│
├── constants/
│   ├── crisis_thresholds.json
│   └── demo_locations.json
│
└── examples/
    ├── fire_report.json
    ├── flood_report.json
    └── wildlife_report.json
```

---

# 8. infrastructure/

## Purpose

Contains local and deployment tooling.

```text
infrastructure/
├── docker/
│   ├── docker-compose.yml
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
│
├── scripts/
│   ├── seed_demo_data.py
│   ├── reset_db.py
│   └── export_demo_data.py
│
└── deployment/
    ├── ibm-code-engine.md
    ├── local-deployment.md
    └── environment-setup.md
```

---

# 9. docs/

## Purpose

Stores all planning, architecture, security, demo, and prompt documents.

```text
docs/
├── product/
│   ├── PRD.md
│   ├── Vision.md
│   ├── UserStories.md
│   ├── HackathonNarrative.md
│   └── CompetitiveAdvantage.md
│
├── architecture/
│   ├── SystemArchitecture.md
│   ├── AgentArchitecture.md
│   ├── DatabaseSchema.md
│   ├── SecurityArchitecture.md
│   ├── DeploymentArchitecture.md
│   └── SharedSchemas.md
│
├── api/
│   └── API_Specification.md
│
├── demo/
│   ├── DemoScenarios.md
│   ├── JudgePitchFlow.md
│   └── MVPScope.md
│
├── prompts/
│   ├── LeadSystemArchitectPrompt.md
│   ├── BackendAgentEngineerPrompt.md
│   ├── FrontendEngineerPrompt.md
│   ├── DevOpsPrompt.md
│   └── DocumentationPrompt.md
│
└── operations/
    ├── EnvironmentVariables.md
    ├── TestingStrategy.md
    ├── CI_CD_Pipeline.md
    └── ContributionGuide.md
```

---

# 10. bob_sessions/

## Purpose

This folder is required for hackathon evidence.

Store all exported IBM Bob task session reports here.

```text
bob_sessions/
├── screenshots/
│   ├── bob-session-architecture.png
│   ├── bob-session-backend.png
│   └── bob-session-frontend.png
│
├── exports/
│   ├── bob-architecture-session.md
│   ├── bob-backend-session.md
│   ├── bob-api-session.md
│   └── bob-frontend-session.md
│
└── README.md
```

---

## bob_sessions/README.md

Should explain:

```text
This folder contains exported IBM Bob task session reports and screenshots
showing how IBM Bob was used to design and build CrisisGrid AI.
```

This is critical for judging.

---

# 11. Root README.md

The root README should be clear and judge-friendly.

## Recommended Sections

```text
# CrisisGrid AI

## Problem
## Solution
## Demo Flow
## Architecture
## IBM Bob Usage
## Tech Stack
## How to Run Locally
## API Summary
## Screenshots
## Bob Session Reports
## Future Work
```

---

# 12. Root .env.example

```text
APP_ENV=local
API_BASE_URL=http://localhost:8000/api/v1
FRONTEND_URL=http://localhost:3000

DATABASE_URL=postgresql://crisisgrid:crisisgrid_password@localhost:5432/crisisgrid

CLOUDANT_URL=
CLOUDANT_API_KEY=
CLOUDANT_DB_REPORTS=crisis_reports_raw
CLOUDANT_DB_AGENT_LOGS=agent_payload_logs

WATSONX_API_KEY=
WATSONX_PROJECT_ID=
IBM_CLOUD_API_KEY=

GOOGLE_MAPS_API_KEY=
WEATHER_API_KEY=
SMS_API_KEY=

JWT_SECRET=replace_with_secure_value
```

---

# 13. Root .gitignore

```text
.env
.env.*
!.env.example

node_modules/
.next/
dist/
build/

.venv/
__pycache__/
*.pyc

service-account.json
credentials.json
*.pem
*.key

.DS_Store
.idea/
.vscode/
```

---

# 14. Solo MVP Build Order

## Step 1

Create repo folders:

```text
apps/web-app
services/backend
docs
shared
bob_sessions
```

## Step 2

Build backend skeleton:

```text
FastAPI app
health endpoint
reports endpoint
agent orchestrator
```

## Step 3

Build core agents:

```text
verification
georisk
alert
dispatch
advisory
```

## Step 4

Build frontend:

```text
report form
map/list view
alert feed
dashboard
```

## Step 5

Add demo data and polish.

---

# 15. IBM Bob Usage Plan

Use Bob to generate:

- folder structure
- FastAPI skeleton
- Pydantic schemas
- SQLAlchemy models
- agent modules
- React components
- dashboard UI
- tests
- README
- deployment scripts

## Important Bob Instruction

If Bob cannot access IBM Cloud, Cloudant, watsonx.ai, Maps, or other external tools directly, it should guide you through:

- creating the service
- generating API keys
- copying values into `.env`
- testing connectivity
- creating local fallback mocks

Bob should never ask you to paste real secrets into prompts.

---

# 16. Future Expansion Structure

After MVP, the monorepo can expand to:

```text
apps/
├── mobile-app/
├── web-dashboard/
└── admin-portal/

services/
├── a2a-client-gateway/
├── verification-agent/
├── georisk-agent/
├── dispatch-agent/
├── alert-agent/
└── analytics-agent/
```

But do not start with this structure during the hackathon unless the MVP is already working.

---

## Final Monorepo Principle

Build a repository that tells the whole story:

```text
docs explain the vision
backend proves the intelligence
frontend shows the impact
bob_sessions proves IBM Bob usage
```

That is what judges should see when they open the repo.


remember to keep the make the strcuture to be easy understandable which a human developer can be able to navigate the project read code and understand it.
