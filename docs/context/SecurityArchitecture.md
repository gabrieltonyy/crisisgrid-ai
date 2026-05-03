# CrisisGrid AI — Security Architecture

## Purpose

This document defines the security architecture for CrisisGrid AI.

Because CrisisGrid AI deals with crisis reporting, user location, public alerts, and simulated authority dispatch, security must cover more than normal application protection.

The platform must protect against:

- fake crisis reports
- panic amplification
- exposed API keys
- misuse of location data
- unauthorized dashboard access
- unsafe AI-generated advice
- accidental leakage of IBM Cloud credentials

---

## Security Goals

CrisisGrid AI should be:

- privacy-aware
- abuse-resistant
- explainable
- safe for public crisis communication
- compliant with hackathon restrictions
- careful with cloud credentials and API keys

---

# 1. Security Principles

## 1.1 Minimum Data Collection

Only collect what is needed for the demo and crisis response.

### Collect

- crisis type
- report description
- image/media evidence
- latitude/longitude
- timestamp
- optional anonymous user reference

### Avoid

- unnecessary personal details
- national ID numbers
- personal health data
- private addresses where not needed
- social media scraping
- client or company confidential data

This aligns with the hackathon requirement to avoid personal information, client data, company confidential data, and social media data.

---

## 1.2 Verification Before Amplification

The platform should not blindly broadcast every report.

A report should pass the credibility and threshold logic before public alerting.

However, urgent incidents like fires may trigger a provisional warning.

### Key Rule

```text
Do not wait for perfect certainty when delay creates danger.
Do not amplify low-confidence reports as verified truth.
```

---

## 1.3 Explainability

Every major AI or agent decision should be logged.

This includes:

- verification confidence
- threshold decision
- alert decision
- dispatch decision
- safety advice source

Use the `agent_runs` and `incident_score_history` records for traceability.

---

## 1.4 Human-Safe AI Advice

Safety advice must be:

- simple
- calm
- non-technical
- non-harmful
- bounded to crisis response
- not a replacement for official emergency services

The system should avoid giving dangerous or overconfident advice.

---

# 2. Threat Model

## 2.1 Fake Reports

### Risk

A user submits false reports to cause panic or waste emergency resources.

### Controls

- confidence scoring
- cross-report verification
- image/media validation
- duplicate detection
- reporter trust score
- manual review option
- dispute/confirmation system

---

## 2.2 Panic Amplification

### Risk

Low-confidence crisis reports could trigger unnecessary fear.

### Controls

- crisis-specific thresholds
- provisional wording for urgent but unverified alerts
- calm alert language
- severity scoring
- status labels:
  - NEEDS_CONFIRMATION
  - PROVISIONAL_CRITICAL
  - VERIFIED

---

## 2.3 Delayed Response to Critical Events

### Risk

Over-verification may delay action for fires or other urgent incidents.

### Controls

- lower thresholds for fire
- provisional critical status
- immediate local alert for high-risk reports
- later confirmation upgrades/downgrades

Example:

```text
Fire report + image + GPS + keywords
→ PROVISIONAL_CRITICAL
→ alert users
→ simulate dispatch
→ wait for confirmations
```

---

## 2.4 Location Privacy Abuse

### Risk

User location or crisis locations could be misused.

### Controls

- avoid exposing reporter identity publicly
- show incident location, not reporter location
- allow anonymous reporting
- limit precise personal location display
- restrict dashboard access
- retain only needed geodata

---

## 2.5 Unauthorized Dashboard Access

### Risk

Non-authorized users access authority dashboard or dispatch controls.

### Controls

- role-based access control
- roles:
  - CITIZEN
  - AUTHORITY
  - ADMIN
- protect dashboard APIs
- simulate authority dispatch in MVP
- do not expose sensitive admin endpoints publicly

---

## 2.6 API Key and Credential Leakage

### Risk

IBM Cloud, Cloudant, watsonx.ai, Maps, Weather, SMS, or other API keys could be committed to GitHub.

### Controls

- use `.env`
- create `.env.example`
- never commit real secrets
- add `.env` to `.gitignore`
- rotate exposed keys immediately
- use environment variables in deployment
- use IBM Cloud secure credential practices

---

## 2.7 Unsafe Media Uploads

### Risk

Uploaded images/files may contain malicious payloads or large files.

### Controls

- limit file size
- allow only safe MIME types
- rename uploaded files using UUIDs
- store outside executable paths
- scan metadata where possible
- avoid exposing raw file paths

---

# 3. Authentication and Authorization

## MVP Approach

For solo hackathon MVP, use one of:

### Option 1: Simple Demo Auth

- mock login
- hardcoded demo roles
- fastest build

### Option 2: Firebase Auth

- real authentication
- easier frontend integration

### Option 3: JWT Auth in FastAPI

- custom backend auth
- more control, more work

## Recommended for Solo MVP

Use simple demo auth first.

Add Firebase Auth only if time allows.

---

## Role Permissions

| Role | Permissions |
|---|---|
| CITIZEN | submit reports, view alerts, confirm incidents |
| AUTHORITY | view dashboard, view dispatch logs, mark incidents resolved |
| ADMIN | manage incidents, view analytics, override status |
| SYSTEM | internal agent operations only |

---

# 4. API Security

## Required Controls

- request validation using Pydantic
- input length limits
- file size limits
- crisis type enum validation
- rate limiting for report submission
- role checks for dashboard endpoints
- structured error handling
- no stack traces in API responses

## Example API Rules

```text
POST /reports
- citizen/demo user only
- max description length
- image optional but size-limited
- latitude/longitude required

GET /dashboard/incidents
- authority/admin only

POST /incidents/{id}/resolve
- authority/admin only
```

