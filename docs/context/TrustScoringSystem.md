# CrisisGrid AI — Trust Scoring System

## Purpose

This document defines the **Trust Scoring System** used to evaluate:

- **Reporter Trust** (how reliable a user is)
- **Report Credibility Contribution** (how much a user’s report should influence confidence)

This system works alongside the Verification Engine to improve accuracy over time.

---

## Core Principle

```text
Trust should be earned gradually and lost quickly.
```

---

# 1. What Trust Scoring Does

The system:

- tracks user reporting history
- rewards accurate reports
- penalizes false or spam reports
- influences confidence scoring
- helps prioritize reliable signals

---

# 2. Trust Score Range

```text
0.0 → 1.0
```

| Range | Meaning |
|------|--------|
| 0.0 – 0.3 | Low trust |
| 0.3 – 0.6 | Neutral |
| 0.6 – 0.8 | Trusted |
| 0.8 – 1.0 | Highly trusted |

---

# 3. Initial Trust Score

New users start with:

```text
0.5 (neutral)
```

Reason:

- avoid bias
- allow fair contribution

---

# 4. Trust Score Inputs

## Positive Signals

- report confirmed by others
- report matches verified incident
- consistent accurate reporting
- media provided

## Negative Signals

- report rejected
- false report
- spam behavior
- inconsistent reports

---

# 5. Trust Score Updates

## Positive Update

```text
+0.05 to +0.10
```

## Negative Update

```text
-0.10 to -0.20
```

Trust drops faster than it rises.

---

# 6. Trust Impact on Verification

Reporter trust contributes to confidence:

```text
Reporter Trust Contribution = trust_score × 10%
```

Example:

```text
trust_score = 0.8 → +0.08 confidence boost
```

---

# 7. Cross-Report Weighting

Reports from trusted users:

- weigh more in clustering
- increase confidence faster

Low-trust users:

- limited impact
- require more confirmations

---

# 8. Abuse Prevention

## Anti-Spam Rules

- cap trust gain per day
- detect repeated identical reports
- reduce trust for rapid submissions

---

# 9. Trust Decay (Optional)

If a user becomes inactive:

```text
slow decay toward 0.5
```

---

# 10. Database Fields

```text
users.trust_score
reports.reporter_trust_snapshot
```

---

# 11. Example

### Scenario

User submits 3 accurate reports:

```text
0.5 → 0.6 → 0.7 → 0.8
```

Then submits false report:

```text
0.8 → 0.6
```

---

# 12. MVP Simplification

For hackathon:

- basic increment/decrement
- no complex ML model
- simple thresholds

---

# 13. Future Enhancements

- ML trust modeling
- network-based trust
- anomaly detection
- reputation graphs

---

# 14. Logging

Track:

```text
user_id
old_score
new_score
reason
timestamp
```

---

# 15. IBM Bob Usage

Use Bob to:

- generate trust update logic
- simulate trust scenarios
- debug scoring behavior

---

# 16. Final Principle

```text
Trust scoring should be simple, fair, and explainable.
```
