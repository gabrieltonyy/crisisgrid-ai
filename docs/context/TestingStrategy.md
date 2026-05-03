# CrisisGrid AI — Testing Strategy

## Purpose

This document defines the testing strategy for CrisisGrid AI.

The goal is to make the MVP reliable enough for a hackathon demo while keeping testing practical for a solo developer.

Testing should focus on the parts of the system that judges will see:

```text
report submission → verification → clustering → alerts → dispatch → dashboard
```

---

## Testing Philosophy

For the hackathon, do not try to test everything.

Test the logic that can break the demo.

Priority:

1. Core decision logic
2. Agent outputs
3. API endpoints
4. Demo scenario flows
5. Frontend critical UI paths

---

# 1. Testing Layers

## 1.1 Unit Tests

Test small logic units in isolation.

Best for:

- credibility scoring
- threshold decisions
- radius calculation
- safety advice selection
- incident clustering
- crisis type logic

---

## 1.2 Integration Tests

Test API routes and service interactions.

Best for:

- report submission
- incident creation
- alert generation
- dispatch simulation
- agent run logging

---

## 1.3 End-to-End Demo Tests

Test the full user journey.

Best for:

- fire demo
- flood demo
- wildlife demo

---

## 1.4 Manual Demo Checklist

Use a simple checklist before recording/presenting.

Best for:

- UI polish
- map visibility
- alert display
- dashboard data
- Bob session folder check

---

# 2. Backend Test Tools

Recommended:

```text
pytest
pytest-asyncio
httpx
FastAPI TestClient
```

Optional:

```text
factory_boy
freezegun
```

---

# 3. Frontend Test Tools

Recommended minimal approach:

```text
manual testing first
TypeScript type checking
npm run build
```

Optional if time allows:

```text
React Testing Library
Playwright
```

Because this is a solo hackathon project, do not spend too much time on advanced frontend tests before the MVP works.

---

# 4. Critical Backend Unit Tests

---

## 4.1 Credibility Engine Tests

Test score calculation.

### Test: Fire report with image and GPS

```text
Given:
- crisis_type = FIRE
- image exists
- GPS exists
- fire keywords present

Expected:
- confidence >= 0.60
- status can become PROVISIONAL_CRITICAL
```

Suggested test name:

```text
test_fire_report_with_image_and_gps_reaches_provisional_threshold
```

---

## 4.2 Flood confidence increases with cross-reports

```text
Given:
- first flood report confidence = 0.60
- second independent nearby report exists
- weather signal is heavy rain

Expected:
- confidence increases
- incident status becomes VERIFIED
```

Suggested test name:

```text
test_flood_confidence_increases_with_cross_reports_and_weather
```

---

## 4.3 Low-confidence report does not dispatch

```text
Given:
- confidence below dispatch threshold

Expected:
- no dispatch log created
- status remains NEEDS_CONFIRMATION
```

Suggested test name:

```text
test_low_confidence_report_does_not_trigger_dispatch
```

---

## 4.4 Crisis-specific thresholds

```text
FIRE alert threshold = 0.60
FLOOD alert threshold = 0.70
WILDLIFE alert threshold = 0.65
```

Suggested test name:

```text
test_crisis_specific_thresholds_are_applied_correctly
```

---

# 5. Incident Clustering Tests

---

## 5.1 Same-area reports cluster

```text
Given:
- existing FIRE incident
- new FIRE report within 500m
- report submitted within 45 minutes

Expected:
- report links to existing incident
```

Suggested test name:

```text
test_nearby_same_type_report_links_to_existing_incident
```

---

## 5.2 Different crisis types do not cluster

```text
Given:
- existing FIRE incident
- new FLOOD report nearby

Expected:
- new incident is created
```

Suggested test name:

```text
test_different_crisis_types_do_not_cluster
```

---

## 5.3 Old reports do not cluster

```text
Given:
- existing incident older than time window
- new report same area

Expected:
- new incident is created
```

Suggested test name:

```text
test_report_outside_time_window_creates_new_incident
```

---

# 6. Agent Tests

---

## 6.1 Verification Agent

Test:

- fire keyword detection
- flood keyword detection
- wildlife keyword detection
- image presence boost
- GPS presence boost
- confidence output format

Suggested tests:

