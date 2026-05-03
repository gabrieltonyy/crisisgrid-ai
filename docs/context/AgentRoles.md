# CrisisGrid AI — Agent Roles

## Purpose

This document defines all AI agents used in CrisisGrid AI, their responsibilities, inputs, outputs, and how they interact.

Agents are the core of the system.

They transform:

```text
raw citizen reports → verified crisis intelligence → alerts → actions
```

---

## Core Principle

```text
Each agent must have ONE clear responsibility.
```

Avoid agents doing too many things.

---

# 1. Agent System Overview

```text
User Report
   ↓
Orchestrator
   ↓
Verification Agent
   ↓
GeoRisk Agent
   ↓
Context Agents (Weather / Wildlife)
   ↓
Decision Engine
   ↓
Alert Agent
   ↓
Dispatch Agent
   ↓
Advisory Agent
   ↓
Analytics Agent
```

---

# 2. A2A Client Agent (Orchestrator)

## Role

Entry point for all user requests.

## Responsibilities

- receive report
- validate input
- trigger agent pipeline
- manage execution order
- combine results

## Input

```json
{
  "report": {}
}
```

## Output

```json
{
  "incident": {},
  "alerts": [],
  "dispatch": {},
  "advice": {}
}
```

---

# 3. Verification Agent

## Role

Determine if a report is credible.

## Responsibilities

- analyze description
- check keywords
- validate image presence
- assign initial confidence
- detect duplicates (basic)

## Input

```json
{
  "description": "",
  "image_url": "",
  "latitude": 0,
  "longitude": 0
}
```

## Output

```json
{
  "initial_confidence_score": 0.65,
  "crisis_type": "FIRE",
  "summary": "Fire likely based on keywords and image"
}
```

---

# 4. GeoRisk Agent

## Role

Calculate impact area and clustering.

## Responsibilities

- assign risk radius
- detect nearby incidents
- cluster reports
- check geo consistency

## Output Example

```json
{
  "risk_radius_meters": 500,
  "is_clustered": true,
  "cluster_size": 2
}
```

---

# 5. Weather Context Agent

## Role

Provide environmental context.

## Responsibilities

- check rainfall
- detect flood conditions
- enhance confidence

## Output

```json
{
  "weather_signal": "HEAVY_RAIN",
  "confidence_boost": 0.10
}
```

---

# 6. Wildlife Agent

## Role

Handle wildlife-related reports.

## Responsibilities

- classify species (basic or simulated)
- determine threat level
- expand risk radius

## Output

```json
{
  "species": "LION",
  "threat_level": "HIGH",
  "radius": 1500
}
```

---

# 7. Decision Engine (Not an Agent but Critical)

## Role

Combine all scores and decide:

- incident status
- alert trigger
- dispatch trigger

## Responsibilities

- apply thresholds
- calculate final confidence
- decide escalation

---

# 8. Alert Agent

## Role

Generate user-facing alerts.

## Responsibilities

- create alert message
- assign severity
- define radius
- format safe language

## Output

```json
{
  "title": "FIRE ALERT",
  "message": "Fire reported nearby. Avoid the area.",
  "severity": "HIGH"
}
```

---

# 9. Dispatch Agent

## Role

Notify authorities (simulated in MVP).

## Responsibilities

- map crisis to authority
- generate structured message
- log dispatch

## Output

```json
{
  "authority": "FIRE_SERVICE",
  "status": "SIMULATED_SENT"
}
```

---

# 10. Advisory Agent

## Role

Provide safety guidance.

## Responsibilities

- return safe instructions
- avoid risky advice
- keep language simple

## Output

```json
{
  "steps": [
    "Move away from fire",
    "Avoid smoke"
  ]
}
```

---

# 11. Analytics Agent

## Role

Track trends and metrics.

## Responsibilities

- count incidents
- track hotspots
- measure response time

---

# 12. Agent Interaction Rules

- Agents do NOT call each other directly
- Orchestrator controls flow
- Each agent is stateless (for MVP)
- All outputs must be logged

---

# 13. MVP Agent Priority

## Build First

- Verification Agent
- GeoRisk Agent
- Alert Agent
- Dispatch Agent
- Advisory Agent

## Add Later

- Weather Agent
- Wildlife Agent
- Analytics Agent

---

# 14. Agent Logging

Every agent must log:

```text
agent_name
input_summary
output_summary
confidence_before
confidence_after
duration
```

---

# 15. IBM Bob Usage

Use Bob to:

- generate agent classes
- define inputs/outputs
- create test cases
- refine logic

---

# 16. Final Agent Principle

```text
Agents should be simple, explainable, and composable.
```

Complexity should live in orchestration, not inside individual agents.
