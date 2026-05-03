# CrisisGrid AI — API Specification

## Purpose

This document defines the backend API contract for CrisisGrid AI.

The API is designed for a solo hackathon MVP, but structured so it can later scale into a full crisis intelligence platform.

The API supports:

- crisis reporting
- agent-based verification
- incident clustering
- nearby alerts
- authority dispatch simulation
- safety guidance
- dashboard views
- agent run explainability

---

## API Design Principles

- Use simple REST endpoints for MVP.
- Keep request and response payloads consistent.
- Every report should trigger the agent processing pipeline.
- Every major agent action should be logged.
- Responses should expose confidence, severity and status clearly.
- Avoid collecting unnecessary personal information.

---

## Base URL

Local development:

```text
http://localhost:8000/api/v1
```

Production/staging placeholder:

```text
https://api.crisisgrid.ai/api/v1
```

---

## Common Response Format

All API responses should follow this structure:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {}
}
```

Error response:

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

---

## Core Status Values

### Report / Incident Status

```text
PENDING_VERIFICATION
NEEDS_CONFIRMATION
PROVISIONAL_CRITICAL
VERIFIED
DISPATCHED
RESOLVED
FALSE_REPORT
```

### Crisis Types

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

### Severity Levels

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

# 1. Authentication APIs

For MVP, authentication can be simple or simulated.

If time allows, use Firebase Auth.

---

## 1.1 Register User

```http
POST /auth/signup
```

### Request

```json
{
  "name": "Demo User",
  "email": "demo@example.com",
  "password": "password123",
  "role": "CITIZEN"
}
```

### Response

```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user_id": "USR-001",
    "name": "Demo User",
    "email": "demo@example.com",
    "role": "CITIZEN",
    "trust_score": 0.50
  }
}
```

---

## 1.2 Login User

```http
POST /auth/login
```

### Request

```json
{
  "email": "demo@example.com",
  "password": "password123"
}
```

### Response

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "demo-token",
    "user": {
      "user_id": "USR-001",
      "role": "CITIZEN"
    }
  }
}
```

---

# 2. Report APIs

---

## 2.1 Submit Crisis Report

```http
POST /reports
```

### Purpose

Creates a new crisis report and triggers the agent processing pipeline.

### Request Type

Use `multipart/form-data` if uploading an image.

### Request Fields

```text
crisis_type: FIRE | FLOOD | WILDLIFE | ACCIDENT | SECURITY | HEALTH | OTHER
description: string
latitude: number
longitude: number
location_text: string optional
image: file optional
anonymous: boolean optional
```

### Example Request Body

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

### Processing Flow

```text
1. API receives report
2. Store report as PENDING_VERIFICATION
3. ReportOrchestrator starts agent pipeline
4. Verification Agent calculates initial confidence
5. GeoRisk Agent checks risk radius and clustering
6. Context Agent adds weather/wildlife signal if applicable
7. Decision Engine applies thresholds
8. Alert/Dispatch/Advisory outputs are generated
9. Final report status is returned
```

### Response

```json
{
  "success": true,
  "message": "Report submitted and processed",
  "data": {
    "report_id": "REP-001",
    "incident_id": "INC-001",
    "status": "PROVISIONAL_CRITICAL",
    "crisis_type": "FIRE",
    "confidence_score": 0.72,
    "severity_score": 0.85,
    "risk_radius_meters": 500,
    "actions": [
      "ALERT_CREATED",
      "DISPATCH_SIMULATED",
      "SAFETY_ADVICE_GENERATED"
    ]
  }
}
```

---

## 2.2 Get Report Details

```http
GET /reports/{report_id}
```

### Response

```json
{
  "success": true,
  "message": "Report retrieved",
  "data": {
    "report_id": "REP-001",
    "incident_id": "INC-001",
    "crisis_type": "FIRE",
    "description": "Smoke and flames near a building",
    "image_url": "/uploads/fire.jpg",
    "latitude": -1.2921,
    "longitude": 36.8219,
    "status": "PROVISIONAL_CRITICAL",
    "confidence_score": 0.72,
    "severity_score": 0.85,
    "risk_radius_meters": 500,
    "created_at": "2026-05-01T10:20:00Z"
  }
}
```

---

## 2.3 Get Nearby Reports / Incidents

```http
GET /reports/nearby?lat=-1.2921&lng=36.8219&radius=2000
```

### Purpose

Returns active incidents near a user.

### Query Parameters

```text
lat: number required
lng: number required
radius: number required, meters
crisis_type: optional
min_confidence: optional
```

### Response

```json
{
  "success": true,
  "message": "Nearby incidents retrieved",
  "data": [
    {
      "incident_id": "INC-001",
      "crisis_type": "FIRE",
      "status": "PROVISIONAL_CRITICAL",
      "confidence_score": 0.72,
      "severity": "HIGH",
      "latitude": -1.2921,
      "longitude": 36.8219,
      "risk_radius_meters": 500,
      "distance_meters": 350,
      "alert_message": "Fire reported nearby. Avoid the area."
    }
  ]
}
```

---

## 2.4 Confirm Report / Incident

```http
POST /reports/{report_id}/confirm
```

