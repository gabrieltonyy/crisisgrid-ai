# CrisisGrid AI — IBM Product Access Requirements

## Document Purpose

This document identifies all IBM products, external services, and tools that may be used in CrisisGrid AI, explains what access is required, and provides guidance for setup when IBM Bob cannot perform tasks directly.

**Key Principle:** The system must work locally even if optional IBM services are unavailable.

---

# 1. IBM Bob IDE

## Status
**MANDATORY** - Required for hackathon proof and judging

## Purpose
- Primary development assistant
- Code generation and scaffolding
- Documentation creation
- Testing assistance
- Proof of AI-assisted development

## What IBM Bob Can Do
- Generate code files and structures
- Create API endpoints and schemas
- Write database models
- Generate React components
- Create tests
- Write documentation
- Refactor code
- Explain architecture decisions

## What You Must Do
1. Install IBM Bob IDE
2. Select hackathon Bob account
3. Create `bob_sessions/` folder in repository
4. Export Bob task session reports regularly
5. Take screenshots of Bob sessions
6. Document which files Bob generated

## Required Repository Structure
```
bob_sessions/
├── README.md
├── screenshots/
│   ├── bob-architecture-session.png
│   ├── bob-backend-session.png
│   ├── bob-frontend-session.png
│   └── bob-agents-session.png
└── exports/
    ├── phase-0-setup.md
    ├── phase-1-backend.md
    ├── phase-2-schemas.md
    └── [other-phases].md
```

## Evidence Requirements
- Export session reports after each major phase
- Capture screenshots showing Bob's contributions
- Document in README which components Bob helped build
- Maintain clear narrative of Bob's role

## Bobcoin Management
- **Budget:** 40 Bobcoins for entire hackathon
- **Strategy:** Use Bob for scaffolding and complex logic
- **Avoid:** Using Bob for simple edits or debugging
- **Track:** Keep count of Bob usage per phase

## Setup Checklist
- [ ] IBM Bob IDE installed
- [ ] Hackathon account selected
- [ ] `bob_sessions/` folder created
- [ ] Screenshot tool ready
- [ ] Session export process understood

---

# 2. IBM Cloudant

## Status
**OPTIONAL** - Enhances but not required for MVP

## Purpose
- Store raw report payloads
- Log agent processing payloads
- Audit event storage
- Demonstrate IBM Cloud integration

## Use Cases in CrisisGrid AI
1. **Raw Report Storage:** Store original JSON payloads
2. **Agent Payload Logs:** Store full agent inputs/outputs
3. **Audit Trail:** Track all system actions
4. **Backup:** Secondary storage for critical data

## Architecture Strategy
```
PostgreSQL = Structured incident intelligence (primary)
Cloudant = Raw payloads and logs (optional enhancement)
```

## Required Environment Variables
```bash
CLOUDANT_ENABLED=false
CLOUDANT_URL=
CLOUDANT_API_KEY=
CLOUDANT_DB_REPORTS=crisis_reports_raw
CLOUDANT_DB_AGENT_LOGS=agent_payload_logs
CLOUDANT_DB_AUDIT_EVENTS=audit_events
```

## What IBM Bob Cannot Do
- Create Cloudant service instance
- Generate API keys
- Access IBM Cloud console
- Configure databases

## What You Must Do Manually

### Step 1: Create Cloudant Instance
1. Log in to IBM Cloud: https://cloud.ibm.com
2. Navigate to Catalog
3. Search for "Cloudant"
4. Click "Create"
5. Select plan (Lite is sufficient for hackathon)
6. Choose region (us-south recommended)
7. Name: `crisisgrid-cloudant`
8. Click "Create"

### Step 2: Generate API Key
1. Open your Cloudant instance
2. Go to "Service credentials"
3. Click "New credential"
4. Name: `crisisgrid-api-key`
5. Role: Manager
6. Click "Add"
7. View credentials and copy:
   - `url` → CLOUDANT_URL
   - `apikey` → CLOUDANT_API_KEY

### Step 3: Create Databases
1. Open Cloudant Dashboard
2. Click "Create Database"
3. Create three databases:
   - `crisis_reports_raw`
   - `agent_payload_logs`
   - `audit_events`
4. Use default settings (non-partitioned)

