# CrisisGrid AI — Shared Schemas

## Purpose

This document defines the shared data schemas used across CrisisGrid AI.

These schemas keep the system consistent across:

- frontend forms
- backend APIs
- agent inputs and outputs
- database models
- dashboard views
- demo scenarios

For implementation, these schemas should be converted into:

- Pydantic models for FastAPI
- TypeScript interfaces for React/Next.js
- database models for persistence

---

## Design Principles

- Keep schemas simple for MVP.
- Use consistent naming across frontend and backend.
- Use enums for fixed values.
- Include confidence and status values in every crisis-related response.
- Avoid storing unnecessary personal data.
- Make agent outputs explainable.

---

# 1. Common Enums

## CrisisType

```text
FIRE
FLOOD
WILDLIFE
ACCIDENT
SECURITY
HEALTH
LANDSLIDE
HAZARDOUS_SPILL
OTHER
```

---

## IncidentStatus

```text
PENDING_VERIFICATION
NEEDS_CONFIRMATION
PROVISIONAL_CRITICAL
VERIFIED
DISPATCHED
RESOLVED
FALSE_REPORT
```

---

## SeverityLevel

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

## UserRole

```text
CITIZEN
AUTHORITY
ADMIN
SYSTEM
```

---

## ConfirmationType

```text
CONFIRM
DISPUTE
UPDATE_LOCATION
RESOLVED
```

---

## DispatchStatus

```text
PENDING
SIMULATED_SENT
SENT
FAILED
```

---

## AlertStatus

```text
ACTIVE
EXPIRED
CANCELLED
```

---

# 2. Location Schema

## Location

```json
{
  "latitude": -1.2921,
  "longitude": 36.8219,
  "location_text": "Nairobi CBD"
}
```

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| latitude | number | yes | Decimal latitude |
| longitude | number | yes | Decimal longitude |
| location_text | string | no | Human-readable location |

---

# 3. User Schemas

## UserProfile

```json
{
  "user_id": "USR-001",
  "name": "Demo User",
  "email": "demo@example.com",
  "role": "CITIZEN",
  "trust_score": 0.50,
  "status": "ACTIVE"
}
```

## Notes

For MVP, users can be simulated.

Do not expose unnecessary user identity in public views.

---

# 4. Crisis Report Schemas

## CrisisReportCreateRequest

Used when a citizen submits a report.

```json
{
  "crisis_type": "FIRE",
  "description": "Smoke and flames near a building",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "location_text": "Nairobi CBD",
  "anonymous": false
}
```

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| crisis_type | CrisisType | yes | User-selected or auto-detected |
| description | string | no | Short explanation |
| latitude | number | yes | GPS latitude |
| longitude | number | yes | GPS longitude |
| location_text | string | no | Optional label |
| anonymous | boolean | no | Hide reporter identity publicly |
| image | file | no | Multipart upload |

---

## CrisisReportResponse

```json
{
  "report_id": "REP-001",
  "incident_id": "INC-001",
  "crisis_type": "FIRE",
  "description": "Smoke and flames near a building",
  "image_url": "/uploads/fire.jpg",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "location_text": "Nairobi CBD",
  "status": "PROVISIONAL_CRITICAL",
  "confidence_score": 0.72,
  "severity_score": 0.85,
  "risk_radius_meters": 500,
  "created_at": "2026-05-01T10:20:00Z"
}
```

---

# 5. Incident Schemas

## Incident

An incident is a clustered real-world crisis event.

Multiple reports can belong to one incident.

```json
{
  "incident_id": "INC-001",
  "primary_report_id": "REP-001",
  "crisis_type": "FIRE",
  "title": "Fire reported near Nairobi CBD",
  "description": "Smoke and flames near a building",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "location_text": "Nairobi CBD",
  "status": "PROVISIONAL_CRITICAL",
  "confidence_score": 0.72,
  "severity_score": 0.85,
  "risk_radius_meters": 500,
  "report_count": 1,
  "confirmation_count": 0,
  "dispute_count": 0,
  "created_at": "2026-05-01T10:20:00Z",
  "updated_at": "2026-05-01T10:22:00Z"
}
```

---

## IncidentScoreComponents