### Purpose

Allows a user to confirm or dispute a crisis report.

This is important for credibility scoring because independent confirmations increase confidence.

### Request

```json
{
  "confirmation_type": "CONFIRM",
  "comment": "I can see smoke from this area too",
  "latitude": -1.2919,
  "longitude": 36.8221
}
```

### Confirmation Types

```text
CONFIRM
DISPUTE
UPDATE_LOCATION
RESOLVED
```

### Processing Flow

```text
1. Save confirmation
2. Check if confirmation is independent
3. Recalculate confidence score
4. Update incident status if threshold is crossed
5. Trigger alert/dispatch if needed
```

### Response

```json
{
  "success": true,
  "message": "Confirmation recorded",
  "data": {
    "report_id": "REP-001",
    "incident_id": "INC-001",
    "updated_confidence_score": 0.84,
    "updated_status": "VERIFIED"
  }
}
```

---

# 3. Incident APIs

Reports are individual submissions.

Incidents are clustered crisis events.

Multiple reports can belong to one incident.

---

## 3.1 Get Incident Details

```http
GET /incidents/{incident_id}
```

### Response

```json
{
  "success": true,
  "message": "Incident retrieved",
  "data": {
    "incident_id": "INC-001",
    "crisis_type": "FIRE",
    "status": "VERIFIED",
    "confidence_score": 0.84,
    "severity_score": 0.85,
    "risk_radius_meters": 500,
    "report_count": 3,
    "confirmation_count": 2,
    "latitude": -1.2921,
    "longitude": 36.8219,
    "created_at": "2026-05-01T10:20:00Z",
    "updated_at": "2026-05-01T10:35:00Z"
  }
}
```

---

## 3.2 Recalculate Incident Credibility

```http
POST /incidents/{incident_id}/recalculate
```

### Purpose

Manually or automatically recalculates confidence based on latest reports, confirmations and external signals.

### Response

```json
{
  "success": true,
  "message": "Incident credibility recalculated",
  "data": {
    "incident_id": "INC-001",
    "previous_confidence_score": 0.72,
    "new_confidence_score": 0.84,
    "status": "VERIFIED"
  }
}
```

---

## 3.3 Resolve Incident

```http
POST /incidents/{incident_id}/resolve
```

### Request

```json
{
  "resolution_note": "Fire response team has cleared the area",
  "resolved_by": "AUTH-001"
}
```

### Response

```json
{
  "success": true,
  "message": "Incident resolved",
  "data": {
    "incident_id": "INC-001",
    "status": "RESOLVED"
  }
}
```

---

# 4. Verification APIs

---

## 4.1 Verify Report

```http
POST /verify/report
```

### Purpose

Runs or re-runs the verification agent for a report.

### Request

```json
{
  "report_id": "REP-001"
}
```

### Response

```json
{
  "success": true,
  "message": "Verification completed",
  "data": {
    "report_id": "REP-001",
    "crisis_type": "FIRE",
    "initial_confidence_score": 0.68,
    "media_validity_score": 0.80,
    "description_match_score": 0.75,
    "verification_summary": "Image and description strongly indicate a fire incident."
  }
}
```

---

## 4.2 Get Verification Status

```http
GET /verify/status/{report_id}
```

### Response

```json
{
  "success": true,
  "message": "Verification status retrieved",
  "data": {
    "report_id": "REP-001",
    "status": "PROVISIONAL_CRITICAL",
    "confidence_score": 0.72,
    "last_verified_at": "2026-05-01T10:22:00Z"
  }
}
```

---

# 5. Alert APIs

---

## 5.1 Get Nearby Alerts

```http
GET /alerts/nearby?lat=-1.2921&lng=36.8219&radius=2000
```

### Response

```json
{
  "success": true,
  "message": "Nearby alerts retrieved",
  "data": [
    {
      "alert_id": "ALT-001",
      "incident_id": "INC-001",
      "title": "FIRE ALERT",
      "message": "Fire reported nearby. Avoid the area and follow official instructions.",
      "crisis_type": "FIRE",
      "severity": "HIGH",
      "distance_meters": 350,
      "created_at": "2026-05-01T10:23:00Z"
    }
  ]
}
```

---

## 5.2 Create Alert Manually

```http
POST /alerts
```

### Request

```json
{
  "incident_id": "INC-001",
  "title": "FIRE ALERT",
  "message": "Avoid Nairobi CBD area due to reported fire.",
  "target_radius_meters": 500
}
```

### Response

```json
{
  "success": true,
  "message": "Alert created",
  "data": {
    "alert_id": "ALT-001",
    "status": "ACTIVE"
  }
}
```

---

# 6. Dispatch APIs

---

## 6.1 Simulate Authority Dispatch

```http
POST /dispatch/simulate
```

### Purpose

Simulates sending an incident notification to the relevant authority.

### Request

```json
{
  "incident_id": "INC-001"
}
```

### Response

```json
{
  "success": true,
  "message": "Dispatch simulated",
  "data": {
    "dispatch_id": "DSP-001",
    "authority_type": "FIRE_SERVICE",
    "channel": "SIMULATED",
    "status": "SIMULATED_SENT",
    "message": "High-confidence fire incident reported near Nairobi CBD."
  }
}
```