### Step 4: Update Environment
```bash
# In your .env file
CLOUDANT_ENABLED=true
CLOUDANT_URL=https://your-instance.cloudantnosqldb.appdomain.cloud
CLOUDANT_API_KEY=your_api_key_here
CLOUDANT_DB_REPORTS=crisis_reports_raw
CLOUDANT_DB_AGENT_LOGS=agent_payload_logs
CLOUDANT_DB_AUDIT_EVENTS=audit_events
```

### Step 5: Test Connection
```python
# Test script Bob can generate
from cloudant.client import Cloudant
client = Cloudant.iam(
    account_name="your-account",
    api_key="your-api-key"
)
client.connect()
print("Connected to Cloudant!")
client.disconnect()
```

## Fallback Strategy
If Cloudant setup fails or takes too long:
```bash
CLOUDANT_ENABLED=false
```
System will work with PostgreSQL only.

## MVP Recommendation
**Start with:** `CLOUDANT_ENABLED=false`
**Enable later:** After core MVP works

---

# 3. watsonx.ai

## Status
**OPTIONAL** - Enhances AI capabilities but not required

## Purpose
- Enhance safety advice wording
- Classify report descriptions
- Generate alert messages
- Improve agent reasoning
- Demonstrate IBM AI integration

## Use Cases in CrisisGrid AI
1. **Safety Advice Enhancement:** Rewrite playbook advice in user-friendly language
2. **Report Classification:** Improve crisis type detection
3. **Alert Wording:** Generate clear, calm alert messages
4. **Confidence Explanation:** Generate human-readable reasoning

## Required Environment Variables
```bash
WATSONX_ENABLED=false
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2
```

## What IBM Bob Cannot Do
- Create watsonx.ai project
- Generate API keys
- Access Prompt Lab
- Configure models

## What You Must Do Manually

### Step 1: Access watsonx.ai
1. Log in to IBM Cloud: https://cloud.ibm.com
2. Navigate to watsonx.ai
3. Create or select a project
4. Note your Project ID

### Step 2: Generate API Key
1. Go to IBM Cloud API Keys: https://cloud.ibm.com/iam/apikeys
2. Click "Create"
3. Name: `crisisgrid-watsonx-key`
4. Description: "CrisisGrid AI watsonx.ai access"
5. Click "Create"
6. Copy and save the API key securely

### Step 3: Select Model
Recommended models:
- `ibm/granite-13b-chat-v2` - General purpose
- `meta-llama/llama-2-70b-chat` - Advanced reasoning
- `google/flan-ul2` - Text generation

### Step 4: Update Environment
```bash
WATSONX_ENABLED=true
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2
```

### Step 5: Test Integration
```python
# Test script Bob can generate
from ibm_watson_machine_learning.foundation_models import Model

model = Model(
    model_id="ibm/granite-13b-chat-v2",
    credentials={
        "apikey": "your_api_key",
        "url": "https://us-south.ml.cloud.ibm.com"
    },
    project_id="your_project_id"
)

response = model.generate_text("Test prompt")
print(response)
```

## Integration Points

### Advisory Agent Enhancement
```python
# Before watsonx.ai
advice = "Move to higher ground. Avoid flood water."

# After watsonx.ai
advice = watsonx_client.enhance_safety_advice(
    crisis_type="FLOOD",
    base_advice=advice
)
# Result: More natural, context-aware guidance
```

### Report Classification
```python
# Use watsonx.ai to classify ambiguous reports
classification = watsonx_client.classify_report(
    description="Water rising quickly in street"
)
# Returns: FLOOD with confidence score
```

## Fallback Strategy
If watsonx.ai unavailable:
```bash
WATSONX_ENABLED=false
```
System uses rule-based logic and static playbooks.

## MVP Recommendation
**Start with:** `WATSONX_ENABLED=false`
**Enable later:** After core verification works

---

# 4. IBM Code Engine

## Status
**OPTIONAL** - For deployment demonstration

## Purpose
- Deploy backend container
- Deploy frontend container
- Demonstrate cloud deployment
- Show scalability potential

## Use Cases
- Host FastAPI backend
- Host Next.js frontend
- Demonstrate production-ready architecture

## Required Environment Variables
```bash
IBM_CLOUD_API_KEY=
IBM_CLOUD_REGION=us-south
IBM_CODE_ENGINE_PROJECT=crisisgrid-demo
```

## What IBM Bob Cannot Do
- Create Code Engine project
- Deploy containers
- Configure networking
- Set up domains

## What You Must Do Manually

