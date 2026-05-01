# CrisisGrid AI — System Architecture

## Purpose

This document defines the technical architecture for CrisisGrid AI as a solo-build hackathon MVP.

The architecture is designed to be:

- Buildable by one developer
- Strong enough for a live demo
- Aligned with IBM Bob Dev Day expectations
- Easy to explain to judges
- Extensible after the hackathon

---

## Architecture Goal

CrisisGrid AI must demonstrate an end-to-end crisis intelligence flow:

```text
Citizen Report
    ↓
API Gateway / A2A Client Layer
    ↓
Agent Processing Layer
    ↓
Incident Intelligence Engine
    ↓
Alerts + Dispatch + Dashboard
```

The MVP should prove that a citizen report can be transformed into verified, actionable emergency intelligence.

---

## High-Level System Architecture

```text
┌──────────────────────────┐
│ Citizen Web / Mobile UI  │
│ Report + Map + Alerts    │
└─────────────┬────────────┘
              ↓
┌──────────────────────────┐
│ Backend API Gateway      │
│ FastAPI                  │
│ Report Intake            │
│ Auth                     │
│ Incident APIs            │
└─────────────┬────────────┘
              ↓
┌──────────────────────────┐
│ A2A Client Agent Layer   │
│ Orchestrates report flow │
└─────────────┬────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ Multi-Agent Processing Layer                │
│                                             │
│ - Verification Agent                        │
│ - GeoRisk Agent                             │
│ - Alert Agent                               │
│ - Dispatch Agent                            │
│ - Advisory Agent                            │
│ - Weather Context Agent (optional)          │
│ - Wildlife Agent (optional/stretch)         │
└─────────────┬───────────────────────────────┘
              ↓
┌──────────────────────────┐
│ Data Layer               │
│ PostgreSQL / PostGIS     │
│ Cloudant Optional        │
│ Redis Optional           │
└─────────────┬────────────┘
              ↓
┌──────────────────────────┐
│ Authority Dashboard      │
│ Incident Queue           │
│ Map View                 │
│ Simulated Dispatch Logs  │
└──────────────────────────┘
```

---

## Core Architecture Principle

For the hackathon MVP, the architecture should be modular but not unnecessarily distributed.

Instead of building many separate deployed microservices, implement the agents as modular internal services first.

Recommended MVP structure:

```text
One FastAPI backend
    ├── routes
    ├── services
    ├── agents
    ├── schemas
    ├── repositories
    └── integrations
```

This keeps development fast while still demonstrating a multi-agent design.

---

## Main System Components

---

## 1. Citizen Interface

### Purpose

Allows citizens to:

- Submit crisis reports
- Upload an image
- Capture location
- View nearby incidents
- Receive alerts
- Read safety guidance

### Recommended MVP Technology

- React / Next.js web app first
- Mobile-friendly responsive layout
- Flutter can be a future enhancement

### MVP Screens

- Home / Crisis Map
- Report Incident Form
- Incident Detail View
- Alert Feed
- Safety Advice Panel

### Why Web First?

Because you are building solo, a responsive web app is faster than building both mobile and web. It still demonstrates the full product flow.

---

## 2. Backend API Gateway

### Purpose

Central entry point for all user and dashboard actions.

### Recommended Technology

- Python FastAPI
- Pydantic schemas
- Async endpoints where useful

### Main Responsibilities

- Receive crisis reports
- Store reports
- Trigger agent pipeline
- Serve nearby incidents
- Serve alerts
- Serve dashboard data

### Core Endpoints

```text
POST /reports
GET  /reports/{report_id}
GET  /reports/nearby
POST /reports/{report_id}/confirm
GET  /alerts/nearby
GET  /dashboard/incidents
POST /dispatch/simulate
```

---

## 3. A2A Client Agent Layer

### Purpose

Acts as the bridge between user requests and specialized agents.

### Responsibilities

- Accept report payload
- Create an agent task
- Call required agents in order
- Merge outputs
- Return final decision

### MVP Implementation

For the hackathon, implement this as a Python orchestration service:

```text
ReportOrchestrator
    ├── run_verification()
    ├── run_georisk()
    ├── run_context_check()
    ├── run_alert_decision()
    └── run_dispatch_decision()
```

