# CrisisGrid AI — Build Plan

## Document Purpose

This document provides a structured, phase-by-phase implementation plan for building CrisisGrid AI for the IBM Bob Dev Day Hackathon.

**CRITICAL RULES:**
- Build in small, safe chunks
- Wait for approval before moving to next phase
- Conserve Bobcoins through careful planning
- Prioritize MVP features over stretch goals
- Ensure system works locally even without external services

---

# 1. Project Summary

## What is CrisisGrid AI?

CrisisGrid AI is a multi-agent crisis intelligence platform that transforms citizen-reported emergencies into verified, actionable intelligence for authorities and communities.

**Core Flow:**
```
Citizen Report → AI Verification → Geospatial Risk Analysis → Alert Generation → Authority Dispatch → Dashboard Visibility
```

**Key Innovation:**
- Multi-agent AI verification system
- Location-aware incident clustering
- Crisis-specific confidence thresholds
- Real-time community alerting
- Simulated authority coordination

**Target Use Cases:**
- Fire emergencies (immediate escalation)
- Flood events (cross-report verification)
- Wildlife threats (large safety radius)
- Urban accidents and security incidents

---

# 2. Architecture Summary

## Frontend
- **Technology:** React/Next.js web application
- **Purpose:** Citizen reporting interface + Authority dashboard
- **Key Features:**
  - Crisis report submission form
  - Interactive crisis map
  - Real-time alert feed
  - Authority incident dashboard
  - Safety advisory display

## Backend
- **Technology:** Python FastAPI
- **Purpose:** API gateway + Agent orchestration + Business logic
- **Key Components:**
  - RESTful API endpoints
  - Report orchestrator
  - Multi-agent processing layer
  - Decision engine
  - Database repositories

## Agents
- **Verification Agent:** Validates report credibility
- **GeoRisk Agent:** Calculates affected area and clustering
- **Alert Agent:** Generates public warnings
- **Dispatch Agent:** Creates authority notifications
- **Advisory Agent:** Provides safety guidance
- **Weather Context Agent:** (Optional) Adds environmental signals
- **Wildlife Agent:** (Optional) Classifies animal threats

## Database
- **Primary:** PostgreSQL (with optional PostGIS)
- **Optional:** IBM Cloudant for raw payloads and logs
- **Key Tables:** users, reports, incidents, alerts, dispatch_logs, agent_runs

## Verification System
- **Credibility Scoring:** Multi-factor confidence calculation
- **Clustering:** Geospatial + temporal incident grouping
- **Thresholds:** Crisis-specific alert/dispatch rules
- **Status Flow:** PENDING → PROVISIONAL_CRITICAL → VERIFIED → DISPATCHED

## Alert/Dispatch Flow
- **Alert Generation:** Proximity-based user warnings
- **Dispatch Simulation:** Authority notification logs
- **Safety Advisories:** Crisis-specific guidance playbooks

---

# 3. MVP Scope

## Must Build (Core MVP)

### Backend Core
- ✅ FastAPI application skeleton
- ✅ Report submission endpoint
- ✅ Report orchestrator service
- ✅ Verification Agent (rule-based)
- ✅ GeoRisk Agent (radius + clustering)
- ✅ Decision Engine (threshold logic)
- ✅ Alert Agent (message generation)
- ✅ Dispatch Agent (simulated notifications)
- ✅ Advisory Agent (safety playbooks)
- ✅ PostgreSQL database setup
- ✅ Agent run logging

### Frontend Core
- ✅ Report submission form
- ✅ Crisis type selection
- ✅ Location capture (GPS/manual)
- ✅ Image upload
- ✅ Alert feed display
- ✅ Basic crisis map
- ✅ Dashboard incident list
- ✅ Incident detail view

### Data & Testing
- ✅ Database schema implementation
- ✅ Seed demo data script
- ✅ Core threshold logic tests
- ✅ Demo scenario validation

### Documentation
- ✅ README with setup instructions
- ✅ API documentation
- ✅ Bob session exports
- ✅ Environment setup guide

## Should Build (If Time Allows)

