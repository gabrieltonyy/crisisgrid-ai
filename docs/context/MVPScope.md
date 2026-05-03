# CrisisGrid AI — MVP Scope

## Purpose

This document defines the **Minimum Viable Product (MVP)** scope for CrisisGrid AI for the hackathon.

The MVP must:

- demonstrate the full end-to-end flow
- be reliable during demo
- showcase AI + multi-agent value
- be achievable by a solo developer within limited time and considerate of the 40bob coins

---

## Core MVP Principle

```text
Build the smallest system that clearly proves:
report → verify → cluster → alert → dispatch → dashboard
```

---

# 1. MVP Goals

The MVP must demonstrate:

- citizen report intake
- AI verification & scoring
- geospatial risk mapping (basic)
- alert generation
- simulated authority dispatch
- simple dashboard visibility

---

# 2. In-Scope Features (Must Have)

## 2.1 Authentication (Lightweight)

- Demo mode auth (no complex setup)
- Optional: simple JWT or mock user

---

## 2.2 Crisis Report Submission

- Form with:
  - crisis_type (FIRE, FLOOD, WILDLIFE)
  - description
  - latitude & longitude
  - optional image upload
- POST /reports endpoint

---

## 2.3 Verification Engine (Core)

- Keyword-based classification
- Media presence boost
- GPS validation
- Initial confidence score
- Basic duplicate detection

---

## 2.4 GeoRisk Mapping (Basic)

- Assign risk radius by crisis type:
  - FIRE → 500m
  - FLOOD → 1000m
  - WILDLIFE → 1500m
- Simple clustering:
  - same type + nearby + recent

---

## 2.5 Decision Engine

- Apply thresholds:
  - FIRE → faster escalation
  - FLOOD → requires more signals
- Determine:
  - status (NEEDS_CONFIRMATION, PROVISIONAL, VERIFIED, PROVISIONAL_CRITICAL)
  - should_alert
  - should_dispatch

---

## 2.6 Alert System

- Generate alert message
- Store alerts
- Display alerts in UI

---

## 2.7 Dispatch Simulation

- Map crisis → authority:
  - FIRE → FIRE_SERVICE
  - FLOOD → DISASTER_MANAGEMENT
  - WILDLIFE → WILDLIFE_AUTHORITY
- Store dispatch logs
- Mark as SIMULATED_SENT

---

## 2.8 Advisory System

- Return basic safety guidance
- Based on crisis type

---

## 2.9 Dashboard (Simple)

- List of incidents
- Show:
  - crisis type
  - confidence score
  - status
  - severity
  - dispatch status

---

## 2.10 Agent Run Logging

- Log each agent execution
- Store:
  - agent name
  - input summary
  - output summary
  - duration

---

# 3. Nice-to-Have (If Time Allows)

- map visualization (Google Maps / Mapbox)
- multiple report confirmation UI
- trust score display
- simple heatmap
- basic filtering (by crisis type)

---

# 4. Out of Scope (For Hackathon MVP)

Do NOT build:

- real authority integrations
- real SMS sending
- full auth systems (OAuth, SSO)
- complex ML models
- IoT/sensor integrations
- satellite data integration
- advanced predictive analytics

---

# 5. Demo Scenarios Covered

The MVP must support:

## Fire Scenario

- single report triggers immediate alert
- provisional critical status
- dispatch simulated

## Flood Scenario

- multiple reports increase confidence
- clustering visible
- alert triggered

## Wildlife Scenario (Optional but recommended)

- large radius
- correct authority mapping

---

# 6. Backend Scope

## Required Endpoints

```text
POST /reports
GET /reports/{id}
GET /reports/nearby
POST /reports/{id}/confirm (optional)
GET /alerts
GET /dashboard/incidents
GET /agent-runs
```

---

## Core Services

- ReportService
- VerificationAgent
- GeoRiskAgent
- DecisionEngine
- AlertAgent
- DispatchAgent
- AdvisoryAgent

---

# 7. Frontend Scope

## Pages

- Report Submission Page
- Alerts Page
- Dashboard Page

## Components

- ReportForm
- AlertCard
- IncidentList
- DashboardTable

---

# 8. Data Requirements

Minimum data:

- sample reports
- sample incidents
- sample alerts
- sample dispatch logs

Optional:

- seed script to preload demo data

---

# 9. Performance Expectations

For MVP:

- response time < 2 seconds (local)
- no blocking UI
- simple async handling

---

# 10. Reliability Requirements

The system must:

- not crash during demo
- handle missing optional services
- gracefully degrade

Example:

```text
Weather API unavailable → continue without it
```

---

# 11. IBM Alignment

MVP must show:

- agent-based architecture
- structured workflows
- use of AI concepts
- optional IBM service hooks (Cloudant, watsonx)

---

# 12. Solo Execution Strategy

Focus order:

```text
1. Backend report flow
2. Verification logic
3. Decision engine
4. Alerts + dispatch
5. Dashboard
6. Demo polish
```

---

# 13. Success Criteria

MVP is successful if:

- report submission works
- confidence score is visible
- alerts are generated
- dispatch logs are shown
- dashboard reflects incidents
- demo scenarios run smoothly

---

# 14. Final MVP Principle

```text
A simple, working system that clearly demonstrates value
is better than a complex incomplete system.
```