This gives the appearance and behavior of agent orchestration without requiring complex infrastructure.

---

## 4. Multi-Agent Processing Layer

The agents are modular services with clear responsibilities.

---

### 4.1 Verification Agent

### Purpose

Determines whether a crisis report is credible.

### Inputs

- Image URL or file
- Description
- Location
- Timestamp
- Reporter trust score

### Outputs

- crisis_type
- confidence_score
- media_validity
- duplicate_likelihood
- verification_summary

### MVP Logic

Use rule-based or mock AI classification first:

```text
If user selects FIRE → classify as FIRE
If image exists → increase confidence
If description mentions smoke/flames → increase confidence
If duplicate nearby report exists → increase confidence
```

Optional enhancement:

- watsonx.ai / IBM model for text classification
- Vision model integration if available

---

### 4.2 GeoRisk Agent

### Purpose

Calculates affected area and location-based risk.

### Inputs

- latitude
- longitude
- crisis_type
- severity_score

### Outputs

- risk_radius_meters
- affected_area
- nearby_users
- geospatial_summary

### MVP Logic

Example radius rules:

```text
FIRE     → 500m
FLOOD    → 1000m
WILDLIFE → 1500m
ACCIDENT → 300m
```

---

### 4.3 Alert Agent

### Purpose

Generates user-facing crisis alerts.

### Inputs

- crisis_type
- severity
- confidence
- affected radius
- location

### Outputs

- alert_title
- alert_message
- target_radius
- alert_status

### MVP Delivery

- Store alert in database
- Display alert in app
- Optional: simulate push/SMS

---

### 4.4 Dispatch Agent

### Purpose

Generates structured authority notification messages.

### Inputs

- verified report
- severity
- confidence
- location
- crisis type

### Outputs

- dispatch_payload
- authority_type
- dispatch_status

### MVP Delivery

Simulate dispatch by storing a dispatch log.

Example:

```json
{
  "authority_type": "FIRE_SERVICE",
  "message": "High confidence fire incident reported near Nairobi CBD.",
  "status": "SIMULATED_SENT"
}
```

---

### 4.5 Advisory Agent

### Purpose

Provides safe, bounded guidance to citizens.

### Inputs

- crisis_type
- severity

### Outputs

- safety_steps
- emergency_note
- avoid_actions

### MVP Logic

Start with predefined safety playbooks:

```text
FIRE:
- Move away from smoke.
- Do not enter the building.
- Follow official emergency instructions.

FLOOD:
- Move to higher ground.
- Avoid walking or driving through flood water.
- Stay away from drainage channels.

WILDLIFE:
- Stay indoors.
- Do not approach the animal.
- Report location updates from a safe distance.
```

Optional enhancement:

- watsonx.ai can rewrite safety guidance in simple user-friendly language.

---

### 4.6 Weather Context Agent Optional

### Purpose

Adds environmental context to flood or severe weather reports.

### MVP Options

- Use OpenWeatherMap if time allows
- Otherwise simulate weather confirmation

### Example

```text
Rainfall intensity: HIGH
Weather support signal: TRUE
Flood escalation probability: HIGH
```

---

### 4.7 Wildlife Agent Optional

### Purpose

Classifies wildlife sightings and estimates threat level.

### MVP Options

- Manual category selection
- Basic keyword detection
- Simulated species recognition

---

## 5. Data Layer

### Recommended MVP Database

Use PostgreSQL.

If PostGIS is available, use it for geospatial queries.

If setup time is limited, use normal latitude/longitude fields and calculate distance in application code.

### Main Tables

```text
users
reports
alerts
dispatch_logs
agent_runs
confirmations
```

### Important Stored Fields

Reports:

```text
id
crisis_type
description
image_url
latitude
longitude
status
confidence_score
severity_score
risk_radius_meters
created_at
```

Agent Runs:

```text
id
report_id
agent_name
input_summary
output_summary
status
duration_ms
created_at
```

Why store agent runs?

Because it proves the system is explainable and helps with demo storytelling.

---

## 6. Authority Dashboard

### Purpose

Gives officials/admins visibility into verified incidents.

### MVP Features

- Incident queue
- Severity sorting
- Confidence score display
- Location/map view
- Dispatch status
- Agent run summary

