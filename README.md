# AI Finance Controller — Multi-Source Reconciliation

[![Status](https://img.shields.io/badge/Status-Phase%2013%20Completed-emerald.svg)](https://github.com/yashwanth31-B/ai-finance-controller)
[![Tests](https://img.shields.io/badge/Tests-86%2F86%20Passed-blue.svg)](https://github.com/yashwanth31-B/ai-finance-controller)
[![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](https://github.com/yashwanth31-B/ai-finance-controller)

An enterprise-grade, high-throughput multi-source financial reconciliation platform designed to automatically ingest, normalize, reconcile, and audit multi-source transaction datasets across:

1. **Invoice Ledgers** (ERP billing exports, invoicing systems)
2. **Bank Statement Feeds** (Direct bank settlement statements)
3. **Payment Processor Gateways** (Razorpay, Stripe payment settlement logs)

The platform processes batches of **50+ to 500+ records** per execution run, computes real-time operational metrics (**Match Rate**, **Verified Ground Truth Accuracy**, **Engine Throughput**, **Unresolved Discrepancy Exceptions**), provides **AI-Assisted Exception Diagnosis**, and maintains an **Immutable Compliance Audit Trail**.

---

## 📢 Problem Statement Pitches

- **10-Second Pitch**:
  *"Finance teams spend hundreds of manual hours cross-referencing invoices, bank statements, and gateway logs. Our AI Finance Controller automates this 3-way reconciliation loop while verifying accuracy and logging an audit trail."*

- **30-Second Pitch**:
  *"Multi-source financial reconciliation is slow, expensive, and error-prone. Instead of forcing uncertain matches or sending every transaction to expensive LLMs, our AI Finance Controller uses deterministic rules and RapidFuzz matching to automatically resolve 80%+ of records at 1,500+ records/sec. Uncertain exceptions are diagnosed by an AI Assistant and escalated to a human reviewer with an immutable audit log."*

- **1-Minute Pitch**:
  *"High-growth fintechs process millions in transactions across billing ledgers, bank feeds, and payment gateways like Razorpay or Stripe. Manually resolving fee variances, missing settlements, and name formatting differences creates massive audit backlog. Our AI Finance Controller solves this with a 3-way matching engine that normalizes data, scores candidate candidates, and self-evaluates accuracy against ground truth benchmarks. Obvious matches are resolved instantly; ambiguous cases are analyzed by an AI Exception Assistant that suggests root-cause fixes. Human reviewers can approve or override decisions, with every action immutably logged in SQLite for audit compliance."*

---

## 🏛️ System Architecture

```text
Invoice CSV                 Bank CSV                 Gateway CSV
    │                          │                          │
    └──────────────────────────┼──────────────────────────┘
                               │
                               v
                  ┌─────────────────────────┐
                  │   Data Normalization    │
                  │   (Suffixes/Names/Dates)│
                  └────────────┬────────────┘
                               │
                               v
                  ┌─────────────────────────┐
                  │ Deterministic Matching  │
                  │ (Exact References/Amts) │
                  └────────────┬────────────┘
                               │
                               v
                  ┌─────────────────────────┐
                  │ RapidFuzz Fuzzy Engine  │
                  │ (Similarity & Score Gap)│
                  └────────────┬────────────┘
                               │
                               v
                  ┌─────────────────────────┐
                  │ Exception Classifier    │
                  │ (11 Exception Categories)│
                  └────────────┬────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            │                                     │
            v                                     v
   High Confidence Match                     Uncertain Record
 (MATCHED: Score >= 85%)               (REVIEW / EXCEPTION)
            │                                     │
            │                                     v
            │                        ┌─────────────────────────┐
            │                        │  AI Exception Assistant │
            │                        │  (Root Cause Diagnosis) │
            │                        └────────────┬────────────┘
            │                                     │
            └──────────────────┬──────────────────┘
                               │
                               v
                  ┌─────────────────────────┐
                  │ Human Review Workbench  │
                  │ (Approve / Reject / Res)│
                  └────────────┬────────────┘
                               │
                               v
                  ┌─────────────────────────┐
                  │ Immutable Audit Trail   │
                  │ (SQLite Database Log)   │
                  └────────────┬────────────┘
                               │
                               v
                  MATCHED / REVIEW / EXCEPTION
```

### 🗣️ Spoken Architecture Summary (30 Seconds)
*"Raw multi-source CSV files are normalized to eliminate company name variations and reference formatting differences. The deterministic engine evaluates exact matches, while RapidFuzz calculates fuzzy text similarity and score gaps. High-confidence pairs auto-resolve as MATCHED, while uncertain records are classified into 11 exception types. An AI Assistant analyzes root causes for exceptions, recommending actions to human reviewers who make final decisions recorded in an immutable SQLite audit trail."*

---

## ✨ System Feature Matrix

| Domain | Feature Capability | Implementation Detail |
| :--- | :--- | :--- |
| **Core Matching** | Multi-Source 3-Way Reconciliation | Normalizes & connects Invoices, Bank Feeds, and Payment Gateways |
| | Data Normalization | Cleans suffixes (`Pvt Ltd` -> `Private Limited`), references, and currencies |
| | RapidFuzz Similarity | Fuzzy matching for counterparty names and bank transaction descriptions |
| | Candidate Scoring | Evaluates bank scores, gateway scores, and candidate score gap thresholds |
| **Verification** | Ground Truth Benchmarking | Evaluates actual matching predictions against `ground_truth.csv` |
| | Match Rate & Verified Accuracy | Computes automated resolution ratio vs ground-truth correctness % |
| | Engine Throughput | Measures real-time execution throughput in `records/sec` |
| **Exception Engine**| Discrepancy Classification | Categorizes unresolved cases into 11 specific exception types |
| | Severity & Suggested Actions | Assigns severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) and remediation steps |
| **AI Assistant** | AI-Assisted Diagnosis | Diagnoses root causes (e.g. MDR fees, rounding variances, duplicate payments) |
| | Uptime Fallback Guarantee | Seamlessly switches to heuristic financial rule engine if API key is absent |
| **Human Oversight** | Reviewer Workbench | Supports `APPROVE_MATCH`, `REJECT_MATCH`, `MARK_RESOLVED`, `KEEP_UNDER_REVIEW` |
| | Confirmation Modals | Interactive dialogs prevent accidental overrides |
| | Immutable Audit History | SQLite persistence of all review actions, reviewer names, notes, and timestamps |
| **Product Experience**| Live Executive Dashboard | Live KPI cards, Recharts status donut chart, exception bar chart |
| | Multi-Source CSV Ingestion | Drag-and-drop 3-card upload with 10-row preview tabs (`/upload`) |
| | Search, Filters & Pagination | Interactive filtering by status, confidence range, severity, and invoice search |

---

## ⏱️ Presentation & Hackathon Guides

- 📘 [**5-Minute Demo Script**](file:///c:/Users/yashwanthteja/Documents/razorpay/ai-finance-controller/DEMO_SCRIPT.md) — Timed presentation script for hackathon judges.
- 📌 [**Demo Highlight Records Directory**](file:///c:/Users/yashwanthteja/Documents/razorpay/ai-finance-controller/DEMO_RECORDS.md) — Authentic sample IDs (`INV001`, `INV066`, `INV081`, `INV091`, `INV099`, `INV104`, `INV109`, `INV113`).
- ❓ [**Judge Q&A Guide**](file:///c:/Users/yashwanthteja/Documents/razorpay/ai-finance-controller/JUDGE_QA.md) — Concise answers for the 10 likely judge technical questions.

---

## ⚡ Performance & Throughput Benchmarks

Measured performance benchmarks across varying dataset sizes (measured via `python backend/scripts/benchmark.py`):

| Batch Size | Processing Time | Throughput | Match Rate | Status |
| :---: | :---: | :---: | :---: | :---: |
| **50 Records** | `0.0900 sec` (`90 ms`) | **555.85 records/sec** | `100.00%` | ✅ Instant |
| **100 Records** | `0.3294 sec` (`329 ms`) | **303.62 records/sec** | `100.00%` | ✅ High-Speed |
| **500 Records** | `10.7646 sec` (`10.7 s`) | **46.45 records/sec** | `100.00%` | ✅ Batch Scalable |
| **Synthetic Demo Dataset (120 Records + Complex Scenarios)** | `0.0800 sec` (`80 ms`) | **1,500 records/sec** | `83.33%` | ✅ Ground Truth 98.33% |

---

## 💻 Installation & Running Locally

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI dev server
uvicorn main:app --reload --port 8000
```
- **Backend API Base URL**: `http://localhost:8000`
- **Swagger Interactive API Docs**: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
- **Web Application URL**: `http://localhost:5173`

---

## 🔑 Environment Configuration

Copy `.env.example` to create your local environment variables:

```bash
cp .env.example .env
```

```ini
# AI Provider Configuration (Optional — Fallbacks to Heuristic AI Engine if blank)
AI_PROVIDER=google
AI_API_KEY=your_gemini_or_openai_api_key_here
AI_MODEL=gemini-1.5-flash

# Backend Configuration
PORT=8000
HOST=0.0.0.0
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Service identity and health status |
| `GET` | `/api/health` | Service health status check |
| `GET` | `/api/metrics` | System operational KPIs & ground truth accuracy |
| `POST` | `/api/reconciliation/run` | Execute 3-way reconciliation on synthetic demo dataset |
| `POST` | `/api/upload/validate` | Validate 3 uploaded CSV files with schema & security checks |
| `POST` | `/api/reconciliation/run-uploaded` | Execute 3-way reconciliation on uploaded CSV batch session |
| `GET` | `/api/reconciliation/results` | Fetch all reconciliation results from latest batch |
| `GET` | `/api/reconciliation/results/{invoice_id}` | Fetch single 3-way record breakdown |
| `GET` | `/api/exceptions` | List unresolved discrepancy exceptions |
| `POST` | `/api/reviews` | Submit human review decision (`APPROVE_MATCH`, `REJECT_MATCH`, etc.) |
| `GET` | `/api/reviews` | Query human review history logs |
| `GET` | `/api/audit-trail` | Query immutable audit log compliance events |
| `POST` | `/api/ai/analyze-exception` | Trigger AI-assisted root-cause analysis for an exception |

---

## 🧪 Automated Testing

Execute the complete backend test suite:

```bash
python -m pytest tests/ -v
```

```text
====================== 86 passed, 12 warnings in 11.95s =======================
```

---

## ⚠️ Known Limitations

1. **Synthetic Dataset Baseline**: Ground truth verification metrics rely on `data/ground_truth.csv`. Custom uploaded CSVs without ground truth report `Verified Accuracy: N/A`.
2. **No Direct Banking API Connectors**: The hackathon prototype ingests bank CSV statements rather than live Open Banking / Plaid OAuth API connections.
3. **No Enterprise RBAC / Authentication**: Human review actions accept a reviewer name string without full OAuth/SAML authentication.
4. **Not Certified Accounting Software**: Designed as an intelligent reconciliation automation and audit assistant, not a certified accounting GL system.

---

## 🚀 Future Scope & Roadmap

- **Live Banking & Settlement APIs**: Integration with Plaid, Yodlee, Razorpay Settlement Webhooks, and Stripe Payout APIs.
- **GL Accounting System Connectors**: Direct sync with QuickBooks, Xero, NetSuite, and SAP.
- **Multi-Currency FX Normalization**: Real-time spot rate foreign exchange gain/loss calculation.
- **Enterprise SSO & Role-Based Access Control**: Granular reviewer permission levels and approval limits.
- **Proactive Anomaly Detection**: Unsupervised ML models for detecting fraudulent billing patterns.

---

## 📋 Final Acceptance Checklist

- [x] Backend starts cleanly on `http://localhost:8000`.
- [x] Frontend starts cleanly on `http://localhost:5173`.
- [x] Frontend production bundle builds cleanly (`npm run build`).
- [x] 100% Pytest suite passing (**86 / 86 tests passed**).
- [x] 3-Way deterministic & RapidFuzz fuzzy reconciliation working.
- [x] Reproducible synthetic dataset generation working (`seed = 42`).
- [x] Multi-source CSV upload, validation, and preview working.
- [x] Live operational metrics & ground truth verification accuracy working.
- [x] 11 Exception types and classifications working.
- [x] AI Exception Assistant working (with 100% uptime heuristic fallback).
- [x] Human Review decisions & confirmation modal working.
- [x] Immutable SQLite audit log compliance history working.
- [x] Presentation materials ([`DEMO_SCRIPT.md`](file:///c:/Users/yashwanthteja/Documents/razorpay/ai-finance-controller/DEMO_SCRIPT.md), [`DEMO_RECORDS.md`](file:///c:/Users/yashwanthteja/Documents/razorpay/ai-finance-controller/DEMO_RECORDS.md), [`JUDGE_QA.md`](file:///c:/Users/yashwanthteja/Documents/razorpay/ai-finance-controller/JUDGE_QA.md)) finalized.
