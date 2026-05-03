# CrisisGrid AI — Environment Variables

## Purpose

This document defines the environment variables required for CrisisGrid AI.

The goal is to make the project easy to run locally, simple to deploy, and safe from accidental credential leaks.

Environment variables are used for:

- backend configuration
- frontend configuration
- database access
- IBM Cloud services
- Cloudant access
- watsonx.ai access
- weather/map/SMS integrations
- authentication secrets
- demo mode toggles

---

## Core Principle

Never hardcode secrets in code.

Use:

```text
.env
.env.example
platform environment variables
```

Do not commit real `.env` files to GitHub.

---

# 1. Required Files

## .env

Local private configuration.

Should contain real local or demo credentials.

Must never be committed.

---

## .env.example

Safe template file.

Should contain empty placeholder values only.

This file should be committed.

---

## .gitignore

Must include:

```text
.env
.env.*
!.env.example
service-account.json
credentials.json
*.pem
*.key
```

---

# 2. Root .env.example

Recommended root-level `.env.example`:

```text
# --------------------------------------------------
# CrisisGrid AI Environment Template
# --------------------------------------------------

# App
APP_NAME=CrisisGrid AI
APP_ENV=local
APP_DEBUG=true

# Backend
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://localhost:8000/api/v1

# Frontend
FRONTEND_URL=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=

# Database - PostgreSQL
DATABASE_URL=postgresql://crisisgrid:crisisgrid_password@localhost:5432/crisisgrid
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=crisisgrid
POSTGRES_USER=crisisgrid
POSTGRES_PASSWORD=crisisgrid_password

# IBM Cloudant Optional
CLOUDANT_ENABLED=false
CLOUDANT_URL=
CLOUDANT_API_KEY=
CLOUDANT_DB_REPORTS=crisis_reports_raw
CLOUDANT_DB_AGENT_LOGS=agent_payload_logs
CLOUDANT_DB_AUDIT_EVENTS=audit_events

# IBM watsonx.ai Optional
WATSONX_ENABLED=false
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=
WATSONX_MODEL_ID=

# IBM Cloud Optional
IBM_CLOUD_API_KEY=
IBM_CLOUD_REGION=us-south
IBM_CODE_ENGINE_PROJECT=

# Weather API Optional
WEATHER_ENABLED=false
WEATHER_API_PROVIDER=openweathermap
WEATHER_API_KEY=
WEATHER_API_BASE_URL=

# Maps
MAPS_PROVIDER=google
GOOGLE_MAPS_API_KEY=
MAPBOX_ACCESS_TOKEN=

# SMS / Dispatch Optional
SMS_ENABLED=false
SMS_PROVIDER=simulated
SMS_API_KEY=
SMS_SENDER_ID=CrisisGrid
AFRICAS_TALKING_USERNAME=
AFRICAS_TALKING_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Auth
AUTH_MODE=demo
JWT_SECRET=replace_with_secure_value
JWT_EXPIRES_MINUTES=1440

# File Uploads
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE_MB=5
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/webp

# Agent Settings
AGENT_MODE=local
ENABLE_AGENT_RUN_LOGS=true
ENABLE_SIMULATED_VERIFICATION=true
ENABLE_SIMULATED_DISPATCH=true
ENABLE_DEMO_SEED_DATA=true

# Thresholds
FIRE_ALERT_THRESHOLD=0.60
FIRE_DISPATCH_THRESHOLD=0.65
FLOOD_ALERT_THRESHOLD=0.70
FLOOD_DISPATCH_THRESHOLD=0.75
WILDLIFE_ALERT_THRESHOLD=0.65
WILDLIFE_DISPATCH_THRESHOLD=0.70

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

# 3. Variable Groups

---

## 3.1 Application Variables

```text
APP_NAME
APP_ENV
APP_DEBUG
```

### APP_ENV Values

```text
local
staging
production
demo
```

### Usage

Use these to control environment-specific behavior.

Example:

```text
APP_ENV=demo
ENABLE_DEMO_SEED_DATA=true
```

---

## 3.2 Backend Variables

```text
API_HOST
API_PORT
API_BASE_URL
```

### Example

```text
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://localhost:8000/api/v1
```

---

## 3.3 Frontend Variables

Frontend variables that are exposed to the browser must use the required frontend prefix.

For Next.js:

```text
NEXT_PUBLIC_API_BASE_URL
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
```

### Important

Never put private backend secrets in `NEXT_PUBLIC_*` variables.

These are visible in the browser.

---

# 4. Database Variables

## PostgreSQL

```text
DATABASE_URL
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