- 🔶 Weather API integration (real or simulated)
- 🔶 Wildlife classification logic
- 🔶 Interactive map with markers
- 🔶 Report confirmation voting
- 🔶 Trust score display
- 🔶 Dashboard analytics
- 🔶 IBM Cloudant integration
- 🔶 watsonx.ai for text enhancement

## Nice to Have (Stretch Goals)

- ⭐ Real-time updates (WebSockets)
- ⭐ Advanced map visualizations
- ⭐ Heatmap generation
- ⭐ Mobile-responsive polish
- ⭐ Multi-language support
- ⭐ Advanced filtering/search

## Out of Scope (Post-Hackathon)

- ❌ Real authority integrations
- ❌ Real SMS sending
- ❌ Full OAuth/SSO authentication
- ❌ Complex ML model training
- ❌ IoT/sensor integrations
- ❌ Satellite data processing
- ❌ Native mobile apps
- ❌ Production deployment infrastructure

---

# 4. Build Phases

## Phase 0: Repository and Environment Setup

### Goal
Establish project structure, development environment, and foundational configuration.

### Files to Create/Update
```
Buildproject/
├── .gitignore
├── .env.example
├── README.md
├── docker-compose.yml (optional)
└── bob_sessions/
    └── README.md
```

### Tasks
1. Create monorepo folder structure
2. Initialize git repository
3. Create `.env.example` with all variables
4. Create `.gitignore` with security rules
5. Create `bob_sessions/` folder for evidence
6. Write initial README.md
7. Set up PostgreSQL (local or Docker)
8. Verify database connectivity

### Expected Output
- Clean repository structure
- Environment template ready
- Database accessible
- Git initialized with proper ignores

### Acceptance Criteria
- [ ] Folder structure matches MonorepoStructure.md
- [ ] `.env.example` contains all required variables
- [ ] PostgreSQL is running and accessible
- [ ] `bob_sessions/` folder exists
- [ ] `.gitignore` prevents credential leaks

### Tests to Run
- Database connection test
- Environment variable loading test

### Estimated Complexity
**Low** - Mostly setup and configuration

### Risk Level
**Low** - Standard setup tasks

### Bobcoin-Saving Advice
- Use Docker Compose for quick PostgreSQL setup
- Copy `.env.example` to `.env` and update values
- Don't spend time on complex deployment yet

**STOP: Wait for developer approval before continuing to Phase 1.**

---

## Phase 1: Backend Skeleton

### Goal
Create FastAPI application foundation with health check and basic routing structure.

### Files to Create/Update
```
services/backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── api/
│   │   ├── api_router.py
│   │   └── routes/
│   │       └── health_routes.py
│   └── schemas/
│       └── common.py
├── requirements.txt
└── README.md
```

### Tasks
1. Create FastAPI application in `main.py`
2. Set up configuration management (`config.py`)
3. Create health check endpoint
4. Set up CORS middleware
5. Create common response schemas
6. Add basic error handling
7. Create requirements.txt with dependencies
8. Test server startup

### Expected Output
- FastAPI server running on port 8000
- Health endpoint responding: `GET /health`
- CORS configured for frontend
- Structured logging enabled

### Acceptance Criteria
- [ ] Server starts without errors
- [ ] `GET /health` returns 200 OK
- [ ] CORS allows localhost:3000
- [ ] Configuration loads from environment
- [ ] Basic error handling works

### Tests to Run
```bash
curl http://localhost:8000/health
```

### Estimated Complexity
**Low** - Standard FastAPI setup

### Risk Level
**Low** - Well-documented patterns

### Bobcoin-Saving Advice
- Use FastAPI's built-in features (validation, docs)
- Keep initial dependencies minimal
- Use Pydantic for configuration management

**STOP: Wait for developer approval before continuing to Phase 2.**

---

## Phase 2: Shared Schemas and Database Models

### Goal
Define data contracts and database schema for the entire system.

### Files to Create/Update
```
services/backend/app/
├── schemas/
│   ├── common.py
│   ├── reports.py
│   ├── incidents.py
│   ├── alerts.py
│   ├── dispatch.py
│   └── agents.py
├── models/
│   ├── user.py
│   ├── report.py
│   ├── incident.py
│   ├── alert.py
│   ├── dispatch_log.py
│   ├── agent_run.py
│   └── confirmation.py
└── database/
    ├── base.py
    ├── session.py
    └── migrations/
        └── init_schema.sql
```

