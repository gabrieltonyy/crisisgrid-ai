# CrisisGrid AI — Database Schema (Updated)

## Purpose

This document defines the database schema for CrisisGrid AI, including flexible storage strategies aligned with hackathon constraints and IBM tooling.

---

# Recommended Database Strategy (UPDATED)

## Option 1 — PostgreSQL (Primary Recommendation)

Use **PostgreSQL** as the main database.

### Why:
- Strong relational structure
- Works well with incident/report relationships
- Supports scaling later
- Compatible with ORMs (SQLAlchemy)

### PostGIS (Optional Enhancement)
If available:
- Use PostGIS for geospatial queries (radius, clustering)

If not:
- Store latitude/longitude as decimals
- Perform distance calculations in backend logic

---

## Option 2 — IBM Cloudant (NoSQL Alternative)

Use **IBM Cloudant** for faster setup within IBM Cloud ecosystem.

### Why:
- Quick to spin up (less setup than PostgreSQL)
- JSON document storage (fits report structure)
- Good for hackathon speed

### Trade-offs:
- Harder to model relationships (reports ↔ incidents)
- Geospatial queries less straightforward
- Clustering logic must be handled in application layer

---

## Option 3 — Hybrid Model (RECOMMENDED FOR IBM ALIGNMENT)

Use **PostgreSQL + IBM Cloudant together**

### Architecture:

PostgreSQL:
- Structured data
- incidents
- reports relationships
- alerts
- dispatch logs
- agent runs

Cloudant:
- raw incoming reports (JSON)
- agent payloads
- verification metadata
- audit logs
- AI interaction logs

---

### Flow Example:

```text
User submits report
→ Store raw payload in Cloudant
→ Process via agents
→ Store structured result in PostgreSQL
```

---

### Benefits:

- Combines speed + structure
- Shows strong IBM ecosystem usage
- Enables better demo narrative:
  “We use Cloudant for raw AI data and PostgreSQL for structured intelligence”

---

# Important Note for IBM Bob Usage

IBM Bob may not always have direct access to:

- Cloudant setup
- PostgreSQL provisioning
- API key generation
- External service dashboards

## What Bob Should Do

If Bob cannot access a tool directly, it should:

1. Guide you step-by-step to:
   - Create the service (Cloudant / PostgreSQL)
   - Generate credentials
   - Configure access

2. Provide:
   - Exact UI navigation steps (IBM Cloud console)
   - Required configuration values
   - Sample `.env` variables

3. Suggest alternatives:
   - Local PostgreSQL via Docker
   - SQLite fallback for MVP
   - Mock services if APIs unavailable

---

## Example Environment Variables

```text
POSTGRES_URL=postgresql://user:password@localhost:5432/crisisgrid
CLOUDANT_URL=https://your-instance.cloudant.com
CLOUDANT_API_KEY=your_api_key
CLOUDANT_DB=crisis_reports
```

---

## Final Recommendation (For You Specifically)

Since you are working solo:

### Best Approach:

Start with:
→ PostgreSQL only

Then optionally add:
→ Cloudant for demo enhancement

---

## Key Principle

Do not let infrastructure slow you down.

Your priority is:

```text
Working crisis pipeline > perfect database setup
```

---

## Everything Below (Schema Tables)

(The rest of the schema remains unchanged and continues to apply regardless of storage option.)

