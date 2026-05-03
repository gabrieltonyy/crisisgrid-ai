# CrisisGrid AI — Database Schema

## Purpose

This document defines the database schema for CrisisGrid AI.

The schema supports the hackathon MVP flow:

```text
Citizen report
→ agent verification
→ incident clustering
→ credibility scoring
→ alerts
→ dispatch simulation
→ dashboard visibility
```

The design is optimized for a solo developer but remains extensible for future production use.

---

## Recommended Database Strategy

## MVP Recommendation

Use **PostgreSQL**.

If PostGIS is available, use it for geospatial queries.

If PostGIS setup takes too long, store latitude/longitude as decimal values and calculate distance in backend application code.

## Optional IBM Alternative

Use **IBM Cloudant** if you want a quicker document-database setup within IBM Cloud services.

However, PostgreSQL is recommended because CrisisGrid AI is location-heavy and will benefit from relational structure and geospatial support later.

---

# 1. Entity Relationship Overview

```text
users
  └── reports
        ├── confirmations
        ├── agent_runs
        └── media_files

incidents
  ├── reports
  ├── alerts
  ├── dispatch_logs
  ├── safety_advice_logs
  └── incident_score_history
```

---

# 2. Core Tables

---

## 2.1 users

Stores basic user or demo reporter information.

For MVP, this can be simulated.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR(120),
    email VARCHAR(180) UNIQUE,
    phone_number VARCHAR(50),
    role VARCHAR(30) NOT NULL DEFAULT 'CITIZEN',
    trust_score NUMERIC(5,2) NOT NULL DEFAULT 0.50,
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Roles

```text
CITIZEN
AUTHORITY
ADMIN
SYSTEM
```

## Notes

- Avoid collecting unnecessary personal data.
- For demo, use synthetic users.
- Trust score starts neutral at 0.50.

---

## 2.2 reports

Stores individual citizen submissions.

A report is one user's observation.

Multiple reports may later cluster into one incident.

