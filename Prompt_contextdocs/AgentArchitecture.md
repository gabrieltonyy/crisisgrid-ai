# CrisisGrid AI — Agent Architecture

## Purpose

This document defines the agent architecture for CrisisGrid AI.

The goal is to show how the platform converts a citizen crisis report into:

- verified intelligence
- location-aware risk analysis
- user alerts
- authority dispatch
- safety guidance

This architecture is designed for a **solo hackathon MVP**, while still presenting a scalable multi-agent design.

---

## Core Agent Design Principle

Each agent should have one clear responsibility.

The system should avoid one large “do everything” AI agent.

Instead, CrisisGrid AI uses focused agents that work together through an orchestration flow.

```text
Citizen Report
    ↓
A2A Client / Report Orchestrator
    ↓
Specialized Agents
    ↓
Decision Engine
    ↓
Alerts + Dispatch + Dashboard
```

---

## MVP Agent Implementation Strategy

For the hackathon MVP, agents should be implemented as internal backend modules inside one FastAPI service.

Recommended structure:

```text
services/backend/
├── agents/
│   ├── verification_agent.py
│   ├── georisk_agent.py
│   ├── alert_agent.py
│   ├── dispatch_agent.py
│   ├── advisory_agent.py
│   ├── weather_context_agent.py
│   └── wildlife_agent.py
├── orchestrator/
│   └── report_orchestrator.py
└── schemas/
    └── agent_schemas.py
```

This keeps the build realistic for one developer while still demonstrating multi-agent thinking.

---

## Agent Flow Overview

```text
1. User submits report
2. A2A Client / Report Orchestrator receives report
3. Verification Agent calculates initial credibility
4. GeoRisk Agent checks location and clustering
5. Context Agent adds weather or wildlife signals if applicable
6. Decision Engine applies crisis-specific thresholds
7. Alert Agent generates public alert if threshold is met
8. Dispatch Agent creates authority notification if threshold is met
9. Advisory Agent returns safety guidance
10. Agent run logs are saved for explainability
```

---

# 1. A2A Client Agent / Report Orchestrator

## Role

The A2A Client Agent acts as the entry point between the user request and the agent network.

For MVP, this can be implemented as `ReportOrchestrator`.

## Responsibilities

- Receive report payload from API
- Create report processing task
- Call agents in correct order
- Merge agent outputs
- Apply decision rules
- Update report status
- Save agent run logs

## Input

```json
{
  "report_id": "REP-001",
  "crisis_type": "FIRE",
  "description": "Smoke and flames near a building",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "image_url": "/uploads/fire.jpg",
  "created_at": "2026-05-01T10:20:00Z"
}
```

## Output

```json
{
  "report_id": "REP-001",
  "final_status": "PROVISIONAL_CRITICAL",
  "confidence_score": 0.72,
  "severity_score": 0.85,
  "actions": ["ALERT_CREATED", "DISPATCH_SIMULATED"]
}
```

## MVP Notes

This agent does not need a complex Google A2A setup initially.

It should behave like an A2A client by routing structured messages between internal agents.

---

# 2. Verification Agent

## Role

Determines whether the report is credible and assigns an initial confidence score.

## Responsibilities

- Classify crisis type
- Check description keywords
- Validate image presence
- Estimate media credibility
- Check duplicate likelihood
- Produce initial confidence score
- Produce verification summary

## Inputs

- crisis_type
- description
- image_url
- timestamp
- user trust score
- nearby similar reports

## Outputs

```json
{
  "agent_name": "verification_agent",
  "crisis_type": "FIRE",
  "media_validity_score": 0.80,
  "description_match_score": 0.75,
  "initial_confidence_score": 0.68,
  "verification_summary": "Image and description strongly indicate a fire incident."
}
```

## MVP Scoring Logic

For MVP, the verification agent can use rule-based logic.

Example:

```text
Base score = 0.40

+0.20 if image exists
+0.15 if description contains crisis keywords
+0.10 if GPS exists
+0.10 if reporter trust score is high
+0.15 if similar nearby reports exist
```

## Fire-Specific Behavior

Fire requires immediate handling.

If a fire report includes:

- image
- GPS
- fire/smoke/flame keywords

Then the agent can recommend:

```text
status = PROVISIONAL_CRITICAL
```

This allows immediate alerting while waiting for stronger confirmation.

---

# 3. GeoRisk Agent

## Role

Determines affected area and detects whether a new report belongs to an existing incident cluster.

## Responsibilities

- Calculate risk radius
- Find nearby incidents
- Cluster reports that describe the same event
- Estimate affected area
- Support location-based alert targeting

## Inputs

- latitude
- longitude
- crisis_type
- confidence_score
- existing active incidents

## Outputs

```json
{
  "agent_name": "georisk_agent",
  "risk_radius_meters": 500,
  "matched_incident_id": "INC-1001",
  "is_clustered": true,
  "cluster_report_count": 3,
  "geospatial_summary": "Report is within 300m of an active fire incident."
}
```