---

# 5. Report Abuse Prevention

## Controls

### Rate Limiting

Limit reports per user/device/IP.

Example MVP rule:

```text
max 5 reports per user per 10 minutes
```

### Duplicate Detection

Detect repeated reports from:

- same user
- same location
- same crisis type
- short time window

### Reporter Trust Score

New users start neutral.

Trust increases when reports are confirmed.

Trust decreases when reports are disputed or marked false.

---

# 6. Credibility and Alert Safety

## Crisis-Specific Thresholds

| Crisis Type | Alert Threshold | Dispatch Threshold | Notes |
|---|---:|---:|---|
| FIRE | 60% | 65% | allow provisional critical |
| FLOOD | 70% | 75% | use weather and cross-reports |
| WILDLIFE | 65% | 70% | local warning allowed |
| SECURITY | 80% | 85% | avoid panic amplification |
| HEALTH | 85% | 90% | prefer official confirmation |

## Alert Wording Rules

Avoid:

```text
Confirmed disaster
Everyone panic
Guaranteed danger
```

Use:

```text
Reported fire nearby. Avoid the area and follow official instructions.
Flood risk reported. Use alternative routes where possible.
Dangerous animal sighting reported. Stay indoors and avoid the area.
```

---

# 7. AI Safety Boundaries

## Safety Advisory Agent Rules

The Advisory Agent must:

- provide general safety guidance only
- avoid medical/legal certainty
- avoid instructions that increase risk
- recommend contacting official emergency services
- avoid encouraging users to approach dangerous scenes
- avoid asking users to collect risky evidence

## Example Safe Advice

### Fire

- Move away from smoke and flames.
- Do not enter the affected building.
- Keep access routes clear for responders.

### Flood

- Move to higher ground.
- Do not walk or drive through floodwater.
- Avoid drainage channels and river crossings.

### Wildlife

- Stay indoors if possible.
- Do not approach or provoke the animal.
- Keep children and pets inside.

---

# 8. Data Privacy

## Public View

Users should see:

- incident type
- general location
- severity
- alert message
- safety guidance

Users should not see:

- reporter name
- reporter phone number
- exact reporter identity
- private user movement history

## Admin View

Admins may see:

- report metadata
- confidence scores
- agent logs
- dispatch status

Admins should still not access unnecessary sensitive information.

---

# 9. Secrets Management

## Required `.gitignore`

```text
.env
.env.local
*.pem
*.key
service-account.json
credentials.json
```

## Required `.env.example`

```text
DATABASE_URL=
CLOUDANT_URL=
CLOUDANT_API_KEY=
CLOUDANT_DB=
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
IBM_CLOUD_API_KEY=
GOOGLE_MAPS_API_KEY=
WEATHER_API_KEY=
SMS_API_KEY=
JWT_SECRET=
```

## Secret Handling Rule

Never paste real API keys into:

- code
- markdown docs
- screenshots
- demo video
- Bob prompts
- GitHub commits

Use placeholders in documentation.

---

# 10. IBM Cloud and Bob Security Note

IBM Bob may not have direct access to IBM Cloud, Cloudant, watsonx.ai, or API dashboards.

If Bob cannot access a tool directly, it should guide the developer through:

1. creating the IBM Cloud service
2. generating credentials
3. copying required values into `.env`
4. testing connectivity
5. creating fallback mocks if service access is blocked

Bob should never request that real secrets be pasted into prompts.

Instead, Bob should use placeholder values and explain where each value should be inserted locally.

---

# 11. Media Upload Security

## MVP Upload Rules

- Max image size: 5MB
- Allowed types:
  - image/jpeg
  - image/png
  - image/webp
- Rename files using UUID
- Store file metadata in database
- Do not use original filename as trusted input

## Example

```text
original filename: fire.jpg
stored filename: 9f24a8e1-92aa-4d77-a991-fire.jpg
```

Better:

```text
stored filename: 9f24a8e1-92aa-4d77-a991.jpg
```

---

# 12. Audit Logging

Log important actions:

- report submitted
- verification completed
- incident confidence updated
- alert generated
- dispatch simulated
- incident resolved
- dashboard access

## Audit Fields

```text
id
actor_type
actor_id
action
entity_type
entity_id
metadata
created_at
```

For MVP, `agent_runs` and dispatch logs may be enough.

---

# 13. MVP Security Checklist

## Must Have

- `.env` and `.gitignore`
- no committed API keys
- request validation
- file size/type validation
- UUID file names
- role-based dashboard separation
- confidence thresholds before alerts
- safe advisory playbooks
- simulated dispatch instead of real authority messages

## Should Have

- rate limiting
- audit logs
- confirmation/dispute system
- incident score history
- anonymous reporting option

## Can Skip for MVP

- full enterprise IAM
- advanced malware scanning
- real government API integrations
- full encryption-at-rest configuration
- production-grade SOC monitoring

---

# 14. Security Demo Angle

During the pitch, explain:

```text
CrisisGrid AI is designed not to blindly amplify emergency reports.
It combines AI verification, cross-report confirmation, geospatial checks,
and crisis-specific thresholds before alerting users or notifying authorities.
For urgent crises like fire, it uses provisional critical alerts to avoid dangerous delays.
```

This shows responsible AI design.

---

# 15. Final Security Principle

CrisisGrid AI must balance two risks:

```text
False alarm risk
vs
Delayed response risk
```

The system should be:

```text
fast enough to protect people
careful enough to reduce misinformation
transparent enough to be trusted
```
