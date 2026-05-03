# CrisisGrid AI — User Stories (Final Engineering Version)

## Purpose

This document defines implementation-ready user stories with:
- Real-world scenarios (Kenya-focused)
- Backend/API mapping
- Agent responsibilities
- Event-driven flows

Each story is structured to be:
- directly translatable into code using IBM Bob
- usable for demo narration
- aligned with hackathon judging expectations

---

## CORE SYSTEM MODEL

Every user action follows this pipeline:

User Action → API → A2A Client → Agents → Decision → Output

---

## CITIZEN USER STORIES

### US-001: Report Crisis Incident (CORE FLOW)

API:
POST /reports

Payload:
{
  "image": "...",
  "description": "optional",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "timestamp": "..."
}

Agent Flow:
Client → A2A Gateway → Verification Agent → GeoRisk Agent → Context Agent

Outputs:
- report_id
- confidence_score
- crisis_type
- severity_score

Scenario — FIRE INCIDENT:
A user sees a building on fire in Nairobi CBD.

System:
- Detect fire → confidence 0.82
- Radius set to 500m
- Alert + dispatch triggered

---

### US-002: Report Flood Risk

Scenario — FLOODING:
User notices rising water levels.

System:
- Detect water
- Check rainfall
- Generate flood warning

---

### US-003: Report Wildlife Threat

Scenario — WILDLIFE ESCAPE:
User spots dangerous animal in residential area.

System:
- Classify animal
- Create danger zone
- Notify users + authorities

---

### US-004: View Nearby Incidents

API:
GET /reports/nearby?lat=...&lng=...&radius=...

Response:
- Incident type
- Confidence
- Severity
- Location

---

### US-005: Receive Alerts

Trigger:
IF user_distance < risk_radius AND confidence > threshold

Example:
⚠️ FIRE ALERT — 500m away — Avoid area

---

### US-006: Get Safety Advice

Examples:
FIRE → Evacuate immediately
FLOOD → Move to higher ground
WILDLIFE → Stay indoors

---

## AUTHORITY USER STORIES

### US-101: Receive Dispatch

Payload:
{
  "type": "FIRE",
  "location": "...",
  "confidence": 0.82,
  "severity": "HIGH"
}

---

## SYSTEM AGENTS

Verification Agent → Detect + score
GeoRisk Agent → Radius + clustering
Alert Agent → Notify users
Dispatch Agent → Notify authorities

---

## DEMO FLOWS

FIRE:
User → Upload → Verify → Alert → Dispatch

FLOOD:
User → Upload → Weather → Risk → Alert

WILDLIFE:
User → Upload → Classify → Alert

---

## SOLO BUILD PRIORITY

Build:
- Reporting
- Map
- Alerts
- Safety Advice

Skip:
- Complex ML
- Full integrations

---

## FINAL RULE

If it cannot be demoed clearly → do not build it