## Crisis Radius Rules

```text
FIRE       → 500m
FLOOD      → 1000m
WILDLIFE   → 1500m
ACCIDENT   → 300m
SECURITY   → 700m
```

## Clustering Rule

A new report should be linked to an existing incident when:

```text
same crisis_type
AND distance < crisis_cluster_radius
AND time_difference < crisis_time_window
```

Example time windows:

```text
FIRE       → 45 minutes
FLOOD      → 3 hours
WILDLIFE   → 2 hours
ACCIDENT   → 1 hour
```

## Why This Matters

Multiple independent reports should increase credibility.

Example:

```text
1 flood report  → 60% credibility
2 flood reports → 72%
3 flood reports → 85%
```

---

# 4. Weather Context Agent

## Role

Adds external weather or environmental context to reports, especially flooding and severe weather.

## Responsibilities

- Check rainfall status
- Check severe weather signal
- Add external confirmation score
- Improve confidence for flood reports

## Inputs

- crisis_type
- latitude
- longitude
- timestamp

## Outputs

```json
{
  "agent_name": "weather_context_agent",
  "weather_signal": "HEAVY_RAIN",
  "external_confirmation_score": 0.20,
  "summary": "Recent rainfall supports the reported flooding risk."
}
```

## MVP Strategy

If real weather API setup is too slow, simulate this agent with predefined weather responses for demo locations.

Example:

```text
If location = Nairobi and crisis_type = FLOOD:
    weather_signal = HEAVY_RAIN
```

---

# 5. Wildlife Agent

## Role

Evaluates dangerous wildlife reports.

## Responsibilities

- Classify reported animal type
- Estimate threat level
- Recommend safety radius
- Recommend authority type

## Inputs

- image_url
- description
- latitude
- longitude

## Outputs

```json
{
  "agent_name": "wildlife_agent",
  "species_guess": "LION",
  "threat_level": "HIGH",
  "recommended_radius_meters": 1500,
  "summary": "Potential dangerous wildlife reported near a residential area."
}
```

## MVP Strategy

Use manual selection or keyword-based logic.

Examples:

```text
description contains "lion" → threat_level = HIGH
description contains "snake" → threat_level = MEDIUM/HIGH
description contains "hyena" → threat_level = HIGH
```

---

# 6. Credibility / Decision Engine

## Role

Combines outputs from all agents and decides what action to take.

This is not a separate AI agent in the MVP, but it is a core system component.

## Responsibilities

- Combine verification score
- Add cross-report boost
- Add external signal boost
- Apply crisis-specific thresholds
- Set incident status
- Decide whether to alert or dispatch

## Credibility Formula

```text
Credibility Score =
(Media Evidence × 25%) +
(Reporter Trust × 15%) +
(Cross Reports × 25%) +
(Geo/Time Consistency × 15%) +
(External Signal × 20%)
```

## Crisis-Specific Thresholds

| Crisis Type | Alert Threshold | Dispatch Threshold | Special Handling |
|---|---:|---:|---|
| FIRE | 60% | 65% | Provisional critical allowed |
| FLOOD | 70% | 75% | Weather + cross-report boost |
| WILDLIFE | 65% | 70% | Local warning allowed |
| ACCIDENT | 65% | 70% | Fast local alert |
| SECURITY | 80% | 85% | Higher threshold to reduce panic |
| HEALTH | 85% | 90% | Prefer official confirmation |

## Incident Statuses

```text
PENDING_VERIFICATION
NEEDS_CONFIRMATION
PROVISIONAL_CRITICAL
VERIFIED
DISPATCHED
RESOLVED
FALSE_REPORT
```

## Fire Example

```text
Fire report confidence = 62%
Alert threshold = 60%

Result:
- status = PROVISIONAL_CRITICAL
- alert users immediately
- simulate dispatch
- wait for confirmation to upgrade to VERIFIED
```

## Flood Example

```text
Flood report confidence = 62%
Weather confirms heavy rain = +15%
Two independent nearby reports = +10%

Final confidence = 87%

Result:
- status = VERIFIED
- alert nearby users
- simulate dispatch
```

---

# 7. Alert Agent

## Role

Generates public-facing alerts for nearby users.

## Responsibilities

- Create alert title and message
- Determine target radius
- Store alert
- Display alert in app
- Optionally simulate SMS/push delivery

## Inputs

- incident_id
- crisis_type
- confidence_score
- severity_score
- risk_radius_meters
- safety_advice

## Outputs

```json
{
  "agent_name": "alert_agent",
  "alert_title": "FIRE ALERT",
  "alert_message": "Fire reported nearby. Avoid the area and follow official instructions.",
  "target_radius_meters": 500,
  "alert_status": "CREATED"
}
```

## Alert Tone

Alerts must be:

- short
- clear
- calm
- action-oriented
- not panic-inducing

