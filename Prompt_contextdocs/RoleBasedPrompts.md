# CrisisGrid AI — Role-Based Coding Prompts

## Purpose

This document contains **ready-to-use prompts** for IBM Bob / AI coding agents to build CrisisGrid AI.

These prompts are:

- structured
- modular
- aligned with architecture
- optimized for solo development
- compliant with hackathon expectations

---

## Core Principle

```text
One prompt = one responsibility = one output
```

---

# Prompt 1 — System Architect

## Use When

Starting the project / defining structure

```md
# ROLE:
You are a senior system architect.

# OBJECTIVE:
Design the CrisisGrid AI system architecture.

# CONTEXT:
- Multi-agent crisis intelligence system
- Backend: FastAPI
- Frontend: React
- Database: PostgreSQL
- Optional: Cloudant

# REQUIREMENTS:
- modular architecture
- agent-based design
- scalable structure
- simple MVP implementation

# OUTPUT:
- folder structure
- service breakdown
- architecture explanation
```

---

# Prompt 2 — Backend Setup

## Use When

Creating backend service

```md
# ROLE:
You are a senior backend engineer.

# OBJECTIVE:
Create FastAPI backend for CrisisGrid AI.

# REQUIREMENTS:
- POST /reports endpoint
- Pydantic models
- async support
- modular structure

# OUTPUT:
- main.py
- routes
- models
- services
```

---

# Prompt 3 — Verification Agent

```md
# ROLE:
You are an AI systems engineer.

# OBJECTIVE:
Build verification agent.

# REQUIREMENTS:
- keyword detection
- confidence scoring
- simple logic (MVP)
- return structured output

# OUTPUT:
- verification_agent.py
- scoring logic
```

---

# Prompt 4 — GeoRisk Agent

```md
# ROLE:
You are a backend engineer.

# OBJECTIVE:
Build GeoRisk agent.

# REQUIREMENTS:
- assign radius by crisis type
- simple clustering logic
- return structured output

# OUTPUT:
- georisk_agent.py
```

---

# Prompt 5 — Decision Engine

```md
# ROLE:
You are a backend engineer.

# OBJECTIVE:
Create decision engine.

# REQUIREMENTS:
- apply thresholds
- determine status
- decide alert/dispatch

# OUTPUT:
- decision_engine.py
```

---

# Prompt 6 — Alert Agent

```md
# ROLE:
You are a backend engineer.

# OBJECTIVE:
Create alert agent.

# REQUIREMENTS:
- generate alert message
- assign severity
- safe wording

# OUTPUT:
- alert_agent.py
```

---

# Prompt 7 — Dispatch Agent

```md
# ROLE:
You are a backend engineer.

# OBJECTIVE:
Create dispatch agent.

# REQUIREMENTS:
- map crisis to authority
- simulate dispatch
- log output

# OUTPUT:
- dispatch_agent.py
```

---

# Prompt 8 — Advisory Agent

```md
# ROLE:
You are an AI assistant.

# OBJECTIVE:
Generate safety advice.

# REQUIREMENTS:
- simple safe instructions
- crisis-specific

# OUTPUT:
- advisory_agent.py
```

---

# Prompt 9 — Frontend Report Form

```md
# ROLE:
You are a React developer.

# OBJECTIVE:
Create report submission form.

# REQUIREMENTS:
- fields: type, description, location
- submit to API

# OUTPUT:
- ReportForm.tsx
```

---

# Prompt 10 — Dashboard

```md
# ROLE:
You are a frontend engineer.

# OBJECTIVE:
Create dashboard.

# REQUIREMENTS:
- show incidents
- show confidence
- show status

# OUTPUT:
- Dashboard.tsx
```

---

# Prompt 11 — Testing

```md
# ROLE:
You are a QA engineer.

# OBJECTIVE:
Write pytest tests.

# REQUIREMENTS:
- test fire threshold
- test flood clustering

# OUTPUT:
- test files
```

---

# Prompt 12 — CI/CD

```md
# ROLE:
You are a DevOps engineer.

# OBJECTIVE:
Create CI pipeline.

# REQUIREMENTS:
- run backend tests
- build frontend

# OUTPUT:
- GitHub Actions YAML
```

---

# Prompt 13 — Demo Data

```md
# ROLE:
You are a backend engineer.

# OBJECTIVE:
Create seed data script.

# REQUIREMENTS:
- fire
- flood
- wildlife

# OUTPUT:
- seed_demo_data.py
```

---

# Prompt 14 — Debugging

```md
# ROLE:
You are a debugging expert.

# OBJECTIVE:
Fix issue in CrisisGrid AI.

# CONTEXT:
[paste error]

# OUTPUT:
- root cause
- fix
- improved code
```

---

# Prompt 15 — Enhancement

```md
# ROLE:
You are a senior engineer.

# OBJECTIVE:
Improve feature.

# CONTEXT:
[paste code]

# OUTPUT:
- improved version
- explanation
```

---

# Usage Strategy

Use prompts in this order:

```text
1. Architecture
2. Backend
3. Agents
4. Frontend
5. Testing
6. CI/CD
7. Demo polish
```

---

# Final Principle

```text
Structured prompts → Faster development → Better demo
```