```json
{
  "media_evidence_score": 0.25,
  "reporter_trust_score": 0.10,
  "cross_report_score": 0.15,
  "geo_time_consistency_score": 0.12,
  "external_signal_score": 0.10,
  "final_confidence_score": 0.72
}
```

## Scoring Formula

```text
Credibility Score =
(Media Evidence × 25%) +
(Reporter Trust × 15%) +
(Cross Reports × 25%) +
(Geo/Time Consistency × 15%) +
(External Signal × 20%)
```

---

## IncidentScoreHistory

```json
{
  "incident_id": "INC-001",
  "previous_score": 0.60,
  "new_score": 0.72,
  "reason": "Second independent report received nearby",
  "score_components": {
    "cross_report_score": 0.20
  },
  "created_at": "2026-05-01T10:30:00Z"
}
```

---

# 6. Confirmation Schema

## ConfirmationRequest

```json
{
  "confirmation_type": "CONFIRM",
  "comment": "I can also see smoke from this area",
  "latitude": -1.2919,
  "longitude": 36.8221
}
```

---

## ConfirmationResponse

```json
{
  "confirmation_id": "CNF-001",
  "report_id": "REP-001",
  "incident_id": "INC-001",
  "confirmation_type": "CONFIRM",
  "is_independent": true,
  "updated_confidence_score": 0.84,
  "updated_status": "VERIFIED"
}
```

---

# 7. Agent Task Schemas

## AgentTask

Generic task passed between the orchestrator and agents.

```json
{
  "task_id": "TASK-001",
  "report_id": "REP-001",
  "incident_id": "INC-001",
  "source_agent": "report_orchestrator",
  "target_agent": "verification_agent",
  "intent": "VERIFY_REPORT",
  "priority": "HIGH",
  "schema_version": "1.0",
  "payload": {},
  "timestamp": "2026-05-01T10:20:00Z"
}
```

---

## AgentResult

Generic response returned by an agent.

```json
{
  "task_id": "TASK-001",
  "agent_name": "verification_agent",
  "status": "SUCCESS",
  "confidence": 0.72,
  "outputs": {},
  "errors": [],
  "next_action": "RUN_GEORISK_AGENT",
  "duration_ms": 240
}
```

---

# 8. Verification Schemas

## VerificationAgentInput

```json
{
  "report_id": "REP-001",
  "crisis_type": "FIRE",
  "description": "Smoke and flames near a building",
  "image_url": "/uploads/fire.jpg",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "reporter_trust_score": 0.50,
  "nearby_similar_report_count": 0
}
```

---

## VerificationAgentOutput

```json
{
  "crisis_type": "FIRE",
  "media_validity_score": 0.80,
  "description_match_score": 0.75,
  "initial_confidence_score": 0.68,
  "duplicate_likelihood": 0.10,
  "verification_summary": "Image and description strongly indicate a fire incident.",
  "recommended_status": "PROVISIONAL_CRITICAL"
}
```

---

# 9. GeoRisk Schemas

## GeoRiskAgentInput

```json
{
  "report_id": "REP-001",
  "crisis_type": "FIRE",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "confidence_score": 0.68
}
```

---

## GeoRiskAgentOutput

```json
{
  "risk_radius_meters": 500,
  "matched_incident_id": "INC-001",
  "is_clustered": true,
  "cluster_report_count": 3,
  "geo_time_consistency_score": 0.15,
  "geospatial_summary": "Report is within 300m of an active fire incident."
}
```

---

# 10. Weather Context Schemas

## WeatherContextOutput

```json
{
  "weather_signal": "HEAVY_RAIN",
  "external_confirmation_score": 0.20,
  "summary": "Recent rainfall supports the reported flood risk."
}
```

---

# 11. Wildlife Schemas

## WildlifeAgentOutput

```json
{
  "species_guess": "LION",
  "threat_level": "HIGH",
  "recommended_radius_meters": 1500,
  "summary": "Potential dangerous wildlife reported near residential area."
}
```

---

# 12. Alert Schemas

## AlertMessage

```json
{
  "alert_id": "ALT-001",
  "incident_id": "INC-001",
  "title": "FIRE ALERT",
  "message": "Fire reported nearby. Avoid the area and follow official instructions.",
  "crisis_type": "FIRE",
  "severity": "HIGH",
  "target_radius_meters": 500,
  "latitude": -1.2921,
  "longitude": 36.8219,
  "status": "ACTIVE",
  "created_at": "2026-05-01T10:23:00Z"
}
```

