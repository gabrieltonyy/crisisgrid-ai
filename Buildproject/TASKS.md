# CrisisGrid AI - Development Tasks

## Phase 0: Repository and Environment Setup
- [x] Create monorepo folder structure
- [x] Initialize git repository
- [x] Create `.env.example` with all variables
- [x] Create `.gitignore` with security rules
- [x] Create `bob_sessions/` folder for evidence
- [x] Set up PostgreSQL (local or Docker)
- [x] Verify database connectivity
- [x] Configure watsonx.ai credentials
- [x] Configure Cloudant credentials

## Phase 1: Backend Skeleton ⏳ IN PROGRESS
- [ ] Create backend folder structure
- [ ] Create requirements.txt with dependencies
- [ ] Create main.py with FastAPI app
- [ ] Create config.py for environment variables
- [ ] Create database session management
- [ ] Create health check endpoint
- [ ] Test server startup
- [ ] Test health endpoint
- [ ] Verify PostgreSQL connection
- [ ] Verify configuration loading

## Phase 2: Shared Schemas and Database Models
- [ ] Create Pydantic schemas for all entities
- [ ] Define enums (CrisisType, IncidentStatus, etc.)
- [ ] Create SQLAlchemy models
- [ ] Write database initialization script
- [ ] Create database migration
- [ ] Add sample data seed script
- [ ] Test schema validation

## Phase 3: Report Submission API
- [ ] Create POST /reports endpoint
- [ ] Implement report validation
- [ ] Create report repository
- [ ] Add image upload handling
- [ ] Generate unique report IDs
- [ ] Store reports with PENDING_VERIFICATION status
- [ ] Test report submission

## Phase 4: Verification and Decision Engine
- [ ] Create Verification Agent
- [ ] Implement credibility calculation
- [ ] Create threshold policy
- [ ] Build incident clustering logic
- [ ] Create report orchestrator
- [ ] Implement agent run logging
- [ ] Test verification scenarios

## Phase 5: GeoRisk and Clustering Logic
- [ ] Create GeoRisk Agent
- [ ] Implement crisis-specific radius rules
- [ ] Add distance calculation utility
- [ ] Implement clustering algorithm
- [ ] Test clustering scenarios

## Phase 6: Alert and Dispatch Simulation
- [ ] Create Alert Agent
- [ ] Create Dispatch Agent
- [ ] Implement alert message generation
- [ ] Map crisis types to authority types
- [ ] Create alert and dispatch repositories
- [ ] Test alert/dispatch flow

## Phase 7: Safety Advisory Logic
- [ ] Create Advisory Agent
- [ ] Define safety playbooks
- [ ] Implement playbook selection logic
- [ ] Add API endpoint for safety advice
- [ ] Test advisory responses

## Phase 8: Frontend Report Flow
- [ ] Initialize Next.js application
- [ ] Create report submission form
- [ ] Add crisis type selector
- [ ] Implement location capture
- [ ] Add image upload component
- [ ] Create API client
- [ ] Test report submission flow

## Phase 9: Dashboard and Incident View
- [ ] Create dashboard page
- [ ] Build incident list component
- [ ] Add incident detail view
- [ ] Create alert feed
- [ ] Add basic crisis map
- [ ] Test dashboard functionality

## Phase 10: Demo Data and Testing
- [ ] Create seed data script
- [ ] Generate demo users
- [ ] Create sample reports
- [ ] Test fire demo scenario
- [ ] Test flood demo scenario
- [ ] Test wildlife demo scenario

## Phase 11: IBM Bob Session Export
- [ ] Export Bob task session reports
- [ ] Take screenshots of Bob sessions
- [ ] Document Bob-generated files
- [ ] Create Bob usage summary
- [ ] Update README with Bob section

## Phase 12: Deployment/README Polish
- [ ] Polish main README
- [ ] Add setup instructions
- [ ] Add demo instructions
- [ ] Create architecture diagram
- [ ] Add screenshots
- [ ] Document API endpoints
- [ ] Final testing pass

---

## Current Phase: Phase 1 - Backend Skeleton
**Status:** In Progress
**Started:** 2026-05-01
**Target Completion:** Today

### Current Task Checklist
- [ ] Create backend/ folder structure
- [ ] Create requirements.txt
- [ ] Create app/main.py
- [ ] Create app/core/config.py
- [ ] Create app/db/session.py
- [ ] Create app/api/routes/health.py
- [ ] Test server startup
- [ ] Test health endpoint

---

Last Updated: 2026-05-01T19:51:00Z