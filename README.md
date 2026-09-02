# AI Finance Controller — Multi-Source Reconciliation

[![Status](https://img.shields.io/badge/Status-Phase%2012%20Completed-emerald.svg)](https://github.com/yashwanth31-B/ai-finance-controller)
[![Tests](https://img.shields.io/badge/Tests-86%2F86%20Passed-blue.svg)](https://github.com/yashwanth31-B/ai-finance-controller)
[![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](https://github.com/yashwanth31-B/ai-finance-controller)

An enterprise-grade, high-throughput multi-source financial reconciliation platform designed to automatically ingest, normalize, reconcile, and audit multi-source transaction datasets across:

1. **Invoice Ledgers** (ERP billing exports, invoicing systems)
2. **Bank Statement Feeds** (Direct bank settlement statements)
3. **Payment Processor Gateways** (Razorpay, Stripe payment settlement logs)

The platform processes batches of **50+ to 500+ records** per execution run, computes real-time operational metrics (**Match Rate**, **Verified Ground Truth Accuracy**, **Engine Throughput**, **Unresolved Discrepancy Exceptions**), provides **AI-Assisted Exception Diagnosis**, and maintains an **Immutable Compliance Audit Trail**.

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
                  └─────────────────────────┘
```

---

## ⏱️ 5-Minute Hackathon Demo Flow

Follow this exact sequence for a 5-minute hackathon evaluation:

1. **Launch Dashboard (`http://localhost:5173`)**:
   - Point out the **Executive KPI Cards** (Total Records, Match Rate %, Verified Accuracy %, Engine Throughput `records/sec`, Average Confidence %).
   - View the **Recharts Status Donut Chart** (`MATCHED`, `REVIEW`, `EXCEPTION`) and **Exception Category Bar Chart**.

2. **Run Demo Reconciliation**:
   - Click **Run Reconciliation** (or **Use Demo Data**).
   - Observe instant backend execution (< 100 ms) and real-time metric updates without a browser reload.

3. **Inspect a Matched Record (`INV001`)**:
   - Click **View** on invoice `INV001` in the Reconciliation table to demonstrate 3-Way Record Alignment across Invoice, Bank, and Gateway feeds with match score breakdowns.

4. **Inspect an Exception & Run AI Assistant (`INV015`)**:
   - Open invoice `INV015` (`AMOUNT_MISMATCH` exception).
   - Click **Analyze with AI**: watch the AI Assistant diagnose the root-cause variance (e.g. currency conversion/withholding tax) and suggest an audit note with confidence score.

5. **Execute Human Review & Audit Logging**:
   - Submit **Approve Match** or **Mark Resolved** with note `"Verified against bank statement"`.
   - Show how `final_status` updates to `RESOLVED_MANUALLY` while the original system prediction is **immutably preserved**.
   - Navigate to `/history` to demonstrate the new entry in the **Immutable Compliance Audit Trail**.

6. **Ingest Custom CSV Files (`/upload`)**:
   - Navigate to `/upload`, drag and drop Invoice, Bank, and Gateway CSV files.
   - Click **Validate CSV Files** to test schema checks and view 10-row preview tabs (`120 total rows — displaying first 10`).
   - Click **Run Reconciliation** and verify that custom uploads correctly calculate Match Rate and set `Verified Accuracy: N/A` (as no ground truth exists).

---

## 📌 Demo Highlight Records

Use these sample invoice IDs from the reproducible synthetic dataset for presentation:

| Scenario | Invoice ID | Customer Name | System Status | Key Highlight |
| :--- | :--- | :--- | :--- | :--- |
| **Exact Match** | `INV001` | Acme Corp | `MATCHED` | 100% 3-way exact reference & amount match |
| **Fuzzy-Name Match** | `INV008` | Beta Private Limited | `MATCHED` | RapidFuzz matches `Beta Pvt Ltd` to `Beta Private Limited` |
| **Amount Mismatch** | `INV015` | Gamma Logistics | `EXCEPTION` | Invoice amount ₹15,000 vs Bank payment ₹14,800 |
| **Duplicate Payment** | `INV022` | Delta Technologies | `EXCEPTION` | Multiple bank transactions referencing same invoice |
| **Missing Bank Payment**| `INV029` | Epsilon Enterprises | `EXCEPTION` | Invoice settled on Gateway but missing in Bank feed |
| **Ambiguous Match** | `INV036` | Zeta Solutions | `REVIEW` | Multiple close candidate scores (score gap < 10) |
| **Gateway Fee Variance**| `INV043` | Eta Global | `EXCEPTION` | Net settlement matches gross minus 2% gateway MDR fee |
| **AI Assistant Review** | `INV050` | Theta Systems | `EXCEPTION` | Trigger AI Assistant to view root cause analysis |

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

## 🛠️ Tech Stack & Requirements

- **Backend**: Python 3.14, FastAPI, Pydantic v2, SQLAlchemy 2.0, SQLite, RapidFuzz, Pytest, Uvicorn.
- **Frontend**: React 18, Vite, React Router v6, Axios, Tailwind CSS, Recharts, Lucide Icons.
- **Environment**: Node.js 18+, Python 3.10+.

---

## 💻 Installation & Running Locally

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional but recommended)
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

> [!NOTE]
> No secrets or API keys are committed to Git. `.env` and SQLite `.db` files are strictly excluded via `.gitignore`.

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
======================= 86 passed, 12 warnings in 11.95s =======================
```

---

## 🚀 Deployment Readiness

### Frontend Deployment (Vercel)
- The frontend includes `frontend/vercel.json` for single-page application routing.
- Set `VITE_API_BASE_URL` to your production backend URL in Vercel environment variables.

### Backend Deployment (Render / Railway)
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Set `ALLOWED_ORIGINS` to your production Vercel frontend URL.

---

## 📋 Final Acceptance Checklist

- [x] Backend starts cleanly on `http://localhost:8000`.
- [x] Frontend starts cleanly on `http://localhost:5173`.
- [x] Frontend production bundle builds cleanly (`npm run build`).
- [x] 100% Pytest suite passing (**86 / 86 tests passed**).
- [x] 3-Way deterministic & RapidFuzz fuzzy reconciliation working.
- [x] Reproducible synthetic dataset generation working.
- [x] Multi-source CSV upload, validation, and preview working.
- [x] Live operational metrics & ground truth verification accuracy working.
- [x] 11 Exception types and classifications working.
- [x] AI Exception Assistant working (with 100% uptime heuristic fallback).
- [x] Human Review decisions & confirmation modal working.
- [x] Immutable SQLite audit log compliance history working.
- [x] Secrets excluded via `.gitignore` and `.env.example` created.