---

## AlertDecision

```json
{
  "should_alert": true,
  "reason": "Confidence score meets FIRE alert threshold",
  "threshold_used": 0.60,
  "confidence_score": 0.72
}
```

---

# 13. Dispatch Schemas

## AuthorityDispatchRequest

```json
{
  "incident_id": "INC-001",
  "authority_type": "FIRE_SERVICE",
  "channel": "SIMULATED",
  "message": "High-confidence fire incident reported near Nairobi CBD.",
  "confidence_score": 0.72,
  "severity": "HIGH"
}
```

---

## AuthorityDispatchResponse

```json
{
  "dispatch_id": "DSP-001",
  "incident_id": "INC-001",
  "authority_type": "FIRE_SERVICE",
  "channel": "SIMULATED",
  "status": "SIMULATED_SENT",
  "sent_at": "2026-05-01T10:24:00Z"
}
```

---

# 14. Safety Advice Schemas

## SafetyAdvice

```json
{
  "crisis_type": "FIRE",
  "severity": "HIGH",
  "safety_steps": [
    "Move away from the affected area.",
    "Avoid smoke exposure.",
    "Follow official emergency instructions."
  ],
  "avoid_actions": [
    "Do not enter the affected building.",
    "Do not block emergency access routes."
  ],
  "source": "STATIC_PLAYBOOK"
}
```

---

# 15. Dashboard Schemas

## DashboardIncidentSummary

```json
{
  "incident_id": "INC-001",
  "crisis_type": "FIRE",
  "status": "PROVISIONAL_CRITICAL",
  "confidence_score": 0.72,
  "severity": "HIGH",
  "report_count": 1,
  "confirmation_count": 0,
  "dispatch_status": "SIMULATED_SENT",
  "created_at": "2026-05-01T10:20:00Z"
}
```

---

## DashboardSummary

```json
{
  "total_reports": 25,
  "active_incidents": 8,
  "verified_incidents": 5,
  "provisional_critical": 2,
  "dispatches_sent": 4,
  "most_common_crisis_type": "FLOOD",
  "average_confidence_score": 0.76
}
```

---

# 16. Agent Run Schema

## AgentRun

```json
{
  "agent_run_id": "RUN-001",
  "report_id": "REP-001",
  "incident_id": "INC-001",
  "agent_name": "verification_agent",
  "input_summary": "Fire report with image and GPS",
  "output_summary": "Confidence 0.68, crisis_type FIRE",
  "status": "SUCCESS",
  "confidence_before": 0.40,
  "confidence_after": 0.68,
  "duration_ms": 240,
  "created_at": "2026-05-01T10:21:00Z"
}
```

---

# 17. Error Schema

## ApiError

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Latitude is required",
  "details": {
    "field": "latitude"
  }
}
```

---

# 18. TypeScript Interface Example

```ts
export interface CrisisReportResponse {
  report_id: string;
  incident_id?: string;
  crisis_type: CrisisType;
  description?: string;
  image_url?: string;
  latitude: number;
  longitude: number;
  location_text?: string;
  status: IncidentStatus;
  confidence_score: number;
  severity_score: number;
  risk_radius_meters: number;
  created_at: string;
}
```

---

# 19. Pydantic Model Example

```python
from pydantic import BaseModel, Field
from typing import Optional

class CrisisReportCreateRequest(BaseModel):
    crisis_type: str
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    location_text: Optional[str] = None
    anonymous: bool = False
```

---

# 20. IBM Bob Usage

Use IBM Bob to generate:

- Pydantic schemas
- TypeScript interfaces
- validation rules
- enum classes
- API models
- database model mappings
- shared schema documentation

If Bob cannot access a tool or framework directly, it should guide the developer through:

- where to create the file
- what package to install
- what command to run
- what API key or environment variable is needed
- how to use a mock fallback

Bob should never ask for real secrets to be pasted into prompts.

---

## Final Schema Principle

Every major system object should be consistent across:

```text
API contract
database model
agent payload
frontend interface
demo output
```

This keeps CrisisGrid AI easier to build, test, explain, and judge.
