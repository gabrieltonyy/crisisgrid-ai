# CrisisGrid AI — Solo Hackathon Execution Plan

## Purpose

This plan updates the original CrisisGrid AI hackathon strategy for a solo participant. The goal is to keep the idea strong while reducing execution risk, controlling scope, and aligning tightly with IBM Bob Dev Day Hackathon expectations.

## 1. Solo Strategy Summary

Because this project will be built by one person, the winning approach is not to build the entire long-term CrisisGrid AI platform. The winning approach is to build a polished proof-of-concept that clearly demonstrates the complete crisis workflow:

Citizen report → IBM Bob-assisted build process → AI verification → risk scoring → map/dashboard → simulated authority dispatch → safety guidance.

The project should look ambitious, but the MVP must remain small enough to finish alone within the hackathon period.

## 2. Hackathon Alignment

The hackathon expects a proof-of-concept solution aligned with the theme “Turn idea into impact faster with IBM Bob.” IBM Bob IDE must be used as a core part of the solution build process, and the final repository must include exported Bob task session reports for judging.

CrisisGrid AI should therefore be positioned as:

> A crisis-response proof-of-concept built rapidly with IBM Bob, showing how AI-assisted development can transform a complex emergency-coordination idea into a working prototype faster.

## 3. Solo MVP Scope

### Must-Have Features

These are the features to build first:

1. Incident reporting form
2. Image upload or sample image selection
3. GPS/manual location capture
4. AI-style crisis classification
5. Verification confidence score
6. Nearby incidents map
7. Admin incident dashboard
8. Simulated authority dispatch message
9. Safety guidance panel
10. Bob session reports folder

### Nice-to-Have Features

Only build these after the must-have features work:

1. Trust score badge
2. Incident confirmation/voting
3. Weather API cross-check
4. SMS simulation
5. Analytics cards
6. Basic heatmap

### Out of Scope for Solo MVP

These should be documented as future work, not built during the hackathon:

1. Full multi-agent production orchestration
2. Real government integrations
3. Real-time push notifications
4. Full mobile app plus full web app
5. Drone, IoT, satellite and advanced predictive modelling
6. Complex Google A2A/ADK production implementation if time is limited

## 4. Recommended Solo Tech Stack

To reduce complexity, use one primary full-stack app and one backend API.

### Frontend

- React or Next.js
- Tailwind CSS
- Mapbox or Google Maps
- Recharts for simple analytics

### Backend

- Python FastAPI
- Pydantic schemas
- Simple service-layer architecture

### Database

Preferred solo option:

- SQLite for quick local demo

Stretch option:

- PostgreSQL/PostGIS if time allows

IBM-aligned option:

- IBM Cloudant for incident storage if the provisioned account is easy to access

### IBM Tools

- IBM Bob IDE: mandatory and central to development
- IBM watsonx.ai Prompt Lab: optional for safety guidance and classification prompts
- IBM watsonx Orchestrate: optional; use only if setup is smooth
- IBM Cloud services: optional; use only where they improve the demo without slowing development

## 5. IBM Bob Usage Plan

Use IBM Bob IDE for visible, judge-relevant work:

1. Generate the monorepo structure
2. Create architecture and documentation files
3. Scaffold FastAPI services
4. Scaffold React dashboard pages
5. Generate Pydantic schemas
6. Generate test cases
7. Refactor code
8. Generate README and demo instructions
9. Generate commit messages and PR-style summaries
10. Export all relevant Bob task sessions into `bob_sessions/`

This makes Bob part of both the development process and the final story.

## 6. Simplified Architecture for Solo Build

```text
React/Next.js Web App
   ↓
FastAPI Backend
   ↓
Crisis Intelligence Service Layer
   ├── Verification Service
   ├── GeoRisk Service
   ├── Dispatch Simulation Service
   ├── Safety Advisory Service
   └── Analytics Service
   ↓
SQLite / Cloudant / PostgreSQL
```

For the demo, these services can be implemented as modular backend services instead of separate deployed microservices. This preserves the multi-agent concept while keeping development realistic for one person.

## 7. Solo Execution Timeline

### Stage 1 — Foundation

- Create repository structure
- Add README
- Add docs folder
- Add `.env.example`
- Add `bob_sessions/` folder
- Generate PRD, Vision, User Stories, Architecture and MVP Scope documents

### Stage 2 — Backend MVP

- Create FastAPI app
- Add incident report endpoint
- Add verification endpoint
- Add safety advice endpoint
- Add dispatch simulation endpoint
- Add analytics endpoint
- Add mock data seed

### Stage 3 — Frontend MVP

- Build landing/dashboard layout
- Build incident reporting page
- Build incident list
- Build map view
- Build incident detail panel
- Build dispatch and safety guidance panels

### Stage 4 — Intelligence Layer

- Add confidence scoring formula
- Add crisis severity scoring
- Add radius calculation
- Add simple duplicate detection
- Add optional watsonx.ai prompt integration if time allows

### Stage 5 — Demo Polish

- Create three demo scenarios:
  - Nairobi flood alert
  - Urban fire report
  - Wildlife sighting
- Add clear UI labels
- Add sample data buttons
- Add final screenshots
- Record demo video
- Export Bob session reports

## 8. Deliverables Checklist

The final submission should include:

1. Demo video
2. Written problem statement
3. Written solution statement
4. Written statement explaining how IBM Bob was used
5. Working code repository or proof-of-concept evidence
6. `bob_sessions/` folder containing exported Bob reports and screenshots
7. README with setup and demo instructions
8. Architecture documentation
9. Safety and data-compliance notes

## 9. Judging Strategy

### Completeness and Feasibility

Keep the MVP narrow and working. Show one full end-to-end crisis flow instead of many incomplete features.

### Effectiveness and Efficiency

Emphasise how the platform reduces reporting delay, verifies incidents and routes information faster.

### Design and Usability

Make the dashboard simple, visual and judge-friendly. Use clear labels, map markers, confidence scores and next-action cards.

### Creativity and Innovation

Highlight the multi-agent crisis-intelligence concept, Kenya-based crisis narrative and citizen-to-authority workflow.

## 10. Solo Risk Management

### Main Risks

1. Overbuilding the architecture
2. Spending too much time on external API setup
3. Trying to build both mobile and web fully
4. Failing to export Bob reports
5. Weak demo story

### Mitigation

1. Build web-first
2. Use mock/synthetic data where needed
3. Simulate dispatch rather than real government integration
4. Use modular services instead of many deployed microservices
5. Keep Bob session export as a daily task
6. Make the demo scenario the product centrepiece

## 11. Final Solo Positioning

CrisisGrid AI should be pitched as:

> A solo-built, IBM Bob-powered crisis intelligence prototype that shows how one developer can rapidly transform a complex emergency-response concept into a working, explainable, and socially impactful proof of concept.

