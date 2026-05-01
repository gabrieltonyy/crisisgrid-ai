# CrisisGrid AI — Contribution Guide

## Purpose

This document defines how to contribute to the CrisisGrid AI project.

Although this is currently a **solo hackathon project**, this guide ensures:

- clean development workflow
- structured code contributions
- easy future collaboration
- clear expectations for code quality
- alignment with architecture and IBM hackathon requirements

---

## Core Principle

```text
Every change should improve clarity, stability, or demo quality.
```

---

# 1. Contribution Philosophy

Even as a solo developer, follow contribution discipline:

- write clean commits
- keep changes small and focused
- update documentation when needed
- test critical logic
- avoid breaking working demo flows

This makes debugging easier and prepares the project for future team scaling.

---

# 2. Repository Structure Awareness

Before contributing, understand the structure:

```text
apps/web-app        → frontend
services/backend    → API + agents + logic
shared/             → shared schemas/constants
docs/               → documentation
infrastructure/     → docker, scripts, deployment
bob_sessions/       → IBM Bob evidence
```

Do not mix responsibilities across folders.

---

# 3. Branching Strategy

## Recommended Approach (Solo)

Use:

```text
main → stable branch
feature/* → new features
```

### Example

```text
feature/report-submission
feature/verification-agent
feature/dashboard-ui
```

---

## Rules

- Keep `main` always working
- Merge frequently
- Avoid long-lived branches
- Delete branches after merge

---

# 4. Commit Message Standards

Use clear, structured commit messages.

## Format

```text
type: short description
```

## Types

```text
feat     → new feature
fix      → bug fix
docs     → documentation
test     → tests
chore    → tooling/setup
refactor → code improvement
```

## Examples

```text
feat: add crisis report submission endpoint
feat: implement fire provisional critical threshold
fix: prevent low-confidence dispatch
docs: add system architecture document
test: add credibility engine tests
chore: add docker-compose setup
```

---

# 5. Pull Requests (Optional for Solo)

Pull requests are optional but recommended for larger changes.

## When to Use PRs

- large feature additions
- architecture changes
- major refactoring

## PR Guidelines

- include clear title
- describe changes
- link to related docs
- ensure tests pass
- verify demo flow still works

---

# 6. Coding Standards Enforcement

Follow:

- CodingStandards.md
- SharedSchemas.md
- SystemArchitecture.md

## Key Rules

- small functions
- clear naming
- separation of concerns
- schema consistency
- no hardcoded secrets

---

# 7. Backend Contribution Rules

## Required

- use Pydantic schemas
- keep routes thin
- use services/orchestrator
- use repositories for DB access
- log agent runs

## Example Flow

```text
route → service/orchestrator → agent → decision engine → repository → database
```

---

# 8. Frontend Contribution Rules

## Required

- use reusable components
- use API client abstraction
- follow TypeScript interfaces
- keep UI simple and readable
- avoid unnecessary complexity

---

# 9. Agent Contribution Rules

Each agent must:

- have one responsibility
- return structured output
- include explanation summary
- log execution

Example:

```python
class VerificationAgent:
    async def run(self, input_data):
        return {
            "confidence": 0.7,
            "summary": "Fire detected from image"
        }
```

---

# 10. Documentation Rules

Whenever you:

- add a feature
- change architecture
- modify APIs

You must update:

```text
docs/
```

Minimum updates:

- API_Specification.md
- relevant architecture file
- README.md if needed

---

# 11. Testing Requirements

Before committing:

```bash
cd services/backend
pytest

cd ../../apps/web-app
npm run build
```

## Must Verify

- report submission works
- agent pipeline runs
- alerts are generated
- dashboard loads

---

# 12. Security Rules

## Never Commit

```text
.env
API keys
passwords
credentials.json
service-account.json
```

## Always Use

```text
.env.example
environment variables
```

---

# 13. IBM Bob Contribution Workflow

IBM Bob is a key part of this project.

## Use Bob To

- generate code
- scaffold services
- create tests
- build UI components
- write documentation
- debug issues

---

## Bob Usage Rules

When using Bob:

- provide clear prompts
- include project context
- reference existing structure
- request modular output
- validate generated code manually

---

## Important Rule

Bob may not have access to:

- IBM Cloud dashboard
- Cloudant
- watsonx.ai
- API consoles

If Bob cannot access a tool:

It should:

1. explain what is missing  
2. guide you step-by-step  
3. provide mock fallback  
4. use placeholder values  

Bob should never ask for real secrets.

---

# 14. File Naming Conventions

## Backend

```text
snake_case.py
```

Examples:

```text
verification_agent.py
report_orchestrator.py
credibility_engine.py
```

---

## Frontend

```text
PascalCase.tsx
```

Examples:

```text
ReportForm.tsx
IncidentMap.tsx
AlertCard.tsx
```

---

# 15. Contribution Workflow

## Step-by-Step

```text
1. Create feature branch
2. Implement feature
3. Run tests
4. Build frontend
5. Update docs
6. Commit changes
7. Merge to main
```

---

# 16. Demo Protection Rule

Before merging any change, verify:

```text
report → verify → cluster → alert → dispatch → dashboard
```

If this flow breaks, fix before proceeding.

---

# 17. Bob Sessions Contribution

All IBM Bob outputs must be stored.

## Folder

```text
bob_sessions/
```

## Required

- session exports
- screenshots
- summaries

## Purpose

- hackathon requirement
- proof of AI-assisted development
- demonstration of workflow

---

# 18. Pre-Submission Checklist

Before final submission:

## Code

- no broken endpoints
- no missing dependencies
- frontend builds
- backend runs
- tests pass

## Security

- no secrets committed
- `.env` not pushed
- `.env.example` updated

## Documentation

- README complete
- architecture docs updated
- API documented
- demo scenarios included

## Demo

- fire scenario works
- flood scenario works
- dashboard works
- alerts visible
- dispatch simulation visible

## IBM Requirements

- Bob sessions exported
- Bob screenshots included
- explanation of Bob usage ready

---

# 19. Future Contributors

If this project expands:

- enforce PR reviews
- add code owners
- require CI checks before merge
- introduce branch protection

---

# 20. Final Contribution Principle

```text
Keep the system clean, consistent, and demo-ready.
```

Every contribution should make CrisisGrid AI:

- easier to understand
- easier to demo
- more reliable
- more aligned with hackathon goals