### Tasks
1. Create Pydantic schemas for all entities
2. Define enums (CrisisType, IncidentStatus, etc.)
3. Create SQLAlchemy models
4. Write database initialization script
5. Create database migration
6. Add sample data seed script
7. Test schema validation

### Expected Output
- Complete Pydantic schema definitions
- SQLAlchemy models matching database design
- Database tables created
- Seed data script ready

### Acceptance Criteria
- [ ] All schemas defined with proper validation
- [ ] Database tables created successfully
- [ ] Foreign key relationships correct
- [ ] Enums match specification
- [ ] Seed script populates demo data

### Tests to Run
- Schema validation tests
- Database connection and query tests
- Seed data insertion test

### Estimated Complexity
**Medium** - Requires careful schema design

### Risk Level
**Medium** - Schema changes later are costly

### Bobcoin-Saving Advice
- Reference DatabaseSchema.md and SharedSchemas.md closely
- Use Alembic for migrations if time allows
- Keep initial schema simple, add fields later if needed

**STOP: Wait for developer approval before continuing to Phase 3.**

---

## Phase 3: Report Submission API

### Goal
Implement the core report submission endpoint and basic storage.

### Files to Create/Update
```
services/backend/app/
├── api/routes/
│   └── report_routes.py
├── repositories/
│   └── report_repository.py
├── services/
│   └── upload_service.py
└── utils/
    ├── ids.py
    └── time.py
```

### Tasks
1. Create `POST /reports` endpoint
2. Implement report validation
3. Create report repository for database operations
4. Add image upload handling
5. Generate unique report IDs
6. Store reports with PENDING_VERIFICATION status
7. Return report confirmation response
8. Add basic error handling

### Expected Output
- Working report submission endpoint
- Reports stored in database
- Image uploads handled safely
- Proper validation and error messages

### Acceptance Criteria
- [ ] `POST /api/v1/reports` accepts valid reports
- [ ] Reports saved to database
- [ ] Image uploads work (local storage)
- [ ] Validation rejects invalid data
- [ ] Unique IDs generated
- [ ] Timestamps recorded correctly

### Tests to Run
```bash
# Test report submission
curl -X POST http://localhost:8000/api/v1/reports \
  -H "Content-Type: application/json" \
  -d '{
    "crisis_type": "FIRE",
    "description": "Smoke visible",
    "latitude": -1.2921,
    "longitude": 36.8219
  }'
```

### Estimated Complexity
**Medium** - Core business logic

### Risk Level
**Medium** - Critical path for demo

### Bobcoin-Saving Advice
- Start without image upload, add later
- Use simple file storage (local uploads folder)
- Focus on JSON payload first

**STOP: Wait for developer approval before continuing to Phase 4.**

---

## Phase 4: Verification and Decision Engine

### Goal
Implement the core AI verification logic and decision-making system.

### Files to Create/Update
```
services/backend/app/
├── agents/
│   └── verification_agent.py
├── decision_engine/
│   ├── credibility_engine.py
│   ├── threshold_policy.py
│   └── incident_clustering.py
├── orchestrator/
│   └── report_orchestrator.py
└── repositories/
    ├── incident_repository.py
    └── agent_run_repository.py
```

### Tasks
1. Create Verification Agent with scoring logic
2. Implement credibility calculation formula
3. Create threshold policy for each crisis type
4. Build incident clustering logic
5. Create report orchestrator
6. Implement agent run logging
7. Connect orchestrator to report submission
8. Test verification scenarios

### Expected Output
- Reports automatically verified on submission
- Confidence scores calculated
- Incidents created/updated
- Agent runs logged
- Status transitions working

### Acceptance Criteria
- [ ] Verification Agent calculates confidence scores
- [ ] Fire reports can reach PROVISIONAL_CRITICAL
- [ ] Flood reports require higher confidence
- [ ] Clustering detects nearby similar reports
- [ ] Agent runs logged to database
- [ ] Status updates correctly

