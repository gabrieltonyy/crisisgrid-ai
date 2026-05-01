# CrisisGrid AI — Verification Engine

## Purpose

This document defines the **Verification Engine**, which is responsible for determining whether a reported crisis is credible.

This is one of the **most important parts of the system** because:

- It prevents fake reports
- It avoids panic amplification
- It ensures alerts are trustworthy
- It enables smart escalation

---

## Core Principle

```text
Do not amplify unverified information,
but do not delay urgent response.
```

---

# 1. What the Verification Engine Does

The verification engine:

- analyzes incoming reports
- assigns a confidence score
- evaluates supporting signals
- determines initial incident credibility
- feeds the decision engine

---

# 2. Inputs to Verification Engine

```json
{
  "crisis_type": "FIRE",
  "description": "Smoke and flames near building",
  "image_url": "/uploads/fire.jpg",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "timestamp": "2026-05-01T10:20:00Z",
  "reporter_trust_score": 0.5,
  "nearby_reports": 0
}
```

---

# 3. Output of Verification Engine

```json
{
  "crisis_type": "FIRE",
  "initial_confidence_score": 0.68,
  "confidence_components": {
    "media_evidence": 0.25,
    "description_match": 0.20,
    "location_validity": 0.10,
    "reporter_trust": 0.05,
    "cross_reports": 0.00,
    "external_signals": 0.08
  },
  "verification_summary": "Fire likely based on description and image",
  "recommended_status": "PROVISIONAL_CRITICAL"
}
```

---

# 4. Confidence Scoring Model

## Formula

```text
Confidence Score =
(Media Evidence × 25%) +
(Description Match × 20%) +
(Location Validity × 10%) +
(Reporter Trust × 10%) +
(Cross Reports × 25%) +
(External Signals × 10%)
```

---

# 5. Scoring Components

## 5.1 Media Evidence

- Image present → +0.20 to +0.30
- No image → 0
- (Future) Vision AI → stronger validation

---

## 5.2 Description Match

Check keywords:

### Fire

```text
fire, flames, smoke, burning
```

### Flood

```text
water rising, flooded, overflow, heavy rain
```

### Wildlife

```text
lion, snake, hyena, animal
```

---

## 5.3 Location Validity

- GPS present → +0.10
- Missing → 0

---

## 5.4 Reporter Trust

- default user → 0.05
- high trust user → higher boost
- new user → neutral

---

## 5.5 Cross Reports

- each independent nearby report increases score
- capped to avoid spam manipulation

---

## 5.6 External Signals

- weather API for floods
- (future) sensor/IoT signals
- (future) authority confirmations

---

# 6. Crisis-Specific Behavior

## FIRE (High Urgency)

- Lower threshold
- Faster escalation

```text
If confidence >= 0.60 → PROVISIONAL_CRITICAL
```

---

## FLOOD

- Requires environmental confirmation
- benefits from multiple reports

---

## WILDLIFE

- Medium urgency
- large radius impact

---

# 7. Status Assignment

| Confidence | Status |
|----------|--------|
| < 0.5 | NEEDS_CONFIRMATION |
| 0.5–0.7 | PROVISIONAL |
| ≥ 0.7 | VERIFIED |

---

# 8. Duplicate Detection (Basic MVP)

- same location ± radius
- same crisis type
- short time window

If duplicate:

```text
increase cross_report score
link to existing incident
```

---

# 9. Safety Consideration

Avoid:

```text
"Confirmed disaster"
```

Prefer:

```text
"Reported fire nearby"
```

---

# 10. Future Enhancements

- Google Vision AI
- IBM watsonx image classification
- NLP classification
- anomaly detection
- fake image detection

---

# 11. Failure Handling

If verification fails:

- set confidence low
- do not alert
- keep report in system

---

# 12. Logging

Log:

```text
input summary
score components
final score
decision
```

---

# 13. Example Scenario

### Fire Report

- image present
- strong keywords
- GPS present

→ confidence = 0.68  
→ status = PROVISIONAL_CRITICAL  

---

# 14. IBM Bob Usage

Use Bob to:

- generate scoring logic
- improve keyword detection
- simulate classification
- debug scoring anomalies

---

# 15. Final Principle

```text
Verification should be fast, explainable, and adaptive.
```
