# CrisisGrid AI — IBM Bob Master Drive Prompt

## Purpose

Use this as the **first prompt** inside IBM Bob before starting development.

This prompt instructs IBM Bob to act as a multi-role engineering team, review all project context documents, produce a structured build plan, identify missing access/tools/API keys, and prepare the project for safe chunk-by-chunk development.

---

# MASTER PROMPT FOR IBM BOB

```md
# ROLE:
You are IBM Bob acting as a combined software delivery team for the CrisisGrid AI hackathon project.

You must operate as the following roles:

1. Principal System Architect
2. Senior Backend Developer
3. Senior Frontend Developer
4. Database Administrator
5. System Analyst
6. QA / Test Engineer
7. DevOps / Deployment Advisor
8. Security Reviewer

---

# PROJECT:
CrisisGrid AI

A multi-agent crisis intelligence, community reporting, verification, alerting, and emergency coordination platform.

The project is being built for the IBM Bob Dev Day Hackathon.

The project must be built efficiently, in small safe chunks, to reduce build failures, avoid unnecessary rework, and conserve Bobcoins.

---

# FIRST TASK — READ CONTEXT DOCUMENTS

Before writing any code, you must inspect the folder:

```text
Prompt_contextdocs/
```

This folder contains all project planning and architecture markdown files.

You must read and understand all available `.md` files in that folder before making development decisions.

Expected files may include:

```text
PRD.md
Vision.md
UserStories.md
HackathonNarrative.md
CompetitiveAdvantage.md
SystemArchitecture.md
AgentArchitecture.md
API_Specification.md
DatabaseSchema.md
SecurityArchitecture.md
DeploymentArchitecture.md
SharedSchemas.md
MonorepoStructure.md
CodingStandards.md
EnvironmentVariables.md
TestingStrategy.md
CI_CD_Pipeline.md
ContributionGuide.md
AgentRoles.md
A2AProtocolContracts.md
ADKOrchestration.md
VerificationEngine.md
TrustScoringSystem.md
PromptEngineeringStandards.md
DemoScenarios.md
JudgePitchFlow.md
MVPScope.md
StretchGoals.md
RoleBasedPrompts.md
```

If any expected document is missing, do not fail. Instead:
- list what is missing
- proceed with available context
- note assumptions clearly

---

# SECOND TASK — CREATE BUILDPROJECT FOLDER

After reading the context documents, create or use the folder:

```text
Buildproject/
```

This folder will contain:
- the actual source code
- generated project files
- implementation plans
- environment setup files
- documentation updates
- tests
- deployment files

Do not place production code inside `Prompt_contextdocs/`.

That folder is only for planning context.

---

# THIRD TASK — CREATE IMPLEMENTATION PLAN FILE

Create the following file:

```text
Buildproject/BUILD_PLAN.md
```

This file must contain a structured implementation plan based on the context documents.

The plan must split development into small safe chunks.

Do NOT propose building everything at once.

The plan must include:

## 1. Project Summary
Briefly explain what CrisisGrid AI is.

## 2. Architecture Summary
Summarize:
- frontend
- backend
- agents
- database
- verification system
- alert/dispatch flow

## 3. MVP Scope
Clearly separate:
- Must build
- Should build
- Nice to have
- Out of scope

## 4. Build Phases
Split the implementation into safe phases.

Recommended phases:

```text
Phase 0: Repository and environment setup
Phase 1: Backend skeleton
Phase 2: Shared schemas and database models
Phase 3: Report submission API
Phase 4: Verification and decision engine
Phase 5: GeoRisk and clustering logic
Phase 6: Alert and dispatch simulation
Phase 7: Safety advisory logic
Phase 8: Frontend report flow
Phase 9: Dashboard and incident view
Phase 10: Demo data and testing
Phase 11: IBM Bob session export preparation
Phase 12: Deployment/readme polish
```

## 5. For Each Phase Include
For every phase, include:

```text
Goal
Files to create/update
Expected output
Acceptance criteria
Tests to run
Estimated complexity
Risk level
Bobcoin-saving advice
```

## 6. Approval Gate
At the end of each phase, include:

```text
STOP: Wait for developer approval before continuing to the next phase.
```

Do not continue building multiple phases without approval.

---

# FOURTH TASK — CREATE IBM PRODUCT ACCESS REQUIREMENTS FILE

Create the following file:

```text
Buildproject/IBM_PRODUCT_ACCESS_REQUIREMENTS.md
```

This file must list all IBM-related products/tools/services that may be used and what is required from the developer.

The file must include:

## 1. IBM Bob
Explain:
- Bob IDE is mandatory for hackathon proof
- Bob session reports must be exported
- `bob_sessions/` folder must be created
- screenshots and markdown exports should be stored

## 2. IBM Cloudant
Explain:
- whether Cloudant is required or optional
- what it can be used for
- what credentials are needed
- where to put them in `.env`
- how to create a Cloudant instance if Bob cannot do it directly

Include variables:

```text
CLOUDANT_ENABLED=
CLOUDANT_URL=
CLOUDANT_API_KEY=
CLOUDANT_DB_REPORTS=
CLOUDANT_DB_AGENT_LOGS=
```

## 3. watsonx.ai
Explain:
- optional use cases
- safety advice enhancement
- report classification
- alert wording
- what keys/project IDs are required
- how to configure `.env`

Include variables:

```text
WATSONX_ENABLED=
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=
WATSONX_MODEL_ID=
```

## 4. IBM Code Engine
Explain:
- optional deployment target
- what is needed to deploy
- what Bob can generate
- what the developer must do manually if Bob lacks access

Include:

```text
IBM_CLOUD_API_KEY=
IBM_CLOUD_REGION=
IBM_CODE_ENGINE_PROJECT=
```

## 5. PostgreSQL / PostGIS
Explain:
- local setup option
- Docker option
- PostGIS optional
- fallback if unavailable

## 6. External APIs
List possible external APIs:

```text
Google Maps or Mapbox
OpenWeatherMap or weather API
Africa's Talking / Twilio for SMS
```

For each:
- whether required for MVP
- whether it can be mocked
- required environment variables
- setup steps if Bob cannot access dashboard

## 7. Manual Tasks Bob Cannot Perform
Create a section called:

```text
Tasks Bob May Not Be Able To Perform Directly
```

Include examples:

```text
Creating IBM Cloud services from the web console
Generating real API keys
Accessing private cloud dashboards
Verifying billing/credits
Configuring third-party dashboards
Sending real SMS messages without credentials
Deploying without cloud access
```

For each unavailable task:
- explain what Bob can generate
- explain what the developer must do manually
- provide step-by-step guidance
- provide fallback option

## 8. Access Checklist
Create a simple checklist the developer can complete before coding:

```text
[ ] IBM Bob IDE installed
[ ] Hackathon Bob account selected
[ ] bob_sessions folder created
[ ] PostgreSQL available locally or via Docker
[ ] .env.example created
[ ] Cloudant decision made: enabled / disabled
[ ] watsonx decision made: enabled / disabled
[ ] Maps API decision made: real / mock
[ ] Weather API decision made: real / mock
[ ] SMS decision made: simulated / real
```

---

# FIFTH TASK — DO NOT START CODING YET

After creating:

```text
Buildproject/BUILD_PLAN.md
Buildproject/IBM_PRODUCT_ACCESS_REQUIREMENTS.md
```

Stop.

Do NOT generate application code yet.

Wait for my approval.

Your final response should include:
- summary of what you created
- key build phases
- what access/configuration decisions I must make
- request for approval to start Phase 0

---

# DEVELOPMENT RULES

When coding begins later, follow these rules:

## Rule 1: Small Chunks Only
Never generate too many files at once unless explicitly approved.

## Rule 2: Use Existing Context
Always reference the documents in `Prompt_contextdocs/`.

## Rule 3: Preserve Architecture
Follow the architecture in:
- SystemArchitecture.md
- AgentArchitecture.md
- MonorepoStructure.md
- SharedSchemas.md
- API_Specification.md

## Rule 4: MVP First
Build the MVP before stretch goals.

## Rule 5: Local First
The system must work locally even if IBM Cloudant, watsonx.ai, weather APIs, maps APIs, or SMS APIs are unavailable.

## Rule 6: Safe Fallbacks
For optional services, provide mock implementations first.

## Rule 7: No Secrets
Never request real API keys in prompts.
Use placeholders and `.env.example`.

## Rule 8: Explain Before Risky Changes
Before making major architecture or dependency changes, explain the reason and ask for approval.

## Rule 9: Test Critical Logic
Prioritize tests for:
- verification scoring
- fire provisional critical threshold
- flood confidence increase
- clustering
- alert/dispatch decisions

## Rule 10: Hackathon Evidence
Create and maintain:

```text
bob_sessions/
```

for exported IBM Bob task session reports and screenshots.

---

# EXPECTED FIRST OUTPUT

After this prompt, produce only:

```text
Buildproject/BUILD_PLAN.md
Buildproject/IBM_PRODUCT_ACCESS_REQUIREMENTS.md
```

Then stop and wait for approval.

Do not start creating the backend or frontend code yet.
```

---

# How to Use This Prompt

1. Create a folder named:

```text
Prompt_contextdocs/
```

2. Place all generated project markdown documents inside it.

3. Create or keep an empty folder:

```text
Buildproject/
```

4. Open IBM Bob IDE.

5. Paste the master prompt above.

6. Wait for Bob to generate:

```text
Buildproject/BUILD_PLAN.md
Buildproject/IBM_PRODUCT_ACCESS_REQUIREMENTS.md
```

7. Review the plan.

8. Only after approval, instruct Bob to start Phase 0.

---

# Recommended Follow-Up Prompt After Bob Creates the Plan

```md
I approve the build plan.

Proceed with Phase 0 only.

Do not proceed to Phase 1 until I approve.

Follow the BUILD_PLAN.md acceptance criteria and update the plan with completion notes.
```

---

# Final Reminder

This prompt is designed to prevent Bob from:

- overbuilding
- wasting Bobcoins
- generating too many files at once
- skipping setup requirements
- ignoring IBM hackathon deliverables
- missing required manual configuration steps

Use it as the control prompt before coding begins.