### Tests to Run
- Fire report with image → confidence >= 0.60
- Flood report alone → confidence < 0.70
- Two nearby flood reports → confidence increases
- Clustering detects reports within radius

### Estimated Complexity
**High** - Core intelligence logic

### Risk Level
**High** - Critical for demo success

### Bobcoin-Saving Advice
- Start with rule-based logic (no ML needed)
- Use simple keyword matching
- Test with demo scenarios frequently
- Log everything for debugging

**STOP: Wait for developer approval before continuing to Phase 5.**

---

## Phase 5: GeoRisk and Clustering Logic

### Goal
Implement geospatial risk calculation and incident clustering.

### Files to Create/Update
```
services/backend/app/
├── agents/
│   └── georisk_agent.py
└── utils/
    └── distance.py
```

### Tasks
1. Create GeoRisk Agent
2. Implement crisis-specific radius rules
3. Add distance calculation utility
4. Implement clustering algorithm
5. Update incident with cluster information
6. Test clustering scenarios
7. Add geospatial queries (if PostGIS available)

### Expected Output
- Risk radius calculated per crisis type
- Nearby reports clustered into incidents
- Distance calculations working
- Cluster count tracked

### Acceptance Criteria
- [ ] Fire → 500m radius
- [ ] Flood → 1000m radius
- [ ] Wildlife → 1500m radius
- [ ] Reports within radius cluster correctly
- [ ] Cluster count increases confidence
- [ ] Distance calculations accurate

### Tests to Run
- Two fire reports 300m apart → same incident
- Two fire reports 800m apart → separate incidents
- Three flood reports nearby → confidence boost

### Estimated Complexity
**Medium** - Geospatial logic

### Risk Level
**Medium** - Important for clustering demo

### Bobcoin-Saving Advice
- Use simple Haversine distance formula
- PostGIS optional for MVP
- Test with known coordinates

**STOP: Wait for developer approval before continuing to Phase 6.**

---

## Phase 6: Alert and Dispatch Simulation

### Goal
Implement alert generation and simulated authority dispatch.

### Files to Create/Update
```
services/backend/app/
├── agents/
│   ├── alert_agent.py
│   └── dispatch_agent.py
├── repositories/
│   ├── alert_repository.py
│   └── dispatch_repository.py
└── api/routes/
    ├── alert_routes.py
    └── dispatch_routes.py
```

### Tasks
1. Create Alert Agent
2. Create Dispatch Agent
3. Implement alert message generation
4. Map crisis types to authority types
5. Create alert and dispatch repositories
6. Add API endpoints for alerts
7. Store dispatch logs
8. Test alert/dispatch flow

### Expected Output
- Alerts generated for verified incidents
- Dispatch logs created
- Authority types mapped correctly
- Alert messages clear and actionable

### Acceptance Criteria
- [ ] Alerts created when threshold met
- [ ] Alert messages appropriate for crisis type
- [ ] Dispatch logs show correct authority
- [ ] `GET /alerts` returns active alerts
- [ ] Dispatch status tracked

### Tests to Run
- Fire report → alert + dispatch to FIRE_SERVICE
- Flood report → alert + dispatch to DISASTER_MANAGEMENT
- Wildlife report → alert + dispatch to WILDLIFE_AUTHORITY

### Estimated Complexity
**Medium** - Business logic

### Risk Level
**Low** - Straightforward implementation

### Bobcoin-Saving Advice
- Use template messages
- Simulate all dispatch (no real SMS)
- Keep alert logic simple

**STOP: Wait for developer approval before continuing to Phase 7.**

---

## Phase 7: Safety Advisory Logic

### Goal
Implement safety guidance system with crisis-specific playbooks.

### Files to Create/Update
```
services/backend/app/
├── agents/
│   └── advisory_agent.py
├── services/
│   └── safety_playbook_service.py
└── api/routes/
    └── advice_routes.py
```

### Tasks
1. Create Advisory Agent
2. Define safety playbooks for each crisis type
3. Implement playbook selection logic
4. Add API endpoint for safety advice
5. Test advisory responses
6. Optional: Integrate watsonx.ai for enhancement