### Step 1: Create Code Engine Project
1. Log in to IBM Cloud
2. Navigate to Code Engine
3. Click "Create project"
4. Name: `crisisgrid-demo`
5. Region: us-south
6. Click "Create"

### Step 2: Prepare Containers
Bob can generate:
- `Dockerfile` for backend
- `Dockerfile` for frontend
- Deployment configuration files

### Step 3: Deploy Backend
```bash
# Bob can generate this script
ibmcloud ce application create \
  --name crisisgrid-backend \
  --image your-registry/crisisgrid-backend:latest \
  --port 8000 \
  --env-from-configmap crisisgrid-config
```

### Step 4: Deploy Frontend
```bash
# Bob can generate this script
ibmcloud ce application create \
  --name crisisgrid-frontend \
  --image your-registry/crisisgrid-frontend:latest \
  --port 3000
```

## Fallback Strategy
If Code Engine deployment fails:
- Run locally with Docker Compose
- Use local development servers
- Demo from localhost

## MVP Recommendation
**Priority:** LOW - Focus on local demo first
**Deploy only if:** Time permits after MVP complete

---

# 5. PostgreSQL / PostGIS

## Status
**REQUIRED** - Primary database for MVP

## Purpose
- Store structured incident data
- Store reports, alerts, dispatch logs
- Store agent runs
- Optional: Geospatial queries with PostGIS

## Required Environment Variables
```bash
DATABASE_URL=postgresql://crisisgrid:crisisgrid_password@localhost:5432/crisisgrid
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=crisisgrid
POSTGRES_USER=crisisgrid
POSTGRES_PASSWORD=crisisgrid_password
```

## Setup Options

### Option 1: Docker Compose (Recommended)
```yaml
# Bob can generate docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: crisisgrid
      POSTGRES_USER: crisisgrid
      POSTGRES_PASSWORD: crisisgrid_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start with:
```bash
docker-compose up -d
```

### Option 2: Local Installation

#### macOS
```bash
brew install postgresql@14
brew services start postgresql@14
createdb crisisgrid
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb crisisgrid
```

#### Windows
1. Download PostgreSQL installer
2. Run installer
3. Use pgAdmin to create database

### Option 3: PostGIS (Optional)
For geospatial queries:
```bash
# Docker
docker run --name crisisgrid-postgis \
  -e POSTGRES_PASSWORD=crisisgrid_password \
  -p 5432:5432 \
  -d postgis/postgis:14-3.3

# Or add to existing PostgreSQL
CREATE EXTENSION postgis;
```

## What IBM Bob Can Do
- Generate database schema SQL
- Create SQLAlchemy models
- Generate migration scripts
- Create seed data scripts
- Write connection utilities

## What You Must Do
- Install PostgreSQL
- Create database
- Run schema initialization
- Configure connection string

## Testing Connection
```bash
# Test with psql
psql postgresql://crisisgrid:crisisgrid_password@localhost:5432/crisisgrid

# Test with Python
python -c "import psycopg2; conn = psycopg2.connect('postgresql://crisisgrid:crisisgrid_password@localhost:5432/crisisgrid'); print('Connected!')"
```

## Fallback Strategy
If PostgreSQL setup fails:
- Use SQLite for quick MVP
- Bob can generate SQLite configuration
- Switch to PostgreSQL later

## MVP Recommendation
**Required:** YES - Set up first
**PostGIS:** Optional - Add if time allows

---

# 6. External APIs

## 6.1 Google Maps / Mapbox

### Status
**OPTIONAL** - Enhances visualization

### Purpose
- Display crisis locations on map
- Show risk radius circles
- Visualize incident clusters
- Provide location picker

### Required Variables
```bash
MAPS_PROVIDER=google
GOOGLE_MAPS_API_KEY=
# OR
MAPS_PROVIDER=mapbox
MAPBOX_ACCESS_TOKEN=
```

### Setup Steps

#### Google Maps
1. Go to Google Cloud Console
2. Enable Maps JavaScript API
3. Create API key
4. Restrict key to your domain
5. Add to `.env`

#### Mapbox
1. Sign up at mapbox.com
2. Get access token
3. Add to `.env`

### Fallback Strategy
```bash
MAPS_PROVIDER=mock
```
Use simple coordinate display without map.

### MVP Recommendation
**Priority:** MEDIUM - Add after core features work

---

## 6.2 Weather API

### Status
**OPTIONAL** - Enhances flood verification

### Purpose
- Confirm flood reports with rainfall data
- Add external signal to confidence scoring
- Demonstrate multi-source verification

### Required Variables
```bash
WEATHER_ENABLED=false
WEATHER_API_PROVIDER=openweathermap
WEATHER_API_KEY=
WEATHER_API_BASE_URL=https://api.openweathermap.org/data/2.5
```

### Setup Steps
1. Sign up at openweathermap.org
2. Get free API key
3. Add to `.env`
4. Enable in config

### Fallback Strategy
```bash
WEATHER_ENABLED=false
```
Use simulated weather signals for demo.

### MVP Recommendation
**Priority:** LOW - Simulate first, add real API if time allows

---

## 6.3 SMS / Dispatch APIs

### Status
**OPTIONAL** - For real dispatch simulation

### Purpose
- Send real SMS alerts (demo only)
- Simulate authority notifications
- Show real-world integration potential

### Options

#### Africa's Talking (Kenya-focused)
```bash
SMS_ENABLED=false
SMS_PROVIDER=africas_talking
AFRICAS_TALKING_USERNAME=
AFRICAS_TALKING_API_KEY=
```

#### Twilio (Global)
```bash
SMS_ENABLED=false
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