```text
test_verification_agent_detects_fire_keywords
test_verification_agent_detects_flood_keywords
test_verification_agent_applies_image_confidence_boost
```

---

## 6.2 GeoRisk Agent

Test:

- FIRE radius = 500m
- FLOOD radius = 1000m
- WILDLIFE radius = 1500m
- clustering summary is returned

Suggested tests:

```text
test_georisk_agent_assigns_fire_radius
test_georisk_agent_assigns_flood_radius
test_georisk_agent_assigns_wildlife_radius
```

---

## 6.3 Alert Agent

Test:

- alert title generated
- alert message is calm
- alert radius matches incident
- no alert for low confidence unless provisional critical

Suggested tests:

```text
test_alert_agent_generates_fire_alert_message
test_alert_agent_does_not_alert_low_confidence_report
```

---

## 6.4 Dispatch Agent

Test:

- FIRE maps to FIRE_SERVICE
- FLOOD maps to DISASTER_MANAGEMENT
- WILDLIFE maps to WILDLIFE_AUTHORITY
- dispatch status is SIMULATED_SENT for MVP

Suggested tests:

```text
test_dispatch_agent_maps_fire_to_fire_service
test_dispatch_agent_maps_flood_to_disaster_management
test_dispatch_agent_uses_simulated_status
```

---

## 6.5 Advisory Agent

Test safe advice output.

Suggested tests:

```text
test_advisory_agent_returns_fire_safety_steps
test_advisory_agent_returns_flood_safety_steps
test_advisory_agent_returns_wildlife_safety_steps
```

---

# 7. API Integration Tests

---

## 7.1 Submit Report

Endpoint:

```text
POST /reports
```

Expected:

- report is created
- incident is created or linked
- agent pipeline runs
- response includes status and confidence

Suggested test:

```text
test_submit_report_runs_agent_pipeline
```

---

## 7.2 Nearby Reports

Endpoint:

```text
GET /reports/nearby
```

Expected:

- returns incidents within radius
- excludes far incidents

Suggested test:

```text
test_nearby_reports_returns_incidents_within_radius
```

---

## 7.3 Confirm Report

Endpoint:

```text
POST /reports/{report_id}/confirm
```

Expected:

- confirmation is saved
- confidence increases
- incident status may update

Suggested test:

```text
test_confirm_report_increases_incident_confidence
```

---

## 7.4 Agent Run Logs

Endpoint:

```text
GET /agent-runs?report_id=REP-001
```

Expected:

- verification agent log exists
- georisk agent log exists
- alert/dispatch logs exist where applicable

Suggested test:

```text
test_agent_runs_are_logged_for_report_submission
```

---

# 8. Demo Scenario Tests

These should be tested manually and optionally automated.

---

## 8.1 Fire Demo Test

### Steps

1. Submit fire report
2. Include image or mock image
3. Use Nairobi CBD location
4. Confirm status changes to PROVISIONAL_CRITICAL
5. Confirm alert is created
6. Confirm dispatch log is created
7. Confirm dashboard shows incident

### Expected

```text
status = PROVISIONAL_CRITICAL
alert created = yes
dispatch simulated = yes
```

---

## 8.2 Flood Demo Test

### Steps

1. Submit flood report
2. Submit second nearby flood report
3. Enable simulated heavy rain
4. Confirm confidence increases
5. Confirm alert is created

### Expected

```text
confidence increases
status = VERIFIED or DISPATCHED
```

---

## 8.3 Wildlife Demo Test

### Steps

1. Submit wildlife report
2. Description includes lion/hyena/snake
3. Confirm risk radius is large
4. Confirm alert is created
5. Confirm dispatch is mapped to wildlife authority

### Expected

```text
authority_type = WILDLIFE_AUTHORITY
risk_radius_meters >= 1500
```

---

# 9. Frontend Manual Test Checklist

## Report Form

- Can select crisis type
- Can enter description
- Can capture/enter location
- Can submit report
- Shows success response
- Shows confidence/status after processing

## Crisis Map / Incident List

- Shows incident markers or cards
- Shows crisis type
- Shows confidence
- Shows status
- Shows severity

## Alerts Page

- Shows generated alerts
- Alert message is readable
- Alert does not sound panic-inducing

## Dashboard