### Expected Output
- Safety advice returned for each crisis type
- Clear, actionable guidance
- Calm, non-panic-inducing tone
- API endpoint working

### Acceptance Criteria
- [ ] Fire advice: "Move away, avoid smoke"
- [ ] Flood advice: "Move to higher ground"
- [ ] Wildlife advice: "Stay indoors, don't approach"
- [ ] Advice appropriate for severity level
- [ ] `GET /advice/{crisis_type}` works

### Tests to Run
- Request fire advice → correct guidance
- Request flood advice → correct guidance
- Request wildlife advice → correct guidance

### Estimated Complexity
**Low** - Predefined content

### Risk Level
**Low** - Simple lookup logic

### Bobcoin-Saving Advice
- Use static playbooks first
- watsonx.ai enhancement optional
- Focus on clarity over complexity

**STOP: Wait for developer approval before continuing to Phase 8.**

---

## Phase 8: Frontend Report Flow

### Goal
Build the citizen-facing report submission interface.

### Files to Create/Update
```
apps/web-app/
├── src/
│   ├── app/
│   │   ├── page.tsx
│   │   └── report/
│   │       └── page.tsx
│   ├── components/
│   │   ├── reports/
│   │   │   ├── ReportForm.tsx
│   │   │   └── CrisisTypeSelector.tsx
│   │   └── common/
│   │       ├── LocationPicker.tsx
│   │       └── ImageUpload.tsx
│   ├── lib/
│   │   └── api-client.ts
│   └── types/
│       └── crisisgrid.ts
├── package.json
└── next.config.js
```

### Tasks
1. Initialize Next.js application
2. Create report submission form
3. Add crisis type selector
4. Implement location capture (GPS/manual)
5. Add image upload component
6. Create API client for backend
7. Add form validation
8. Test report submission flow

### Expected Output
- Working report form
- Location capture functional
- Image upload working
- Form submits to backend
- Success/error feedback

### Acceptance Criteria
- [ ] Form renders correctly
- [ ] Crisis types selectable
- [ ] GPS location captured
- [ ] Manual location entry works
- [ ] Image upload functional
- [ ] Form validation prevents invalid submissions
- [ ] Success message shown after submission

### Tests to Run
- Submit fire report with all fields
- Submit flood report without image
- Test GPS location capture
- Test manual location entry
- Verify backend receives data correctly

### Estimated Complexity
**Medium** - Frontend development

### Risk Level
**Medium** - User-facing critical path

### Bobcoin-Saving Advice
- Use simple HTML5 geolocation
- Keep UI minimal initially
- Focus on functionality over design
- Use Tailwind CSS for quick styling

**STOP: Wait for developer approval before continuing to Phase 9.**

---

## Phase 9: Dashboard and Incident View

### Goal
Build the authority dashboard and incident visualization.

### Files to Create/Update
```
apps/web-app/src/
├── app/
│   ├── dashboard/
│   │   └── page.tsx
│   ├── incidents/
│   │   └── [id]/
│   │       └── page.tsx
│   └── alerts/
│       └── page.tsx
├── components/
│   ├── dashboard/
│   │   ├── IncidentList.tsx
│   │   ├── IncidentCard.tsx
│   │   └── StatsPanel.tsx
│   ├── alerts/
│   │   └── AlertFeed.tsx
│   └── map/
│       └── CrisisMap.tsx
└── lib/
    └── formatters.ts
```

### Tasks
1. Create dashboard page
2. Build incident list component
3. Add incident detail view
4. Create alert feed
5. Add basic crisis map (optional)
6. Implement data fetching
7. Add filtering/sorting
8. Test dashboard functionality

### Expected Output
- Dashboard showing all incidents
- Incident details viewable
- Alert feed displaying active alerts
- Status and confidence visible
- Dispatch logs shown

### Acceptance Criteria
- [ ] Dashboard loads incident list
- [ ] Incidents show status, confidence, severity
- [ ] Clicking incident shows details
- [ ] Alert feed shows active alerts
- [ ] Agent run logs visible (optional)
- [ ] Map shows incident locations (optional)

### Tests to Run
- Load dashboard with seeded data
- View incident details
- Check alert feed
- Verify data updates after new report