---

## 6.2 Get Dispatch History

```http
GET /dispatch/history?incident_id=INC-001
```

### Response

```json
{
  "success": true,
  "message": "Dispatch history retrieved",
  "data": [
    {
      "dispatch_id": "DSP-001",
      "incident_id": "INC-001",
      "authority_type": "FIRE_SERVICE",
      "channel": "SIMULATED",
      "status": "SIMULATED_SENT",
      "sent_at": "2026-05-01T10:24:00Z"
    }
  ]
}
```

---

# 7. Safety Advice APIs

---

## 7.1 Get Safety Advice

```http
GET /advice?crisis_type=FIRE&severity=HIGH
```

### Response

```json
{
  "success": true,
  "message": "Safety advice retrieved",
  "data": {
    "crisis_type": "FIRE",
    "severity": "HIGH",
    "safety_steps": [
      "Move away from the affected area.",
      "Avoid smoke exposure.",
      "Follow official emergency instructions."
    ],
    "avoid_actions": [
      "Do not enter the building.",
      "Do not block emergency access routes."
    ]
  }
}
```

---

# 8. Dashboard APIs

---

## 8.1 Get Dashboard Incidents

```http
GET /dashboard/incidents?status=VERIFIED&crisis_type=FIRE
```

### Response

```json
{
  "success": true,
  "message": "Dashboard incidents retrieved",
  "data": [
    {
      "incident_id": "INC-001",
      "crisis_type": "FIRE",
      "status": "VERIFIED",
      "confidence_score": 0.84,
      "severity": "HIGH",
      "report_count": 3,
      "dispatch_status": "SIMULATED_SENT",
      "created_at": "2026-05-01T10:20:00Z"
    }
  ]
}
```

---

## 8.2 Get Dashboard Summary

```http
GET /dashboard/summary
```

### Response

```json
{
  "success": true,
  "message": "Dashboard summary retrieved",
  "data": {
    "total_reports": 25,
    "active_incidents": 8,
    "verified_incidents": 5,
    "provisional_critical": 2,
    "dispatches_sent": 4,
    "most_common_crisis_type": "FLOOD",
    "average_confidence_score": 0.76
  }
}
```

---

## 8.3 Get Hotspots

```http
GET /dashboard/hotspots
```

### Response

```json
{
  "success": true,
  "message": "Hotspots retrieved",
  "data": [
    {
      "area_name": "Nairobi CBD",
      "crisis_type": "FIRE",
      "incident_count": 3,
      "average_confidence": 0.81,
      "latitude": -1.2921,
      "longitude": 36.8219
    }
  ]
}
```

---

# 9. Agent Run APIs

---

## 9.1 Get Agent Runs for Report

```http
GET /agent-runs?report_id=REP-001
```

### Purpose

Shows how agents processed a report.

This is useful for:

- debugging
- explainability
- demo storytelling
- judge confidence

### Response

```json
{
  "success": true,
  "message": "Agent runs retrieved",
  "data": [
    {
      "agent_name": "verification_agent",
      "input_summary": "Fire report with image and GPS",
      "output_summary": "Confidence 0.68, crisis_type FIRE",
      "status": "SUCCESS",
      "duration_ms": 240,
      "created_at": "2026-05-01T10:21:00Z"
    },
    {
      "agent_name": "georisk_agent",
      "input_summary": "Location -1.2921, 36.8219",
      "output_summary": "Risk radius 500m, matched cluster INC-001",
      "status": "SUCCESS",
      "duration_ms": 110,
      "created_at": "2026-05-01T10:21:01Z"
    }
  ]
}
```

---

# 10. Health Check API

---

## 10.1 Health Check

```http
GET /health
```

### Response

```json
{
  "success": true,
  "message": "CrisisGrid API is running",
  "data": {
    "status": "UP",
    "version": "1.0.0"
  }
}
```

---

# 11. MVP Endpoint Priority

## Must Build First

```text
POST /reports
GET /reports/{report_id}
GET /reports/nearby
GET /alerts/nearby
GET /dashboard/incidents
GET /dashboard/summary
GET /agent-runs
GET /advice
```

## Build If Time Allows

```text
POST /reports/{report_id}/confirm
POST /dispatch/simulate
GET /dispatch/history
GET /dashboard/hotspots
POST /incidents/{incident_id}/resolve
```

## Can Be Simulated

```text
/auth/signup
/auth/login
/verify/report
/incidents/{incident_id}/recalculate
```

---

# 12. IBM Bob Usage for API Development

Use IBM Bob IDE to:

- generate FastAPI routes
- generate Pydantic request/response schemas
- generate service classes
- generate mock data
- write endpoint tests
- refactor API structure
- document endpoint usage

Save Bob task history exports in:

```text
bob_sessions/
```

---

## Final API Design Principle

The API should support the hackathon story:

```text
Citizen submits report
→ agents verify and score
→ incident is clustered
→ alert is created
→ dispatch is simulated
→ dashboard explains what happened
```

Build this flow first before adding extra endpoints.
