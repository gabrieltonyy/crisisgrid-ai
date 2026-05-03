# CrisisGrid AI — A2A Protocol Contracts

## Purpose

This document defines the Agent-to-Agent (A2A) communication contracts used in CrisisGrid AI.

Even though the MVP may run agents within a single backend, designing with A2A contracts ensures:

- clean separation between agents
- future scalability
- compatibility with IBM-style multi-agent systems
- easier debugging and observability
- structured communication for IBM Bob usage

---

## Core Principle

```text
All agent communication must be structured, traceable, and schema-driven.
```

---

# 1. A2A Communication Overview

```text
Orchestrator → Agent → Agent → Decision Engine → Output
```

Instead of direct function calls, think in terms of **messages**.

Each interaction is a **task request** and **task response**.

---

# 2. A2A Message Lifecycle

```text
1. Create Task
2. Send to Target Agent
3. Agent Processes Task
4. Agent Returns Result
5. Orchestrator Decides Next Step
```

---

# 3. A2A Task Request Schema

## AgentTask

```json
{
  "task_id": "TASK-001",
  "trace_id": "TRACE-001",
  "source_agent": "orchestrator",
  "target_agent": "verification_agent",
  "intent": "VERIFY_REPORT",
  "priority": "HIGH",
  "payload": {},
  "metadata": {},
  "schema_version": "1.0",
  "timestamp": "2026-05-01T10:20:00Z"
}
```

---

## Fields

| Field | Description |
|------|------------|
| task_id | Unique task identifier |
| trace_id | Tracks full request lifecycle |
| source_agent | Who initiated the task |
| target_agent | Who should process the task |
| intent | What action is required |
| priority | LOW / MEDIUM / HIGH / CRITICAL |
| payload | Data required by the agent |
| metadata | Optional context |
| schema_version | Version control |
| timestamp | Time created |

---

# 4. A2A Task Response Schema

## AgentResult

```json
{
  "task_id": "TASK-001",
  "trace_id": "TRACE-001",
  "agent_name": "verification_agent",
  "status": "SUCCESS",
  "confidence": 0.72,
  "outputs": {},
  "errors": [],
  "next_action": "RUN_GEORISK_AGENT",
  "duration_ms": 240,
  "timestamp": "2026-05-01T10:20:02Z"
}
```

---

## Fields

| Field | Description |
|------|------------|
| task_id | Matches request |
| trace_id | Same trace ID |
| agent_name | Agent that processed task |
| status | SUCCESS / FAILED |
| confidence | Optional confidence output |
| outputs | Agent-specific results |
| errors | Error list |
| next_action | Suggested next step |
| duration_ms | Execution time |
| timestamp | Completion time |

---

# 5. Standard Intents

## Core Intents

```text
VERIFY_REPORT
CALCULATE_GEO_RISK
GET_WEATHER_CONTEXT
ANALYZE_WILDLIFE
GENERATE_ALERT
DISPATCH_AUTHORITY
GENERATE_ADVISORY
TRACK_ANALYTICS
```

---

# 6. Example Payloads

## Verification Task

```json
{
  "intent": "VERIFY_REPORT",
  "payload": {
    "description": "Smoke and flames visible",
    "image_url": "/uploads/fire.jpg",
    "latitude": -1.2921,
    "longitude": 36.8219
  }
}
```

---

## GeoRisk Task

```json
{
  "intent": "CALCULATE_GEO_RISK",
  "payload": {
    "incident_id": "INC-001",
    "latitude": -1.2921,
    "longitude": 36.8219,
    "confidence": 0.72
  }
}
```

---

## Alert Task

```json
{
  "intent": "GENERATE_ALERT",
  "payload": {
    "incident_id": "INC-001",
    "crisis_type": "FIRE",
    "confidence": 0.72,
    "severity": "HIGH"
  }
}
```

---

# 7. Traceability

## Trace ID Usage

Every report should generate a `trace_id`.

Example:

```text
TRACE-REPORT-001
```

All agent tasks must carry this ID.

This allows:

- debugging
- audit trails
- demo explainability

---

# 8. Priority Handling

| Priority | Usage |
|----------|------|
| LOW | analytics |
| MEDIUM | normal reports |
| HIGH | important reports |
| CRITICAL | fire, life-threatening |

Example:

```text
FIRE → CRITICAL
FLOOD → HIGH
WILDLIFE → HIGH
```

---

# 9. Error Handling

## Standard Error Format

```json
{
  "code": "AGENT_FAILURE",
  "message": "Verification failed",
  "details": {}
}
```

---

## Failure Response

```json
{
  "status": "FAILED",
  "errors": [
    {
      "code": "INVALID_IMAGE",
      "message": "Image could not be processed"
    }
  ]
}
```

---

# 10. Idempotency

Tasks should be safe to retry.

Example:

- verification can be re-run
- geo-risk recalculation safe
- alert generation should avoid duplication

---

# 11. Logging Requirements

Each A2A interaction must be logged:

```text
task_id
trace_id
source_agent
target_agent
intent
status
duration
```

---

# 12. MVP Simplification

For MVP:

- agents may be called as functions
- A2A contracts are conceptual
- still structure inputs/outputs as if using A2A

This ensures easy upgrade later.

---

# 13. IBM Alignment

A2A contracts align with:

- multi-agent systems
- orchestration frameworks
- IBM AI architecture patterns

---

# 14. Bob Usage

Use IBM Bob to:

- generate task schemas
- enforce structure
- simulate agent pipelines
- debug agent flow
- generate logs

---

## Bob Prompt Example

```text
Generate A2A task and response schemas for CrisisGrid AI agents.
Ensure traceability, error handling, and structured outputs.
```

---

# 15. Final Principle

```text
Every agent interaction should be:
clear, structured, traceable, and explainable.
```