### Local Example

```text
DATABASE_URL=postgresql://crisisgrid:crisisgrid_password@localhost:5432/crisisgrid
```

---

## Cloudant Optional

```text
CLOUDANT_ENABLED
CLOUDANT_URL
CLOUDANT_API_KEY
CLOUDANT_DB_REPORTS
CLOUDANT_DB_AGENT_LOGS
CLOUDANT_DB_AUDIT_EVENTS
```

### Recommended Usage

Use Cloudant for:

- raw report payloads
- agent payload logs
- audit events

Use PostgreSQL for:

- structured reports
- incidents
- alerts
- dispatch logs
- agent runs

---

## Hybrid Database Mode

Recommended long-term and IBM-aligned mode:

```text
PostgreSQL = structured incident intelligence
Cloudant = raw AI/report/audit payloads
```

### Example Toggle

```text
CLOUDANT_ENABLED=true
```

If Cloudant is unavailable:

```text
CLOUDANT_ENABLED=false
```

Backend should continue working with PostgreSQL only.

---

# 5. IBM Cloud and watsonx Variables

## IBM Cloud

```text
IBM_CLOUD_API_KEY
IBM_CLOUD_REGION
IBM_CODE_ENGINE_PROJECT
```

## watsonx.ai

```text
WATSONX_ENABLED
WATSONX_API_KEY
WATSONX_PROJECT_ID
WATSONX_URL
WATSONX_MODEL_ID
```

### Recommended MVP Usage

Set:

```text
WATSONX_ENABLED=false
```

until core app works.

Then enable watsonx.ai for:

- rewriting safety advice
- classifying report descriptions
- generating alert wording

---

# 6. Weather Variables

```text
WEATHER_ENABLED
WEATHER_API_PROVIDER
WEATHER_API_KEY
WEATHER_API_BASE_URL
```

### Recommended MVP Usage

Start with:

```text
WEATHER_ENABLED=false
```

Use simulated weather context first.

Then enable real API if time allows.

---

# 7. Maps Variables

```text
MAPS_PROVIDER
GOOGLE_MAPS_API_KEY
MAPBOX_ACCESS_TOKEN
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
```

### Important

Map keys used in the browser may be public but should be restricted by domain in the provider dashboard where possible.

For MVP:

```text
MAPS_PROVIDER=google
```

or:

```text
MAPS_PROVIDER=mock
```

if map setup becomes a blocker.

---

# 8. SMS / Dispatch Variables

```text
SMS_ENABLED
SMS_PROVIDER
SMS_API_KEY
SMS_SENDER_ID
AFRICAS_TALKING_USERNAME
AFRICAS_TALKING_API_KEY
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER
```

### Recommended MVP Usage

Use simulated dispatch first.

```text
SMS_ENABLED=false
SMS_PROVIDER=simulated
ENABLE_SIMULATED_DISPATCH=true
```

This avoids sending real messages during the hackathon.

---

# 9. Auth Variables

```text
AUTH_MODE
JWT_SECRET
JWT_EXPIRES_MINUTES
```

### AUTH_MODE Values

```text
demo
jwt
firebase
```

### Recommended MVP

```text
AUTH_MODE=demo
```

This allows faster solo execution.

Switch to JWT or Firebase only if time allows.

---

# 10. File Upload Variables

```text
UPLOAD_DIR
MAX_UPLOAD_SIZE_MB
ALLOWED_IMAGE_TYPES
```

### Example

```text
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE_MB=5
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/webp
```

### Upload Rules

- Use UUID filenames
- Do not trust original filename
- Validate MIME type
- Limit file size

---

# 11. Agent Variables

```text
AGENT_MODE
ENABLE_AGENT_RUN_LOGS
ENABLE_SIMULATED_VERIFICATION
ENABLE_SIMULATED_DISPATCH
ENABLE_DEMO_SEED_DATA
```

### AGENT_MODE Values

```text
local
watsonx
orchestrate
hybrid
```

### Recommended MVP

```text
AGENT_MODE=local
ENABLE_AGENT_RUN_LOGS=true
ENABLE_SIMULATED_VERIFICATION=true
ENABLE_SIMULATED_DISPATCH=true
```

---

# 12. Threshold Variables