### Recommended Stack

- Same React/Next.js app as citizen UI
- Use admin route: `/dashboard`

---

## 7. IBM Bob Integration Architecture

IBM Bob is not just mentioned; it must be visible in the build process.

### Bob Usage Plan

Use Bob IDE to:

- Generate monorepo structure
- Scaffold FastAPI routes
- Generate Pydantic schemas
- Create React pages/components
- Refactor agent services
- Write tests
- Generate documentation
- Produce commit messages and PR descriptions

### Required Repository Folder

```text
bob_sessions/
```

This folder should contain:

- Exported Bob task history markdown files
- Screenshots of Bob task session summaries
- Notes explaining what Bob helped generate

---

## 8. Optional IBM Product Mapping

### IBM Bob IDE

Mandatory development assistant and proof of AI-assisted build.

### watsonx.ai

Use for:

- Safety advice enhancement
- Report text classification
- Alert wording generation
- Agent reasoning simulation

### watsonx Orchestrate

Use for:

- Optional agent workflow demonstration
- Simulated business process orchestration
- Future-ready architecture explanation

### IBM Cloudant

Can be used instead of PostgreSQL for quick NoSQL storage if database setup time is limited.

### IBM Code Engine

Can be used to deploy backend containers if time allows.

---

## 9. Security Architecture Summary

### MVP Controls

- Validate all incoming API payloads
- Limit image upload size
- Store secrets in `.env`
- Do not commit API keys
- Avoid personal data
- Use role-based access for dashboard
- Log all dispatch actions
- Use confidence thresholds before alerts

### Data Privacy

Do not collect unnecessary personal information.

For demo, use:

- synthetic users
- sample images
- demo locations
- simulated dispatch contacts

---

## 10. Event Flow: Report to Alert

```text
1. Citizen submits crisis report
2. API stores report as PENDING_VERIFICATION
3. A2A Client Agent starts processing
4. Verification Agent classifies crisis and confidence
5. GeoRisk Agent calculates risk radius
6. Advisory Agent generates safety steps
7. Alert Agent creates nearby alert if confidence is high
8. Dispatch Agent creates authority notification
9. Dashboard updates incident status
10. Demo user sees map marker, alert and guidance
```

---

## 11. MVP Architecture Scope

### Must Build

- FastAPI backend
- Report creation endpoint
- Agent orchestration service
- Verification Agent basic logic
- GeoRisk Agent basic logic
- Alert generation
- Advisory playbooks
- React dashboard/map
- Simulated dispatch logs

### Should Build if Time Allows

- Weather API integration
- Confirmation voting
- Trust score display
- Better dashboard analytics

### Do Not Build for MVP

- Full mobile app
- Real government integrations
- Real-time socket infrastructure
- Advanced computer vision model training
- Drone/IoT/satellite integrations

---

## 12. Demo Architecture Flow

### Demo 1: Flood

```text
User submits flood report
→ Verification Agent detects flood context
→ Weather Agent confirms rainfall or simulated risk
→ GeoRisk Agent creates flood radius
→ Alert Agent warns nearby users
→ Dispatch Agent logs authority notification
```

### Demo 2: Fire

```text
User submits fire image
→ Verification Agent marks FIRE
→ GeoRisk Agent sets 500m radius
→ Alert Agent warns users
→ Dispatch Agent notifies fire response in simulated log
```

### Demo 3: Wildlife

```text
User submits wildlife sighting
→ Wildlife Agent classifies threat
→ GeoRisk Agent creates danger zone
→ Alert Agent warns users
→ Dispatch Agent notifies wildlife authority in simulated log
```

---

## 13. Architecture Decision Summary

| Decision | Reason |
|---|---|
| Use one backend first | Faster solo delivery |
| Implement agents as modules | Easier to build and demo |
| Use simulated integrations | Avoid over-scoping |
| Use React web first | Faster than mobile + web |
| Store agent runs | Improves explainability |
| Use IBM Bob heavily | Required for judging alignment |

---

## Final Architecture Principle

Build a complete, visible crisis pipeline first.

Do not chase complex integrations before the core story works.

The winning demo is:

```text
Citizen sees danger → AI verifies → map updates → users warned → authority notified
```