### Estimated Complexity
**Medium** - Multiple components

### Risk Level
**Medium** - Important for demo

### Bobcoin-Saving Advice
- Start with simple list view
- Map can be added later
- Focus on data display first
- Use table/card layout initially

**STOP: Wait for developer approval before continuing to Phase 10.**

---

## Phase 10: Demo Data and Testing

### Goal
Create comprehensive demo data and validate all scenarios.

### Files to Create/Update
```
services/backend/app/services/
└── seed_service.py

infrastructure/scripts/
├── seed_demo_data.py
└── reset_db.py

docs/demo/
└── DEMO_SCRIPT.md
```

### Tasks
1. Create seed data script
2. Generate demo users
3. Create sample reports for each crisis type
4. Generate incidents with various statuses
5. Create alerts and dispatch logs
6. Test all three demo scenarios
7. Write demo script document
8. Validate end-to-end flows

### Expected Output
- Database populated with realistic demo data
- All crisis types represented
- Various confidence levels shown
- Demo scenarios work smoothly

### Acceptance Criteria
- [ ] Fire demo scenario works
- [ ] Flood demo scenario works
- [ ] Wildlife demo scenario works
- [ ] Dashboard shows varied data
- [ ] All statuses represented
- [ ] Agent runs logged correctly

### Tests to Run
- Run seed script
- Execute fire demo
- Execute flood demo
- Execute wildlife demo
- Verify dashboard displays correctly

### Estimated Complexity
**Low** - Data generation

### Risk Level
**Low** - Preparation task

### Bobcoin-Saving Advice
- Use realistic but simple data
- Focus on demo scenarios
- Test frequently during development

**STOP: Wait for developer approval before continuing to Phase 11.**

---

## Phase 11: IBM Bob Session Export Preparation

### Goal
Document IBM Bob's role in development and prepare hackathon evidence.

### Files to Create/Update
```
bob_sessions/
├── README.md
├── screenshots/
│   ├── bob-architecture-session.png
│   ├── bob-backend-session.png
│   └── bob-frontend-session.png
└── exports/
    ├── phase-0-setup.md
    ├── phase-1-backend.md
    ├── phase-2-schemas.md
    └── [other-phases].md
```

### Tasks
1. Export Bob task session reports
2. Take screenshots of Bob sessions
3. Document which files Bob generated
4. Create Bob usage summary
5. Update main README with Bob section
6. Organize evidence folder
7. Write Bob contribution narrative

### Expected Output
- Complete Bob session documentation
- Screenshots of key sessions
- Clear evidence of AI-assisted development
- Narrative explaining Bob's role

### Acceptance Criteria
- [ ] `bob_sessions/` folder populated
- [ ] Screenshots captured
- [ ] Session exports saved
- [ ] README explains Bob usage
- [ ] Evidence organized for judges

### Tests to Run
- Review all Bob session exports
- Verify screenshots are clear
- Check README Bob section

### Estimated Complexity
**Low** - Documentation

### Risk Level
**Low** - Required for judging

### Bobcoin-Saving Advice
- Export sessions regularly during development
- Take screenshots as you go
- Don't wait until the end

**STOP: Wait for developer approval before continuing to Phase 12.**

---

## Phase 12: Deployment/README Polish

### Goal
Finalize documentation, polish README, and prepare for submission.

### Files to Create/Update
```
README.md
CONTRIBUTING.md
LICENSE
.env.example (final review)
docker-compose.yml (if used)
infrastructure/deployment/
└── local-deployment.md
```

### Tasks
1. Polish main README
2. Add setup instructions
3. Add demo instructions
4. Create architecture diagram
5. Add screenshots
6. Document API endpoints
7. Add troubleshooting section
8. Final testing pass
9. Create submission checklist

### Expected Output
- Professional README
- Clear setup instructions
- Demo guide
- Screenshots
- Complete documentation

### Acceptance Criteria
- [ ] README is clear and complete
- [ ] Setup instructions work
- [ ] Demo scenarios documented
- [ ] Screenshots included
- [ ] API documented
- [ ] Bob usage highlighted
- [ ] All links work

