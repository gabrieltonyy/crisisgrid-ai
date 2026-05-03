# CrisisGrid AI — Coding Standards

## Purpose

This document defines coding standards for CrisisGrid AI.

The goal is to keep the codebase:

- readable
- modular
- easy to debug
- easy for IBM Bob to extend
- consistent across frontend, backend, agents, and documentation

Because this is a solo hackathon build, the standards should improve speed instead of slowing development.

---

## Core Engineering Principle

```text
Build simple, clear, demo-ready code first.
Refactor only when it improves clarity or reduces risk.
```

Do not over-engineer early.

---

# 1. General Coding Rules

## 1.1 Keep Functions Small

Each function should do one clear thing.

Good:

```python
def calculate_fire_radius(confidence_score: float) -> int:
    return 500
```

Avoid:

```python
def process_everything(report):
    # validates, verifies, clusters, alerts, dispatches, saves logs
```

---

## 1.2 Use Clear Names

Use names that explain the crisis domain.

Good:

```text
confidence_score
risk_radius_meters
incident_status
dispatch_status
```

Avoid:

```text
score
radius
status2
data
thing
```

---

## 1.3 Separate Layers

Do not mix:

- API routes
- business logic
- database logic
- agent logic
- frontend display logic

Example backend separation:

```text
routes → orchestrator → agents / decision engine → repositories → database
```

---

## 1.4 Prefer Explicitness

This project involves emergency decisions.

Avoid hidden magic.

Good:

```python
FIRE_ALERT_THRESHOLD = 0.60
```

Avoid:

```python
if score > config["x"]:
```

unless the config is clearly named and documented.

---

# 2. Backend Standards

## Backend Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Optional Cloudant

---

## 2.1 FastAPI Route Standards

Routes should be thin.

Good route:

```python
@router.post("/reports")
async def create_report(request: CrisisReportCreateRequest):
    return await report_service.create_report(request)
```

Bad route:

```python
@router.post("/reports")
async def create_report(request):
    # validate
    # save DB
    # run agents
    # calculate confidence
    # create alerts
    # dispatch
```

---

## 2.2 Service Layer

Business logic should live in service/orchestrator classes.

Example:

```text
ReportService
ReportOrchestrator
CredibilityEngine
ThresholdPolicy
IncidentClusteringService
```

---

## 2.3 Repository Layer

Database operations should live in repositories.

Example:

```python
class ReportRepository:
    async def create(self, report_data):
        ...

    async def find_by_id(self, report_id):
        ...
```

Avoid raw database calls directly in route handlers.

---

## 2.4 Pydantic Validation

Every API request should use a Pydantic schema.

Example:

```python
class CrisisReportCreateRequest(BaseModel):
    crisis_type: CrisisType
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
```

---

## 2.5 Error Handling

Use consistent errors.

Example:

```json
{
  "success": false,
  "message": "Validation failed",
  "error": {
    "code": "VALIDATION_ERROR",
    "details": "Latitude is required"
  }
}
```

Do not expose stack traces to users.

---

# 3. Agent Coding Standards

## 3.1 Agent Responsibility Rule

Each agent must have one primary responsibility.

| Agent | Responsibility |
|---|---|
| Verification Agent | credibility and crisis classification |
| GeoRisk Agent | radius and clustering |
| Alert Agent | user-facing alert creation |
| Dispatch Agent | authority notification payload |
| Advisory Agent | safety guidance |
| Weather Agent | environmental context |
| Wildlife Agent | wildlife threat evaluation |

---

## 3.2 Agent Interface Standard

Each agent should follow a consistent interface:

```python
class VerificationAgent:
    async def run(self, input_data: VerificationAgentInput) -> VerificationAgentOutput:
        ...
```

---

## 3.3 Agent Outputs Must Be Explainable

Every agent output should include:

- result values
- confidence or score if applicable
- human-readable summary

Example:

```json
{
  "initial_confidence_score": 0.68,
  "verification_summary": "Image and description strongly indicate a fire incident."
}
```

---

## 3.4 Agent Logging

Every agent run must be logged.

Minimum fields:

```text
report_id
incident_id
agent_name
input_summary
output_summary
status
duration_ms
created_at
```

This supports demo explainability.

---

# 4. Decision Engine Standards

## 4.1 Keep Scoring Logic Separate

Scoring should not be hidden inside the Verification Agent.

Use:

```text
decision_engine/credibility_engine.py
decision_engine/threshold_policy.py
decision_engine/incident_clustering.py
```

---

## 4.2 Crisis-Specific Thresholds

Thresholds should be named clearly.

Example:

```python
CRISIS_THRESHOLDS = {
    "FIRE": {
        "alert_threshold": 0.60,
        "dispatch_threshold": 0.65,
        "provisional_critical_allowed": True
    },
    "FLOOD": {
        "alert_threshold": 0.70,
        "dispatch_threshold": 0.75,
        "provisional_critical_allowed": False
    }
}
```

---

## 4.3 Fire Handling Rule

Fire can trigger provisional critical action.

```text
If fire confidence >= 0.60:
    status = PROVISIONAL_CRITICAL
    create alert
```

Do not wait for multiple reports when urgent response is needed.

---

## 4.4 Flood Handling Rule

Flood confidence should improve with:

- weather signal
- multiple nearby reports
- geospatial clustering

---

# 5. Frontend Standards

## Frontend Stack

- React / Next.js
- TypeScript
- Tailwind CSS
- Reusable components

---

## 5.1 Component Structure

Use feature-based folders.

```text
components/
├── reports/
├── alerts/
├── dashboard/
├── map/
└── common/
```

---

## 5.2 Component Naming

Use PascalCase.

Good:

```text
ReportForm.tsx
IncidentMap.tsx
AlertCard.tsx
DashboardSummary.tsx
```