---

# 8. Dispatch Agent

## Role

Creates structured authority notifications.

## Responsibilities

- Determine responsible authority type
- Generate dispatch payload
- Simulate SMS/email/API dispatch
- Log dispatch attempt

## Inputs

- verified incident
- location
- severity
- confidence
- crisis type

## Outputs

```json
{
  "agent_name": "dispatch_agent",
  "authority_type": "FIRE_SERVICE",
  "dispatch_status": "SIMULATED_SENT",
  "message": "High-confidence fire incident reported near Nairobi CBD."
}
```

## Authority Mapping

```text
FIRE       → FIRE_SERVICE
FLOOD      → DISASTER_MANAGEMENT
WILDLIFE   → WILDLIFE_AUTHORITY
ACCIDENT   → POLICE / AMBULANCE
SECURITY   → POLICE
HEALTH     → PUBLIC_HEALTH_OFFICE
```

---

# 9. Advisory Agent

## Role

Provides safe, bounded safety guidance to users.

## Responsibilities

- Return crisis-specific advice
- Avoid dangerous or overly technical instructions
- Keep guidance simple and calm
- Support optional watsonx.ai rewriting

## Inputs

- crisis_type
- severity
- user location context

## Outputs

```json
{
  "agent_name": "advisory_agent",
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
```

## MVP Safety Playbooks

### Fire

- Move away from the affected area.
- Avoid smoke.
- Do not enter the building.
- Give responders space.

### Flood

- Move to higher ground.
- Do not walk or drive through floodwater.
- Avoid drainage channels and river crossings.

### Wildlife

- Stay indoors if possible.
- Do not approach or provoke the animal.
- Keep children and pets inside.
- Report new sightings only from a safe distance.

---

# 10. Analytics Agent

## Role

Provides incident and response insights.

## MVP Responsibilities

- Count reports by crisis type
- Track verified vs unverified incidents
- Show average confidence
- Show dispatch count
- Show hotspot summary

## Outputs

```json
{
  "total_reports": 25,
  "verified_incidents": 12,
  "most_common_crisis": "FLOOD",
  "average_confidence": 0.78
}
```

## MVP Note

This can be a simple dashboard query layer rather than a complex AI agent.

---

# 11. Agent Run Logging

Every agent call should be logged.

## Why

- Explainability
- Debugging
- Demo storytelling
- Judge confidence
- Evidence of multi-agent processing

## Suggested Table

```text
agent_runs
- id
- report_id
- agent_name
- input_summary
- output_summary
- status
- duration_ms
- created_at
```

## Example

```json
{
  "report_id": "REP-001",
  "agent_name": "verification_agent",
  "input_summary": "Fire report with image and GPS",
  "output_summary": "Confidence 0.72, crisis_type FIRE",
  "status": "SUCCESS",
  "duration_ms": 240
}
```

---

# 12. IBM Bob Usage in Agent Development

IBM Bob should be used to build and document the agent system.

## Bob Tasks to Capture

- Generate initial agent folder structure
- Create Pydantic schemas for agent inputs/outputs
- Generate Verification Agent logic
- Generate GeoRisk Agent logic
- Generate Alert and Dispatch agents
- Refactor orchestrator flow
- Generate tests for threshold logic
- Generate this documentation

## Required Evidence

Save Bob task exports in:

```text
bob_sessions/
```

Include:

- task history markdown files
- screenshots of session summary
- notes on which files Bob helped build

---

# 13. MVP Agent Priority

## Build First

1. Report Orchestrator
2. Verification Agent
3. GeoRisk Agent
4. Alert Agent
5. Dispatch Agent
6. Advisory Agent

## Build If Time Allows

7. Weather Context Agent
8. Wildlife Agent
9. Analytics Agent

## Simulate If Necessary

- Weather API
- SMS dispatch
- Wildlife classification
- Push notifications

---

# 14. Demo Agent Flow

## Fire Demo

```text
Citizen uploads fire report
→ Verification Agent assigns 62%
→ Decision Engine marks PROVISIONAL_CRITICAL
→ Alert Agent creates nearby warning
→ Dispatch Agent logs fire-service notification
```

## Flood Demo

```text
Citizen uploads flood report
→ Verification Agent assigns 60%
→ Weather Agent adds external signal
→ GeoRisk Agent finds similar nearby reports
→ Credibility rises to 85%
→ Alert + dispatch triggered
```

## Wildlife Demo

```text
Citizen uploads wildlife sighting
→ Wildlife Agent classifies threat
→ GeoRisk Agent creates 1500m danger radius
→ Alert Agent warns residents
→ Dispatch Agent logs wildlife authority notification
```

---

## Final Agent Architecture Principle

CrisisGrid AI should not claim perfect AI verification.

It should demonstrate:

```text
Fast, explainable, multi-signal crisis credibility scoring.
```

That is more realistic, safer, and stronger for judging.