```text
FIRE_ALERT_THRESHOLD
FIRE_DISPATCH_THRESHOLD
FLOOD_ALERT_THRESHOLD
FLOOD_DISPATCH_THRESHOLD
WILDLIFE_ALERT_THRESHOLD
WILDLIFE_DISPATCH_THRESHOLD
```

### Example

```text
FIRE_ALERT_THRESHOLD=0.60
FIRE_DISPATCH_THRESHOLD=0.65
FLOOD_ALERT_THRESHOLD=0.70
FLOOD_DISPATCH_THRESHOLD=0.75
WILDLIFE_ALERT_THRESHOLD=0.65
WILDLIFE_DISPATCH_THRESHOLD=0.70
```

### Why Environment Thresholds Matter

They let you tune the demo without changing code.

Example:

For demo, if a fire report is not triggering:

```text
FIRE_ALERT_THRESHOLD=0.55
```

---

# 13. Logging Variables

```text
LOG_LEVEL
LOG_FORMAT
```

### Example

```text
LOG_LEVEL=INFO
LOG_FORMAT=json
```

Recommended levels:

```text
DEBUG
INFO
WARNING
ERROR
```

---

# 14. Environment Modes

## Local Mode

```text
APP_ENV=local
AUTH_MODE=demo
CLOUDANT_ENABLED=false
WATSONX_ENABLED=false
WEATHER_ENABLED=false
ENABLE_SIMULATED_VERIFICATION=true
ENABLE_SIMULATED_DISPATCH=true
```

Best for fast coding.

---

## Demo Mode

```text
APP_ENV=demo
AUTH_MODE=demo
ENABLE_DEMO_SEED_DATA=true
ENABLE_AGENT_RUN_LOGS=true
ENABLE_SIMULATED_DISPATCH=true
```

Best for judging.

---

## IBM-Enhanced Mode

```text
APP_ENV=demo
CLOUDANT_ENABLED=true
WATSONX_ENABLED=true
WEATHER_ENABLED=true
ENABLE_SIMULATED_DISPATCH=true
```

Best if IBM services are working.

---

## Production Future Mode

```text
APP_ENV=production
APP_DEBUG=false
AUTH_MODE=jwt
CLOUDANT_ENABLED=true
WATSONX_ENABLED=true
ENABLE_SIMULATED_DISPATCH=false
```

Not required for hackathon MVP.

---

# 15. Bob Guidance for Missing Access

IBM Bob may not be able to directly access:

- IBM Cloud dashboard
- Cloudant console
- watsonx.ai Prompt Lab
- Google Maps console
- Weather API dashboard
- SMS gateway dashboard

If Bob lacks access, it should guide you through:

1. creating the service
2. locating credentials
3. creating API keys
4. adding values to `.env`
5. testing connectivity
6. creating a fallback mock

Bob should not ask you to paste real API keys into prompts.

---

## Example Bob Instruction

```text
If you cannot access my IBM Cloud account directly, give me step-by-step instructions to create a Cloudant service, generate an API key, and update my .env file. Use placeholders only.
```

---

# 16. Safe Placeholder Format

Use placeholders like:

```text
CLOUDANT_API_KEY=replace_me
WATSONX_API_KEY=replace_me
GOOGLE_MAPS_API_KEY=replace_me
```

Do not use real-looking keys in documentation.

---

# 17. Environment Validation

Backend should validate required variables at startup.

## Required for local MVP

```text
DATABASE_URL
JWT_SECRET
UPLOAD_DIR
```

## Optional

```text
CLOUDANT_API_KEY
WATSONX_API_KEY
WEATHER_API_KEY
SMS_API_KEY
GOOGLE_MAPS_API_KEY
```

Optional variables should only be required if their feature is enabled.

Example:

```text
If CLOUDANT_ENABLED=true, CLOUDANT_URL and CLOUDANT_API_KEY are required.
```

---

# 18. Startup Validation Pseudocode

```python
if settings.CLOUDANT_ENABLED:
    require("CLOUDANT_URL")
    require("CLOUDANT_API_KEY")

if settings.WATSONX_ENABLED:
    require("WATSONX_API_KEY")
    require("WATSONX_PROJECT_ID")

if settings.SMS_ENABLED:
    require("SMS_PROVIDER")
```

---

# 19. Final Environment Principle

The system should run even when optional services are unavailable.

Core MVP should work with:

```text
FastAPI + React + PostgreSQL + simulated agents
```

Then optional services can enhance it:

```text
Cloudant + watsonx.ai + Weather API + SMS
```

This keeps the project resilient during the hackathon.
