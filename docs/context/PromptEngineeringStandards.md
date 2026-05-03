# CrisisGrid AI — Prompt Engineering Standards

## Purpose

This document defines how prompts should be written and used in CrisisGrid AI when working with AI coding assistants (IBM Bob, GPT, etc.).

The goal is to ensure:

- consistent outputs
- clean architecture
- reduced technical debt
- faster development
- better alignment with system design

---

## Core Principle

```text
A good prompt produces structured, usable, and predictable output.
```

---

# 1. Prompt Structure Standard

Every prompt should include:

```text
ROLE
OBJECTIVE
CONTEXT
REQUIREMENTS
OUTPUT FORMAT
```

---

## Example Structure

```md
# ROLE:
You are a senior backend engineer.

# OBJECTIVE:
Build the verification agent.

# CONTEXT:
CrisisGrid AI multi-agent system.

# REQUIREMENTS:
- FastAPI
- Pydantic
- async

# OUTPUT:
- folder structure
- code files
```

---

# 2. Always Provide Context

Bad:

```text
Create a backend service
```

Good:

```text
Create a FastAPI backend service for CrisisGrid AI report submission aligned with the system architecture.
```

---

# 3. Be Explicit

Bad:

```text
Handle reports
```

Good:

```text
Implement POST /reports endpoint that:
- accepts crisis_type, description, location
- calls verification agent
- returns confidence score
```

---

# 4. Use Constraints

Example:

```text
- do not use external APIs
- keep logic simple for MVP
- follow existing schema
```

---

# 5. Define Output Expectations

Always tell the AI what to return.

Example:

```text
Return:
- Python files
- folder structure
- API endpoints
- explanation
```

---

# 6. Reuse Context

Each new prompt should include:

- previous outputs
- schemas
- architecture decisions

This keeps consistency.

---

# 7. Avoid Overly Broad Prompts

Bad:

```text
Build entire system
```

Good:

```text
Build verification agent only
```

---

# 8. Prompt Sequencing

Follow order:

```text
architecture → backend → agents → frontend → testing → deployment
```

---

# 9. Naming Consistency

Ensure prompts use same names:

```text
Verification Agent
GeoRisk Agent
Dispatch Agent
```

Avoid renaming agents in prompts.

---

# 10. Schema Consistency

Always reference existing schemas:

```text
CrisisReport
VerificationResult
Incident
```

---

# 11. Iterative Refinement

If output is not good:

- refine prompt
- add constraints
- clarify requirements

---

# 12. Error Handling in Prompts

Ask AI to include:

- validation
- error responses
- edge cases

---

# 13. IBM Bob Best Practices

When using IBM Bob:

- keep prompts short but structured
- provide file paths
- request modular code
- avoid secrets
- ask for explanations

---

# 14. Example Bob Prompt

```text
Create a FastAPI verification agent for CrisisGrid AI.

Requirements:
- analyze description
- return confidence score
- use Pydantic models

Output:
- verification_agent.py
- schemas.py
```

---

# 15. Do Not Do

- do not paste API keys
- do not ask for production secrets
- do not generate overly complex code early

---

# 16. Version Prompts

Keep prompt versions:

```text
prompt_v1
prompt_v2
prompt_final
```

---

# 17. Store Prompts

Store in:

```text
docs/prompt-engineering/
```

---

# 18. Testing Prompts

After using a prompt:

- test generated code
- validate against architecture
- refine if needed

---

# 19. Final Principle

```text
Clear prompts → Clean code → Better demo.
```