```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY,
    incident_id UUID,
    user_id UUID,
    crisis_type VARCHAR(50) NOT NULL,
    description TEXT,
    image_url TEXT,
    video_url TEXT,
    latitude NUMERIC(10,7) NOT NULL,
    longitude NUMERIC(10,7) NOT NULL,
    location_text VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING_VERIFICATION',
    confidence_score NUMERIC(5,2) DEFAULT 0.00,
    severity_score NUMERIC(5,2) DEFAULT 0.00,
    source VARCHAR(50) DEFAULT 'CITIZEN_APP',
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Status Values

```text
PENDING_VERIFICATION
NEEDS_CONFIRMATION
PROVISIONAL_CRITICAL
VERIFIED
DISPATCHED
RESOLVED
FALSE_REPORT
```

## Crisis Types

```text
FIRE
FLOOD
WILDLIFE
ACCIDENT
SECURITY
HEALTH
LANDSLIDE
HAZARDOUS_SPILL
OTHER
```

---

## 2.3 incidents

Stores clustered crisis events.

An incident represents the actual emergency being tracked.

```sql
CREATE TABLE incidents (
    id UUID PRIMARY KEY,
    primary_report_id UUID,
    crisis_type VARCHAR(50) NOT NULL,
    title VARCHAR(180),
    description TEXT,
    latitude NUMERIC(10,7) NOT NULL,
    longitude NUMERIC(10,7) NOT NULL,
    location_text VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING_VERIFICATION',
    confidence_score NUMERIC(5,2) DEFAULT 0.00,
    severity_score NUMERIC(5,2) DEFAULT 0.00,
    risk_radius_meters INTEGER DEFAULT 500,
    report_count INTEGER DEFAULT 1,
    confirmation_count INTEGER DEFAULT 0,
    dispute_count INTEGER DEFAULT 0,
    external_signal_score NUMERIC(5,2) DEFAULT 0.00,
    cross_report_score NUMERIC(5,2) DEFAULT 0.00,
    reporter_trust_score NUMERIC(5,2) DEFAULT 0.00,
    media_evidence_score NUMERIC(5,2) DEFAULT 0.00,
    geo_time_consistency_score NUMERIC(5,2) DEFAULT 0.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    resolved_at TIMESTAMP
);
```

## Why reports and incidents are separate

This is important.

```text
Report = what one user submitted
Incident = clustered real-world event
```

Example:

- 5 users report flooding in the same area
- System stores 5 reports
- System links them to 1 incident
- Incident confidence increases as reports accumulate

---

## 2.4 confirmations

Stores user confirmations or disputes.

```sql
CREATE TABLE confirmations (
    id UUID PRIMARY KEY,
    report_id UUID,
    incident_id UUID NOT NULL,
    user_id UUID,
    confirmation_type VARCHAR(50) NOT NULL,
    comment TEXT,
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    is_independent BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Confirmation Types

```text
CONFIRM
DISPUTE
UPDATE_LOCATION
RESOLVED
```

## Notes

- Independent confirmations increase credibility.
- Multiple confirmations from the same user should not boost confidence repeatedly.

---

## 2.5 alerts

Stores user-facing alerts.

```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY,
    incident_id UUID NOT NULL,
    title VARCHAR(180) NOT NULL,
    message TEXT NOT NULL,
    crisis_type VARCHAR(50) NOT NULL,
    severity VARCHAR(30) NOT NULL,
    target_radius_meters INTEGER NOT NULL,
    latitude NUMERIC(10,7) NOT NULL,
    longitude NUMERIC(10,7) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
```

## Alert Status

```text
ACTIVE
EXPIRED
CANCELLED
```

---

## 2.6 dispatch_logs

Stores simulated or real authority dispatch attempts.

```sql
CREATE TABLE dispatch_logs (
    id UUID PRIMARY KEY,
    incident_id UUID NOT NULL,
    authority_type VARCHAR(80) NOT NULL,
    channel VARCHAR(50) NOT NULL DEFAULT 'SIMULATED',
    recipient VARCHAR(180),
    message TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'SIMULATED_SENT',
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_reference VARCHAR(180),
    error_message TEXT
);
```

## Authority Types

```text
FIRE_SERVICE
DISASTER_MANAGEMENT
WILDLIFE_AUTHORITY
POLICE
AMBULANCE
PUBLIC_HEALTH_OFFICE
COUNTY_OFFICE
```

## Dispatch Status

```text
SIMULATED_SENT
SENT
FAILED
PENDING
```

---

## 2.7 agent_runs

Stores explainability logs for every agent execution.

This is very important for the demo.

```sql
CREATE TABLE agent_runs (
    id UUID PRIMARY KEY,
    report_id UUID,
    incident_id UUID,
    agent_name VARCHAR(120) NOT NULL,
    input_summary TEXT,
    output_summary TEXT,
    status VARCHAR(50) NOT NULL,
    confidence_before NUMERIC(5,2),
    confidence_after NUMERIC(5,2),
    duration_ms INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Agent Names

```text
report_orchestrator
verification_agent
georisk_agent
weather_context_agent
wildlife_agent
alert_agent
dispatch_agent
advisory_agent
analytics_agent
```

## Why agent_runs matters

It helps show:

- how the system made decisions
- which agents ran
- why confidence changed
- how Bob-generated agents work together

---

## 2.8 safety_advice_logs

Stores safety guidance generated for incidents.

```sql
CREATE TABLE safety_advice_logs (
    id UUID PRIMARY KEY,
    incident_id UUID NOT NULL,
    crisis_type VARCHAR(50) NOT NULL,
    severity VARCHAR(30),
    safety_steps TEXT NOT NULL,
    avoid_actions TEXT,
    source VARCHAR(50) DEFAULT 'STATIC_PLAYBOOK',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Source Values

```text
STATIC_PLAYBOOK
WATSONX_AI
MANUAL
```

---

## 2.9 incident_score_history

Tracks confidence score changes over time.

This is useful for explaining how multiple reports increase credibility.

```sql
CREATE TABLE incident_score_history (
    id UUID PRIMARY KEY,
    incident_id UUID NOT NULL,
    previous_score NUMERIC(5,2),
    new_score NUMERIC(5,2) NOT NULL,
    reason TEXT,
    score_components JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Example score_components

```json
{
  "media_evidence_score": 0.25,
  "reporter_trust_score": 0.10,
  "cross_report_score": 0.20,
  "geo_time_consistency_score": 0.15,
  "external_signal_score": 0.15
}
```

---

## 2.10 media_files

Stores metadata about uploaded media.

```sql
CREATE TABLE media_files (
    id UUID PRIMARY KEY,
    report_id UUID NOT NULL,
    file_url TEXT NOT NULL,
    file_type VARCHAR(50),
    file_size_bytes BIGINT,
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    media_validity_score NUMERIC(5,2),
    metadata_summary TEXT
);
```

## Notes

For MVP, media can be stored locally or in a simple uploads folder.

For production, use object storage.

---

# 3. Relationships

## Recommended Foreign Keys

```sql
ALTER TABLE reports
ADD CONSTRAINT fk_reports_user
FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE reports
ADD CONSTRAINT fk_reports_incident
FOREIGN KEY (incident_id) REFERENCES incidents(id);

ALTER TABLE incidents
ADD CONSTRAINT fk_incidents_primary_report
FOREIGN KEY (primary_report_id) REFERENCES reports(id);

ALTER TABLE confirmations
ADD CONSTRAINT fk_confirmations_report
FOREIGN KEY (report_id) REFERENCES reports(id);

ALTER TABLE confirmations
ADD CONSTRAINT fk_confirmations_incident
FOREIGN KEY (incident_id) REFERENCES incidents(id);

ALTER TABLE alerts
ADD CONSTRAINT fk_alerts_incident
FOREIGN KEY (incident_id) REFERENCES incidents(id);

ALTER TABLE dispatch_logs
ADD CONSTRAINT fk_dispatch_incident
FOREIGN KEY (incident_id) REFERENCES incidents(id);

ALTER TABLE agent_runs
ADD CONSTRAINT fk_agent_runs_report
FOREIGN KEY (report_id) REFERENCES reports(id);

ALTER TABLE agent_runs
ADD CONSTRAINT fk_agent_runs_incident
FOREIGN KEY (incident_id) REFERENCES incidents(id);
```

---

# 4. Indexing Strategy

## Basic Indexes

```sql
CREATE INDEX idx_reports_crisis_type ON reports(crisis_type);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_created_at ON reports(created_at);
CREATE INDEX idx_reports_location ON reports(latitude, longitude);

CREATE INDEX idx_incidents_crisis_type ON incidents(crisis_type);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_confidence ON incidents(confidence_score);
CREATE INDEX idx_incidents_location ON incidents(latitude, longitude);

CREATE INDEX idx_alerts_incident ON alerts(incident_id);
CREATE INDEX idx_dispatch_incident ON dispatch_logs(incident_id);
CREATE INDEX idx_agent_runs_report ON agent_runs(report_id);
CREATE INDEX idx_agent_runs_incident ON agent_runs(incident_id);
```

## PostGIS Optional Index

If using PostGIS:

```sql
ALTER TABLE incidents
ADD COLUMN location GEOGRAPHY(POINT, 4326);

CREATE INDEX idx_incidents_location_geog
ON incidents
USING GIST(location);
```

---

# 5. Credibility Scoring Fields

The schema explicitly supports the updated scoring model.

## Score Components

Stored on incidents:

```text
media_evidence_score
reporter_trust_score
cross_report_score
geo_time_consistency_score
external_signal_score
confidence_score
```

## Formula

```text
Credibility Score =
(Media Evidence × 25%) +
(Reporter Trust × 15%) +
(Cross Reports × 25%) +
(Geo/Time Consistency × 15%) +
(External Signal × 20%)
```

---

# 6. Crisis-Specific Threshold Storage

For MVP, thresholds can live in backend config.

Optional future table:

```sql
CREATE TABLE crisis_thresholds (
    id UUID PRIMARY KEY,
    crisis_type VARCHAR(50) NOT NULL UNIQUE,
    alert_threshold NUMERIC(5,2) NOT NULL,
    dispatch_threshold NUMERIC(5,2) NOT NULL,
    provisional_critical_allowed BOOLEAN DEFAULT FALSE,
    default_radius_meters INTEGER NOT NULL,
    cluster_radius_meters INTEGER NOT NULL,
    time_window_minutes INTEGER NOT NULL
);
```

## Seed Values

```text
FIRE:
alert_threshold = 0.60
dispatch_threshold = 0.65
provisional_critical_allowed = true
default_radius = 500

FLOOD:
alert_threshold = 0.70
dispatch_threshold = 0.75
default_radius = 1000

WILDLIFE:
alert_threshold = 0.65
dispatch_threshold = 0.70
default_radius = 1500
```

---

# 7. MVP Seed Data

Use seed data to support the demo.

## Demo Users

```text
Citizen Demo User
Authority Demo User
Admin Demo User
```

## Demo Incidents

```text
Nairobi CBD Fire
Westlands Flooding
Wildlife Sighting Near Residential Area
```

## Demo Reports

Create at least:

```text
3 flood reports in same area
1 fire report with provisional critical status
1 wildlife report with danger radius
```

This helps demonstrate clustering and confidence increases.

---

# 8. Example Incident Confidence Progression

## Flood Example

```text
Initial report:
confidence = 0.60
status = NEEDS_CONFIRMATION

Second independent report:
confidence = 0.72
status = VERIFIED

Weather support signal:
confidence = 0.87
status = DISPATCHED
```

This should be visible in `incident_score_history`.

---

# 9. Solo MVP Implementation Notes

## Build First

- users
- reports
- incidents
- alerts
- dispatch_logs
- agent_runs
- safety_advice_logs

## Build If Time Allows

- confirmations
- incident_score_history
- media_files
- crisis_thresholds

## Can Be Simplified

If time is limited:

- skip auth and use demo users
- store image URL only
- calculate distance in code
- keep thresholds in config
- simulate dispatch

---

# 10. IBM Bob Usage

Use IBM Bob to:

- generate SQLAlchemy models
- generate Alembic migrations
- create seed scripts
- write repository classes
- generate database tests
- refactor schema naming
- document database decisions

Save Bob task reports in:

```text
bob_sessions/
```

---

## Final Database Principle

The database should make the crisis pipeline explainable.

It must clearly show:

```text
who reported
what was reported
which incident it belongs to
how credibility changed
which agents ran
who was alerted
which authority was notified
```