### Tests to Run
- Follow setup instructions from scratch
- Run all demo scenarios
- Verify all documentation links
- Check for typos

### Estimated Complexity
**Low** - Documentation polish

### Risk Level
**Low** - Final touches

### Bobcoin-Saving Advice
- Use Bob to help write documentation
- Keep README concise but complete
- Focus on judge-friendly presentation

**STOP: Final review and submission preparation.**

---

# 5. Phase Summary Table

| Phase | Name | Complexity | Risk | Priority | Estimated Time |
|-------|------|------------|------|----------|----------------|
| 0 | Repository Setup | Low | Low | Must | 1-2 hours |
| 1 | Backend Skeleton | Low | Low | Must | 2-3 hours |
| 2 | Schemas & Models | Medium | Medium | Must | 3-4 hours |
| 3 | Report API | Medium | Medium | Must | 2-3 hours |
| 4 | Verification Engine | High | High | Must | 4-6 hours |
| 5 | GeoRisk & Clustering | Medium | Medium | Must | 3-4 hours |
| 6 | Alert & Dispatch | Medium | Low | Must | 2-3 hours |
| 7 | Safety Advisory | Low | Low | Must | 1-2 hours |
| 8 | Frontend Report | Medium | Medium | Must | 3-4 hours |
| 9 | Dashboard | Medium | Medium | Must | 3-4 hours |
| 10 | Demo Data | Low | Low | Must | 2-3 hours |
| 11 | Bob Evidence | Low | Low | Must | 1-2 hours |
| 12 | Polish & Docs | Low | Low | Must | 2-3 hours |

**Total Estimated Time:** 29-43 hours

---

# 6. Critical Success Factors

## For Demo Success
1. ✅ Report submission works reliably
2. ✅ Verification produces visible confidence scores
3. ✅ Fire scenario triggers immediate alert
4. ✅ Flood scenario shows clustering benefit
5. ✅ Dashboard displays real-time state
6. ✅ Agent runs are logged and visible

## For Judging Success
1. ✅ Clear IBM Bob usage evidence
2. ✅ Multi-agent architecture visible
3. ✅ Real-world problem clearly addressed
4. ✅ System works during live demo
5. ✅ Code is clean and well-documented
6. ✅ Innovation is clearly explained

## For Technical Success
1. ✅ System runs locally without external dependencies
2. ✅ Graceful degradation when services unavailable
3. ✅ No hardcoded secrets
4. ✅ Database schema is sound
5. ✅ API is RESTful and documented
6. ✅ Frontend is responsive

---

# 7. Risk Mitigation Strategies

## High-Risk Areas

### Verification Logic
- **Risk:** Confidence scores don't behave as expected
- **Mitigation:** Test frequently with demo scenarios, log all calculations

### Clustering Algorithm
- **Risk:** Reports don't cluster correctly
- **Mitigation:** Use simple distance calculation, test with known coordinates

### Demo Reliability
- **Risk:** System crashes during presentation
- **Mitigation:** Use seed data, test demo flow repeatedly, have screenshots ready

### Time Management
- **Risk:** Running out of time before MVP complete
- **Mitigation:** Build phases sequentially, skip optional features, focus on core flow

## Medium-Risk Areas

### Database Setup
- **Risk:** PostgreSQL configuration issues
- **Mitigation:** Use Docker Compose, have fallback SQLite option

### Frontend Integration
- **Risk:** API integration issues
- **Mitigation:** Test API endpoints independently first, use mock data initially

### Image Upload
- **Risk:** File handling complexity
- **Mitigation:** Start without images, add later if time allows

---

# 8. Bobcoin Conservation Strategy

## High-Value Bob Usage
- Generate database models and schemas
- Create API endpoint boilerplate
- Generate agent class structures
- Write test cases
- Generate documentation

## Low-Value Bob Usage (Avoid)
- Debugging simple syntax errors
- Formatting code
- Writing trivial utility functions
- Repetitive copy-paste tasks

## Bob Usage Guidelines
1. Use Bob for scaffolding and structure
2. Use Bob for complex logic generation
3. Use Bob for documentation
4. Manually handle simple edits
5. Test Bob-generated code before proceeding

