---

# 🚨 CrisisGrid AI

### Turning everyday citizens into a real-time emergency intelligence network

CrisisGrid AI is an end-to-end crisis response platform built for the IBM Bob Dev Day hackathon. It transforms fragmented citizen observations into **verified, actionable intelligence and safety advisories within seconds**.

Inspired by real-world challenges highlighted in the hackathon narrative , the platform demonstrates how AI can bridge the gap between **citizens and emergency responders**.

---

## 🌍 Problem

When disasters strike—flooding, fires, wildlife intrusions—**citizens are the first to see danger**.

But current systems:

* Rely on **top-down reporting**
* Receive **unverified, fragmented information**
* Lack **real-time coordination**

👉 Result:

* Delayed responses
* Preventable harm
* Public panic

---

## 💡 Solution

CrisisGrid AI transforms:

> **Scattered citizen observations → Verified, actionable emergency intelligence**

### 🔑 Core Capabilities

* **📍 Citizen Reporting**

  * Submit geolocated incidents with descriptions + images

* **🧠 AI Verification**

  * Scores:

    * Confidence
    * Severity
    * Urgency
  * Adds contextual intelligence (weather, risk signals)

* **🔗 Incident Clustering**

  * Groups related reports into a single actionable incident

* **🚨 Alerts & Advisories**

  * Sends real-time safety guidance to nearby users

* **🧑‍🚒 Authority Dashboard**

  * Unified view of:

    * Incidents
    * Alerts
    * Dispatch logs

* **🗃️ Audit & Data Layer**

  * IBM Cloudant stores raw + audit data for traceability

---

## 🧠 Why This Is Different

Most systems **collect data**.

CrisisGrid AI **understands and acts on it**.

✔ Multi-agent AI pipeline
✔ Real-time verification (not passive aggregation)
✔ Intelligent clustering + prioritization
✔ Actionable decision support

---

## 👥 User Roles

| Role          | Capabilities                                      |
| ------------- | ------------------------------------------------- |
| **Citizen**   | Submit reports, track incidents, receive alerts   |
| **Authority** | Monitor incidents, view alerts, simulate dispatch |
| **Admin**     | Full system visibility for evaluation             |

---

## ⚡ How It Works

1. Citizen submits a report
2. AI verifies and scores it
3. Reports are clustered into incidents
4. Alerts are generated
5. Authorities are notified (simulated)
6. Citizens receive safety guidance

---

## 🏗️ Architecture Overview

```
Citizen / Authority UI (Next.js)
          │
       FastAPI API
          │
PostgreSQL + IBM Cloudant
          │
AI Services (verification, clustering, alerts)
          │
IBM watsonx.ai (reasoning engine)
```

---

## 🧰 Tech Stack

### Frontend

* Next.js 14
* TypeScript
* Ant Design
* React Query / Zustand

### Backend

* FastAPI
* PostgreSQL
* SQLAlchemy
* JWT Authentication

### AI & Data

* IBM watsonx.ai → AI reasoning
* IBM Cloudant → Raw + audit storage

### Deployment

* Vercel (Frontend)
* Render (Backend)

---

## 🔗 Live Demo

* 🌐 Frontend: [https://crisisgrid-ai.vercel.app](https://crisisgrid-ai.vercel.app)
* ⚙️ Backend: [https://crisisgrid-backend-dlyj.onrender.com](https://crisisgrid-backend-dlyj.onrender.com)
* 📄 API Docs: [https://crisisgrid-backend-dlyj.onrender.com/docs](https://crisisgrid-backend-dlyj.onrender.com/docs)

---

## 🔐 Demo Accounts

Password: `Password123!`

| Role      | Email                                                                             |
| --------- | --------------------------------------------------------------------------------- |
| Citizen   | [citizen.demo01@demo.crisisgrid.ai](mailto:citizen.demo01@demo.crisisgrid.ai)     |
| Authority | [authority.demo01@demo.crisisgrid.ai](mailto:authority.demo01@demo.crisisgrid.ai) |
| Admin     | [admin.demo01@demo.crisisgrid.ai](mailto:admin.demo01@demo.crisisgrid.ai)         |

---

## 🚀 Local Setup

### Backend

```bash
cd Buildproject/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
docker compose up -d postgres

python -m app.db.init_db
uvicorn app.main:app --reload
```

### Frontend

```bash
cd Buildproject/frontend
npm install
cp .env.example .env.local
npm run dev
```

---

## 🤖 IBM Integration (Hackathon Core)

CrisisGrid AI showcases practical use of:

* **IBM watsonx.ai**

  * AI reasoning for verification, clustering, decision-making

* **IBM Cloudant**

  * Persistent storage for raw reports + audit trails

* **IBM Bob**

  * Accelerated development:

    * Architecture generation
    * Backend + frontend scaffolding
    * AI agent structuring
    * Documentation and workflows

👉 Without IBM Bob, delivering this system within a hackathon timeframe would not have been feasible.

---

## 📈 Impact

CrisisGrid AI enables:

* ⚡ Faster emergency response
* 🧭 Better situational awareness
* 🛡️ Safer communities
* 🔗 Citizen–authority coordination

---

## 🔮 Roadmap

* Real authority dispatch integrations
* Advanced clustering & deduplication
* Live map risk visualization
* Cloudant-backed audit dashboards
* Production-grade security (OAuth, rate limiting)

---

## 🌍 Vision

CrisisGrid AI can evolve into:

* National disaster response systems
* Smart city safety infrastructure
* NGO coordination platforms
* Insurance risk intelligence tools

---

## 🎯 Final Thought

> In moments of crisis, seconds matter.
> CrisisGrid AI ensures those seconds turn into **life-saving action**.

---
