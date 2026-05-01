# CrisisGrid AI — ADK Orchestration

## Purpose

This document defines how agent orchestration is handled in CrisisGrid AI using an ADK-style (Agent Development Kit) approach.

Even if the MVP does not fully use IBM ADK tooling, this structure ensures:

- scalable multi-agent coordination
- clear execution flow
- alignment with IBM architecture expectations
- easy future migration to real orchestration frameworks

---

## Core Principle

```text
The orchestrator controls the flow.
Agents do NOT control each other.
```

---

# 1. What is Orchestration?

Orchestration is the process of:

- deciding which agent runs
- deciding when it runs
- passing data between agents
- combining results
- making final decisions

---

# 2. Orchestration Flow

```text
User submits report
    ↓
Orchestrator creates trace_id
    ↓
Verification Agent
    ↓
GeoRisk Agent
    ↓
Context Agents (Weather / Wildlife)
    ↓
Decision Engine
    ↓
Alert Agent
    ↓
Dispatch Agent
    ↓
Advisory Agent
    ↓
Final Response
```

---

# 3. Orchestrator Responsibilities

The orchestrator must:

- validate input
- assign trace_id
- create agent tasks
- execute agents in order
- handle failures
- log agent runs
- combine outputs
- return final response

---

# 4. Example Orchestrator Flow (Pseudo Code)

```python
def process_report(report):
    trace_id = generate_trace_id()

    verification = verification_agent.run(report)

    georisk = georisk_agent.run({
        "location": report.location,
        "confidence": verification.confidence
    })

    context = {}
    if report.crisis_type == "FLOOD":
        context = weather_agent.run(report)

    decision = decision_engine.evaluate(
        verification,
        georisk,
        context
    )

    alert = None
    if decision.should_alert:
        alert = alert_agent.run(decision)

    dispatch = None
    if decision.should_dispatch:
        dispatch = dispatch_agent.run(decision)

    advice = advisory_agent.run(decision)

    return {
        "incident": decision,
        "alert": alert,
        "dispatch": dispatch,
        "advice": advice
    }
```

---

# 5. Orchestration Rules

## Rule 1: Sequential Execution

Agents run in a defined order.

## Rule 2: Conditional Execution

Not all agents run every time.

Example:

- weather agent only runs for floods
- wildlife agent only runs for wildlife reports

## Rule 3: Fail Gracefully

If an agent fails:

- continue pipeline if possible
- log error
- reduce confidence if needed

## Rule 4: No Circular Calls

Agents must not call each other directly.

---

# 6. State Management

For MVP, state is:

- stored in database
- passed via function arguments

For future:

- use distributed state manager (Redis / ADK state)

---

# 7. Traceability

Each orchestration run must track:

```text
trace_id
report_id
incident_id
agent sequence
execution times
decisions made
```

---

# 8. Decision Engine Integration

The orchestrator sends agent outputs to the decision engine.

Decision engine returns:

```text
final confidence
incident status
should_alert
should_dispatch
severity
```

---

# 9. Orchestration Modes

## Mode 1: Local Mode (MVP)

- direct function calls
- simple Python flow
- fastest implementation

## Mode 2: ADK Mode (Future)

- structured agent tasks
- async execution
- queue-based processing
- distributed agents

---

# 10. Failure Handling

## Example

```text
Weather API fails
→ Skip weather boost
→ Continue pipeline
```

```text
Verification fails
→ Mark report as NEEDS_CONFIRMATION
→ Do not alert
```

---

# 11. Logging

Log every step:

```text
agent_name
input_summary
output_summary
status
duration
trace_id
```

---

# 12. IBM Alignment

This orchestration model aligns with:

- IBM multi-agent design
- ADK-style workflows
- enterprise orchestration patterns

---

# 13. Bob Usage

Use IBM Bob to:

- generate orchestrator code
- simulate agent flows
- debug orchestration logic
- optimize execution sequence

---

## Bob Prompt Example

```text
Create a Python orchestrator for CrisisGrid AI that:
1. processes a report
2. runs verification, georisk, and alert agents
3. applies decision thresholds
4. returns structured response
Follow modular architecture.
```

---

# 14. Final Principle

```text
Orchestration is the brain.
Agents are the tools.
```

Keep orchestration simple, clear, and deterministic for MVP.