---

# 9. Development Environment Requirements

## Required Software
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Git
- IBM Bob IDE

## Optional Software
- Docker & Docker Compose
- PostGIS extension
- Redis (for future caching)

## Required Accounts/Keys
- IBM Cloud account (for optional services)
- GitHub account (for repository)

## Optional Accounts/Keys
- IBM Cloudant instance
- watsonx.ai access
- Google Maps API key
- Weather API key

---

# 10. Quality Gates

## After Each Phase
- [ ] Code runs without errors
- [ ] Tests pass (if applicable)
- [ ] Documentation updated
- [ ] Git commit with clear message
- [ ] Bob session exported (if used)

## Before Moving to Next Phase
- [ ] Current phase acceptance criteria met
- [ ] No blocking bugs
- [ ] Developer approval received
- [ ] Confidence in stability

## Before Demo
- [ ] All three demo scenarios tested
- [ ] Dashboard loads correctly
- [ ] No console errors
- [ ] Screenshots captured
- [ ] Bob evidence organized

---

# 11. Fallback Plans

## If PostgreSQL Setup Fails
- Use SQLite for MVP
- Remove PostGIS dependency
- Calculate distances in application code

## If Frontend Takes Too Long
- Focus on API completeness
- Use Postman/curl for demo
- Show API responses directly

## If Time Runs Short
- Skip optional agents (Weather, Wildlife)
- Skip map visualization
- Focus on core report → alert → dispatch flow
- Use seed data instead of live demo

## If External Services Unavailable
- All external services are optional
- System designed to work locally
- Use simulated/mock implementations

---

# 12. Success Metrics

## MVP Complete When:
- ✅ Report can be submitted via API
- ✅ Verification assigns confidence score
- ✅ Alert is generated for high-confidence reports
- ✅ Dispatch log is created
- ✅ Dashboard shows incident
- ✅ Demo scenarios work

## Hackathon Ready When:
- ✅ All MVP criteria met
- ✅ Bob sessions documented
- ✅ README is complete
- ✅ Demo script prepared
- ✅ Screenshots captured
- ✅ Repository is clean

## Stretch Goals Achieved When:
- ✅ Map visualization working
- ✅ Weather integration active
- ✅ IBM Cloudant connected
- ✅ watsonx.ai enhancing content

---

# 13. Final Reminders

## Before Starting Each Phase
1. Read the phase description completely
2. Understand the acceptance criteria
3. Check for dependencies on previous phases
4. Estimate time realistically
5. Have Bob ready if needed

## During Each Phase
1. Build incrementally
2. Test frequently
3. Commit often
4. Log issues immediately
5. Don't over-engineer

## After Each Phase
1. Verify acceptance criteria
2. Update documentation
3. Export Bob session
4. Request approval
5. Take a break

---

# 14. Contact and Support

## If Stuck
1. Review relevant context documents
2. Check API specification
3. Review database schema
4. Test with simpler data
5. Ask Bob for guidance

## Documentation References
- Vision.md - Project goals
- SystemArchitecture.md - Technical design
- AgentArchitecture.md - Agent details
- API_Specification.md - Endpoint contracts
- DatabaseSchema.md - Data models
- MVPScope.md - Feature priorities

---

# 15. Approval Process

## Phase Approval Checklist
Before requesting approval for next phase:
- [ ] All tasks completed
- [ ] Acceptance criteria met
- [ ] Tests passing
- [ ] Code committed
- [ ] Documentation updated
- [ ] No blocking issues

## Approval Request Format
```
Phase [N] Complete

Completed:
- [List of completed tasks]

Acceptance Criteria Status:
- [✓] Criterion 1
- [✓] Criterion 2

Ready for Phase [N+1]: [YES/NO]

Issues/Notes:
- [Any concerns or notes]
```

---

# END OF BUILD PLAN

**Remember:** This is a marathon, not a sprint. Build carefully, test frequently, and conserve Bobcoins. The goal is a working demo that clearly shows value, not a perfect production system.

**Next Step:** Review this plan, then proceed to create IBM_PRODUCT_ACCESS_REQUIREMENTS.md before starting Phase 0.