### Fallback Strategy (Recommended for MVP)
```bash
SMS_ENABLED=false
SMS_PROVIDER=simulated
ENABLE_SIMULATED_DISPATCH=true
```
Store dispatch logs in database only.

### MVP Recommendation
**Priority:** LOW - Use simulated dispatch for MVP

---

# 7. Tasks IBM Bob Cannot Perform Directly

## Cloud Service Creation
**Bob Cannot:**
- Create IBM Cloud services
- Generate real API keys
- Access cloud dashboards
- Configure billing

**Bob Can:**
- Generate setup instructions
- Create configuration templates
- Write integration code
- Generate test scripts

**You Must:**
- Log in to cloud consoles
- Create services manually
- Generate and copy API keys
- Update `.env` file

---

## API Key Generation
**Bob Cannot:**
- Access third-party dashboards
- Generate real API keys
- Verify billing/credits

**Bob Can:**
- Provide step-by-step instructions
- Generate placeholder configurations
- Create fallback mock implementations

**You Must:**
- Sign up for services
- Generate keys
- Copy keys to `.env`
- Never paste real keys in Bob prompts

---

## Real-Time Integrations
**Bob Cannot:**
- Send real SMS messages
- Make real API calls during generation
- Access live external services

**Bob Can:**
- Generate integration code
- Create mock implementations
- Write test utilities

**You Must:**
- Test integrations manually
- Verify API responses
- Handle rate limits

---

## Deployment
**Bob Cannot:**
- Deploy to cloud platforms
- Configure DNS
- Set up load balancers
- Manage secrets in production

**Bob Can:**
- Generate Dockerfiles
- Create deployment scripts
- Write CI/CD configurations
- Generate deployment documentation

**You Must:**
- Execute deployment commands
- Configure cloud resources
- Verify deployments
- Monitor applications

---

# 8. Pre-Development Access Checklist

## Essential (Must Complete Before Coding)
- [ ] IBM Bob IDE installed and configured
- [ ] `bob_sessions/` folder created
- [ ] PostgreSQL installed and running
- [ ] Database created and accessible
- [ ] `.env.example` created
- [ ] `.env` created from template
- [ ] Git repository initialized
- [ ] `.gitignore` configured

## Optional (Can Enable Later)
- [ ] IBM Cloudant instance created
- [ ] Cloudant API key generated
- [ ] watsonx.ai project created
- [ ] watsonx.ai API key generated
- [ ] Google Maps API key obtained
- [ ] Weather API key obtained
- [ ] SMS provider account created

## Decision Points
- [ ] **Cloudant:** Enabled / Disabled
- [ ] **watsonx.ai:** Enabled / Disabled
- [ ] **Maps:** Real / Mock
- [ ] **Weather:** Real / Simulated
- [ ] **SMS:** Real / Simulated

---

# 9. Recommended MVP Configuration

For fastest MVP development:

```bash
# Essential
DATABASE_URL=postgresql://crisisgrid:crisisgrid_password@localhost:5432/crisisgrid
JWT_SECRET=replace_with_secure_random_value
UPLOAD_DIR=uploads

# Disabled Optional Services
CLOUDANT_ENABLED=false
WATSONX_ENABLED=false
WEATHER_ENABLED=false
SMS_ENABLED=false

# Simulated Features
ENABLE_SIMULATED_VERIFICATION=true
ENABLE_SIMULATED_DISPATCH=true
ENABLE_DEMO_SEED_DATA=true

# Mock Providers
MAPS_PROVIDER=mock
SMS_PROVIDER=simulated
WEATHER_API_PROVIDER=simulated
```

This configuration allows full MVP development without external dependencies.

---

# 10. Progressive Enhancement Strategy

## Phase 1: Core MVP (No External Services)
```bash
PostgreSQL only
Simulated agents
Mock integrations
Local development
```

## Phase 2: IBM Enhancement (If Time Allows)
```bash
+ IBM Cloudant
+ watsonx.ai
Still local development
```

## Phase 3: External APIs (If Time Allows)
```bash
+ Google Maps
+ Weather API
Still simulated dispatch
```

## Phase 4: Full Integration (Post-Hackathon)
```bash
+ Real SMS
+ Real authority APIs
+ Production deployment
```

---

# 11. Security Best Practices

## Never Commit
- Real API keys
- Database passwords
- JWT secrets
- Service account files
- `.env` files

## Always Use
- `.env.example` with placeholders
- Environment variables
- `.gitignore` for secrets
- Secure key storage

## In Bob Prompts
- Never paste real API keys
- Use placeholders: `your_api_key_here`
- Request Bob generate templates only
- Update real values manually

---

# 12. Troubleshooting Guide

## PostgreSQL Connection Failed
```bash
# Check if running
pg_isready

# Check connection string
psql $DATABASE_URL

# Reset password
ALTER USER crisisgrid WITH PASSWORD 'new_password';
```

## Cloudant Connection Failed
```bash
# Verify credentials
curl -u $CLOUDANT_API_KEY:$CLOUDANT_API_KEY $CLOUDANT_URL

# Check database exists
curl $CLOUDANT_URL/_all_dbs
```

## watsonx.ai Authentication Failed
```bash
# Verify API key
curl -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=$WATSONX_API_KEY"
```

## Environment Variables Not Loading
```bash
# Check .env file exists
ls -la .env

# Verify loading in Python
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('DATABASE_URL'))"
```

---

# 13. Cost Considerations

## Free Tier Services
- IBM Cloudant Lite: Free
- watsonx.ai: Trial available
- PostgreSQL: Free (self-hosted)
- Google Maps: $200 free credit
- OpenWeatherMap: Free tier available

## Paid Services (Optional)
- IBM Code Engine: Pay per use
- Twilio SMS: Pay per message
- Africa's Talking: Pay per SMS

## Hackathon Budget
- Focus on free tiers
- Use simulated services
- Avoid unnecessary API calls
- Monitor usage

---

# 14. Support Resources

## IBM Documentation
- IBM Cloud Docs: https://cloud.ibm.com/docs
- Cloudant Docs: https://cloud.ibm.com/docs/Cloudant
- watsonx.ai Docs: https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-overview.html

## Community Support
- IBM Developer: https://developer.ibm.com
- Stack Overflow: Tag `ibm-cloud`
- GitHub Issues: For open source components

## Emergency Fallbacks
- All external services are optional
- System designed to work locally
- Mock implementations available
- Focus on core demo flow

---

# 15. Final Recommendations

## For Fastest MVP
1. Start with PostgreSQL only
2. Use simulated agents
3. Skip external APIs initially
4. Focus on core report → alert flow
5. Add IBM services after MVP works

## For Best Demo
1. Enable IBM Cloudant (if time allows)
2. Enable watsonx.ai (if time allows)
3. Use real map (if time allows)
4. Keep dispatch simulated
5. Focus on reliability over features

## For Judging Success
1. Document Bob usage thoroughly
2. Export Bob sessions regularly
3. Show IBM integration (even if optional)
4. Demonstrate multi-agent architecture
5. Ensure demo runs smoothly

---

# END OF IBM PRODUCT ACCESS REQUIREMENTS

**Remember:** The system is designed to work locally without any external services. All IBM products and external APIs are enhancements, not requirements. Focus on building a working MVP first, then progressively enhance with IBM services as time allows.

**Next Step:** Review this document, make access decisions, then begin Phase 0 of the BUILD_PLAN.md.