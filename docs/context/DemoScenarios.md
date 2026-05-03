# CrisisGrid AI — Demo Scenarios

## Purpose

This document defines the **demo scenarios** for CrisisGrid AI.

These scenarios are critical because:

- they showcase the system end-to-end
- they prove real-world applicability
- they demonstrate multi-agent intelligence
- they align with hackathon judging criteria

---

## Core Demo Principle

```text
Show transformation:
Citizen Report → AI Verification → Alert → Authority Action
```

---

# 1. Demo Strategy

Each demo should clearly show:

1. User submits report  
2. AI verifies and scores  
3. System identifies risk area  
4. Alerts are generated  
5. Authorities are notified (simulated)  
6. Dashboard reflects real-time state  

---

# 2. Demo Scenario 1 — Nairobi Flood Alert

## Story

A citizen notices rising flood water in Nairobi.

## Steps

1. Open app
2. Submit report:
   - crisis_type: FLOOD
   - description: "Water levels rising, road becoming impassable"
   - location: Nairobi (Westlands)
3. Submit second nearby flood report (simulate another user)
4. Enable simulated weather signal (heavy rain)

## System Behavior

- Verification Agent assigns initial confidence
- GeoRisk Agent clusters reports
- Weather Agent boosts confidence
- Decision Engine increases confidence

## Expected Output

```text
confidence increases
status = VERIFIED
alert created
dispatch simulated
```

## UI Demo Points

- Map shows flood zone
- Alert visible
- Dashboard shows cluster

---

# 3. Demo Scenario 2 — Urban Fire Emergency

## Story

A citizen sees fire in a building.

## Steps

1. Submit report:
   - crisis_type: FIRE
   - description: "Smoke and flames visible"
   - location: Nairobi CBD
   - image: fire.jpg (real or placeholder)

## System Behavior

- Verification detects fire keywords
- Image boosts confidence
- Fire threshold applied
- Immediate escalation triggered

## Expected Output

```text
status = PROVISIONAL_CRITICAL
alert created immediately
dispatch simulated to FIRE_SERVICE
```

## UI Demo Points

- Alert appears instantly
- Severity shown as HIGH
- Dispatch visible in logs

---

# 4. Demo Scenario 3 — Wildlife Threat

## Story

A lion is spotted near residential area.

## Steps

1. Submit report:
   - crisis_type: WILDLIFE
   - description: "Lion spotted near houses"
   - location: near Nairobi National Park

## System Behavior

- Wildlife Agent classifies threat
- GeoRisk assigns large radius
- Decision Engine flags risk

## Expected Output

```text
status = PROVISIONAL or VERIFIED
large alert radius
dispatch to WILDLIFE_AUTHORITY
```

## UI Demo Points

- Map shows large danger zone
- Alert message clear
- Advisory provided

---

# 5. Demo Scenario Flow Summary

```text
Report → Verify → Score → Cluster → Alert → Dispatch → Dashboard
```

---

# 6. Demo Preparation Checklist

## Backend

- API running
- agents working
- seed data loaded

## Frontend

- form working
- map loading
- alerts visible
- dashboard functional

## Data

- sample images ready
- test coordinates prepared

---

# 7. Demo Script (For Presentation)

### Opening

"Imagine you are walking in Nairobi and notice something dangerous..."

### Action

- submit report live

### AI Explanation

"Our AI verifies the report, checks nearby data, and determines risk..."

### Result

- show alert
- show dashboard
- show dispatch

---

# 8. Fallback Plan

If live demo fails:

- use pre-seeded data
- use screenshots
- explain flow step-by-step

---

# 9. IBM Bob Requirement

During demo, show:

- Bob-generated code
- Bob session outputs
- explanation of how Bob assisted

---

# 10. Final Principle

```text
Demo clarity > technical complexity
```

A simple working demo is better than a complex broken one.