Avoid:

```text
form.tsx
thing.tsx
component1.tsx
```

---

## 5.3 API Client

All API calls should go through one API client.

```text
src/lib/api-client.ts
```

Avoid calling `fetch()` directly in many components.

---

## 5.4 UI Clarity

Emergency UI should be:

- simple
- readable
- calm
- high contrast
- action-oriented

Avoid cluttered screens.

---

## 5.5 Alert UI

Alert messages must be clear.

Good:

```text
Fire reported nearby. Avoid the area and follow official instructions.
```

Avoid:

```text
Disaster confirmed! Immediate danger everywhere!
```

---

# 6. TypeScript Standards

## 6.1 Use Interfaces for API Types

Example:

```ts
export interface IncidentSummary {
  incident_id: string;
  crisis_type: CrisisType;
  status: IncidentStatus;
  confidence_score: number;
  severity: SeverityLevel;
}
```

---

## 6.2 Avoid `any`

Avoid:

```ts
const data: any = response.data;
```

Prefer:

```ts
const data: IncidentSummary[] = response.data;
```

---

# 7. Naming Conventions

## Backend Python

Use snake_case.

```text
confidence_score
risk_radius_meters
report_orchestrator
```

## Frontend TypeScript

Use camelCase for variables.

```text
confidenceScore
riskRadiusMeters
incidentStatus
```

## Database

Use snake_case.

```text
confidence_score
risk_radius_meters
created_at
```

## Files

Use lowercase snake_case for Python files.

```text
verification_agent.py
report_orchestrator.py
credibility_engine.py
```

Use PascalCase for React components.

```text
ReportForm.tsx
IncidentMap.tsx
```

---

# 8. API Standards

## 8.1 Version APIs

Use:

```text
/api/v1
```

## 8.2 Use RESTful Naming

Good:

```text
POST /reports
GET /reports/{report_id}
GET /alerts/nearby
GET /dashboard/incidents
```

Avoid:

```text
POST /do-report
GET /getAllThings
```

---

## 8.3 Consistent Response Format

Success:

```json
{
  "success": true,
  "message": "Report submitted successfully",
  "data": {}
}
```

Failure:

```json
{
  "success": false,
  "message": "Something went wrong",
  "error": {}
}
```

---

# 9. Database Standards

## 9.1 Use UUIDs

Use UUIDs for:

- users
- reports
- incidents
- alerts
- dispatch logs
- agent runs

---

## 9.2 Use created_at and updated_at

Every major table should include:

```text
created_at
updated_at
```

---

## 9.3 Store Score Components

Do not store only the final confidence score.

Store components where useful:

```text
media_evidence_score
cross_report_score
external_signal_score
geo_time_consistency_score
reporter_trust_score
```

This makes the system explainable.

---

# 10. Security Coding Standards

## 10.1 Never Hardcode Secrets

Never write API keys directly in code.

Use:

```text
.env
.env.example
environment variables
```

---

## 10.2 File Upload Safety

Use:

- file size limits
- MIME type checks
- UUID filenames
- safe upload paths

---

## 10.3 Validate Inputs

Validate:

- latitude
- longitude
- crisis type
- description length
- image type
- role permissions

---

# 11. Testing Standards

## 11.1 Test Critical Logic First

Priority tests:

- credibility score calculation
- crisis threshold decisions
- incident clustering
- advisory outputs
- report submission endpoint

---

## 11.2 Example Test Names

```text
test_fire_report_triggers_provisional_critical
test_flood_confidence_increases_with_cross_reports
test_low_confidence_report_does_not_dispatch
test_wildlife_report_creates_large_radius
```

---

# 12. Documentation Standards

Every major folder should have a short README when useful.

Minimum docs:

```text
README.md
docs/product/*
docs/architecture/*
docs/api/*
docs/demo/*
bob_sessions/README.md
```

---

## 12.1 Comments

Use comments only where they explain why.

Good:

```python
# Fire uses a lower threshold because delayed response is more dangerous than provisional warning.
```

Avoid:

```python
# increment i by 1
```

---

# 13. IBM Bob Usage Standards

When using IBM Bob:

## Good Prompts

Ask Bob to:

- create files using the established structure
- follow these coding standards
- use existing schemas
- write tests for generated logic
- explain any assumptions

## Avoid

Do not paste real secrets into Bob.

Do not ask Bob to use services it cannot access directly without giving it a fallback plan.

---

## Bob Tool Access Rule

If Bob cannot access a required tool, API, dashboard, or cloud service, it should:

1. explain what access is missing
2. guide the developer step-by-step to create or configure it
3. list required environment variables
4. provide mock fallback code
5. avoid requesting real keys in the prompt

---

# 14. Solo Workflow Standards

Because this is a solo project:

## Work in Small Increments

Suggested order:

```text
1. Create backend health endpoint
2. Create report endpoint
3. Add verification logic
4. Add georisk logic
5. Add alert generation
6. Add dashboard view
7. Add demo seed data
8. Polish README and pitch
```

---

## Commit Often

Use clear commit messages.

Examples:

```text
feat: add crisis report submission endpoint
feat: implement fire provisional critical threshold
docs: add system architecture
test: add credibility engine tests
```

---

# 15. Code Review Checklist

Before final submission:

- routes are clean
- agents have focused responsibilities
- no secrets committed
- README explains how to run
- Bob sessions exported
- demo data works
- confidence scores are visible
- dashboard shows incident status
- dispatch is simulated clearly
- safety advice is safe and bounded

---

## Final Coding Principle

Write code that a judge can understand quickly.

The best hackathon code is not the most complex.

It is the code that clearly proves:

```text
report → verify → cluster → alert → dispatch → explain
```
