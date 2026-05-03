# CrisisGrid AI — System Architecture (Updated with Verification Model)

## Purpose

This version refines the architecture to include a **multi-signal credibility verification system**
based on:

- Community reporting (cross-reports)
- Crisis-specific thresholds
- Provisional escalation for urgent events (e.g. fire)

---

## Core Architecture Principle (Updated)

CrisisGrid AI does NOT rely on a single AI decision.

Instead, it uses a **Credibility Scoring Pipeline**:

Credibility Score =
- Media Evidence
- Reporter Trust
- Cross Reports
- Geo/Time Consistency
- External Signals (weather etc.)

---

## Updated Incident Lifecycle

PENDING_VERIFICATION  
→ NEEDS_CONFIRMATION  
→ PROVISIONAL_CRITICAL (for urgent cases like fire)  
→ VERIFIED  
→ DISPATCHED  
→ RESOLVED / FALSE_REPORT  

---

## Multi-Report Clustering (NEW)

When new reports come in:

IF:
- same crisis_type
- distance < threshold
- time difference < threshold

THEN:
→ merge into existing incident cluster

---

### Example (Flood)

1 report → 60% confidence  
2 reports → 72%  
3 reports → 85%  

Confidence increases with independent reports.

---

## Crisis-Specific Thresholds (NEW)

| Crisis Type | Alert Threshold | Dispatch Threshold |
|------------|---------------|-------------------|
| FIRE       | 60%           | 65%               |
| FLOOD      | 70%           | 75%               |
| WILDLIFE   | 65%           | 70%               |

---

## Fire Handling (Critical Update)

Fire cannot wait for confirmation.

### Flow:

User submits fire report  
→ Image + location detected  
→ Assign provisional confidence  
→ IF ≥ 60%:

→ status = PROVISIONAL_CRITICAL  
→ trigger alert immediately  
→ simulate dispatch  

Then:

If confirmations increase → VERIFIED  
If no confirmation → NEEDS_REVIEW  

---

## Flood Handling (Updated)

Flood relies on multiple signals:

- Image detection
- Weather API
- Cross reports

Flow:

User report  
→ Check water evidence  
→ Check rainfall  
→ Check nearby reports  
→ Compute score  

---

## Updated Agent Responsibilities

### Verification Agent
Now calculates:
- base confidence
- crisis type

### GeoRisk Agent
Now also:
- supports clustering logic

### Alert Agent
Now:
- respects crisis thresholds

### Dispatch Agent
Now:
- triggers based on confidence + crisis type

---

## Key Improvement Summary

Before:
Single-report → direct decision  

Now:
Multi-signal → adaptive credibility system  

---

## Why This Matters

- Prevents false alarms  
- Handles urgent cases correctly  
- Improves realism for judges  
- Matches real-world emergency systems  

---

## Final Principle

Do not aim for perfect verification.

Aim for:
Fast + adaptive + explainable decision-making
