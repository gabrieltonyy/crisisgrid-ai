# 🚀 CrisisGrid AI — Quick Start Prompts (Orchestrator Context)

## 📌 Purpose

This document defines the **Quick Start Prompts** used in the CrisisGrid Orchestrator (watsonx Orchestrate).

These prompts:
- Guide users and agents on how to interact with the system
- Trigger specific **agent pipelines**
- Serve as **entry points** into the orchestration workflow
- Provide **context for Codex / AI agents** during implementation

---

## 🧠 Why Quick Start Prompts Matter

In a multi-agent orchestration system:

- Prompts act as **intent signals**
- They determine **which agents are triggered**
- They help enforce **consistent workflows**
- They improve **user experience and demo clarity**

👉 Think of them as:
> “Predefined commands that map to orchestration pipelines”

---

## ⚙️ Prompt → Pipeline Mapping Concept

| Prompt Type | Pipeline Triggered |
|------------|------------------|
| Report Processing | Full pipeline |
| Deduplication | Deduplication agent |
| Verification | Verification agent |
| Alert Generation | Alert agent |
| Analysis | Aggregation + reporting |

---

## 🧩 Quick Start Prompts

### 1. Full Crisis Processing Pipeline
```text
Run the full crisis processing pipeline from intake to alert generation for this report.