- Shows incident queue
- Shows status
- Shows confidence score
- Shows dispatch status
- Shows agent run summary if available

---

# 10. Security Tests

## Must Test

- invalid latitude rejected
- invalid longitude rejected
- invalid crisis type rejected
- oversized image rejected
- unsupported image type rejected
- dashboard endpoint protected or clearly demo-protected
- no secrets committed

Suggested tests:

```text
test_invalid_latitude_is_rejected
test_invalid_crisis_type_is_rejected
test_oversized_file_is_rejected
```

---

# 11. Environment Tests

## Startup Validation

Test that:

- app starts with local env
- optional services disabled do not break app
- Cloudant required variables only checked if `CLOUDANT_ENABLED=true`
- watsonx required variables only checked if `WATSONX_ENABLED=true`

Suggested tests:

```text
test_app_starts_without_optional_services
test_cloudant_requires_credentials_when_enabled
test_watsonx_requires_credentials_when_enabled
```

---

# 12. Seed Data Testing

Seed data should include:

- fire incident
- flood incident with multiple reports
- wildlife incident
- dispatch logs
- agent runs

Test that:

```text
python seed_demo_data.py
```

creates demo-ready records.

---

# 13. MVP Testing Priority

## Must Test

- credibility engine
- threshold policy
- report submission endpoint
- agent run logging
- fire provisional critical behavior
- flood confidence increase
- dashboard loads

## Should Test

- confirmations
- nearby incidents
- dispatch mapping
- safety advice
- file upload validation

## Nice to Test

- Cloudant logging
- watsonx integration
- real weather API integration
- frontend automated tests

---

# 14. Test Data

## Fire Report

```json
{
  "crisis_type": "FIRE",
  "description": "Smoke and flames near a building",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "location_text": "Nairobi CBD"
}
```

## Flood Report

```json
{
  "crisis_type": "FLOOD",
  "description": "Water levels are rising and road is becoming impassable",
  "latitude": -1.2676,
  "longitude": 36.8108,
  "location_text": "Westlands"
}
```

## Wildlife Report

```json
{
  "crisis_type": "WILDLIFE",
  "description": "A lion has been spotted near residential houses",
  "latitude": -1.3615,
  "longitude": 36.7438,
  "location_text": "Near Nairobi National Park"
}
```

---

# 15. Suggested Pytest Structure

```text
services/backend/tests/
├── test_reports.py
├── test_incidents.py
├── test_credibility_engine.py
├── test_threshold_policy.py
├── test_incident_clustering.py
├── test_verification_agent.py
├── test_georisk_agent.py
├── test_alert_agent.py
├── test_dispatch_agent.py
├── test_advisory_agent.py
└── test_environment.py
```

---

# 16. Example Test Case Pseudocode

```python
def test_fire_report_triggers_provisional_critical():
    report = {
        "crisis_type": "FIRE",
        "description": "Smoke and flames near building",
        "latitude": -1.2921,
        "longitude": 36.8219,
        "image_url": "/uploads/fire.jpg"
    }

    result = orchestrator.process_report(report)

    assert result.status == "PROVISIONAL_CRITICAL"
    assert result.confidence_score >= 0.60
    assert "ALERT_CREATED" in result.actions
```

---

# 17. IBM Bob Testing Usage

Use IBM Bob to:

- generate pytest files
- create API tests
- write fake data factories
- generate frontend manual checklist
- debug failing tests
- improve test naming
- create CI test steps

## Bob Prompt Example

```text
Using the CrisisGrid AI architecture and coding standards, generate pytest tests for:
1. fire provisional critical threshold
2. flood confidence increase from cross-reports
3. low confidence reports not triggering dispatch
Follow the existing folder structure.
```

---

# 18. Pre-Demo Test Checklist

Before recording or presenting:

- backend starts
- frontend starts
- database seeded
- fire demo works
- flood demo works
- wildlife demo works or is ready as optional
- dashboard loads
- alerts display
- agent logs visible
- Bob session reports exported
- no real secrets in repo
- README run instructions work

---

# 19. Final Testing Principle

Do not aim for perfect test coverage.

Aim for confidence that the core demo will not fail.

The most important tested flow is:

```text
report → verify → score → cluster → alert → dispatch → dashboard
```
