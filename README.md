# AI Finance Controller — Multi-Source Reconciliation

An enterprise-grade financial reconciliation platform designed to automatically ingest, reconcile, and audit multi-source transaction datasets across:

1. **Invoice Systems** (ERP ledgers, billing exports)
2. **Bank Transactions** (Direct bank statements, feeds)
3. **Payment Gateways** (Payment processor settlements, e.g., Stripe, Razorpay)

The system processes batches of **50+ records** and computes real-time operational metrics:
- **Match Rate**
- **Verified Accuracy**
- **Throughput (records/sec)**
- **Unresolved Exceptions**

---

## Current Status: Phase 6 (Exception Detection & Classification)

This repository contains **Phase 1, Phase 2, Phase 3, Phase 4, Phase 5 & Phase 6**:
- Clean modular backend architecture with FastAPI, SQLAlchemy 2.0, SQLite, and Pydantic.
- Reproducible multi-source financial dataset generator (`backend/scripts/generate_data.py`).
- Reusable in-memory data normalization service (`backend/services/normalization.py`).
- RapidFuzz fuzzy text similarity matching engine (`backend/services/fuzzy_matching.py`).
- Smarter candidate scoring service (`backend/services/scoring.py`).
- Multi-source 3-way reconciliation engine with ambiguity guardrails (`backend/services/reconciliation.py`).
- Dedicated exception detection & classification layer (`backend/services/exceptions.py`).
- Reconciliation API endpoints (`POST /api/reconciliation/run`, `GET /api/reconciliation/results`, `GET /api/reconciliation/results/{invoice_id}`).
- Exception API endpoints (`GET /api/exceptions`, `GET /api/exceptions/{exception_id}`, `GET /api/exceptions/type/{type}`).
- Comprehensive Pytest suite with **54 unit tests** verifying health checks, dataset integrity, seed reproducibility, normalization, fuzzy matching, scoring rules, ambiguity gap detection, exception classification, and API endpoints.
- Modern React + Vite frontend dashboard shell with Tailwind CSS and React Router.

---

## Synthetic Dataset

The system generates a reproducible multi-source financial dataset (120 invoice records across 10 realistic operational reconciliation scenarios) stored in `data/`:

1. **`data/invoices.csv`**: Internal ERP billing ledger records containing invoice IDs, customer legal names, invoice numbers, amounts, dates, references, and payment statuses.
2. **`data/bank_transactions.csv`**: Direct bank feed statement entries (`CREDIT` type) with bank transaction IDs, descriptions, credit amounts, dates, and bank references.
3. **`data/gateway_transactions.csv`**: Payment gateway settlement reports from processors (**Razorpay**, **Stripe**, **PayU**) including payment IDs, gross amounts, processing fees, net settled amounts, payment dates, and gateway references.
4. **`data/ground_truth.csv`**: Baseline reconciliation mappings pairing each invoice with its expected bank transaction ID, expected gateway payment ID, expected resolution status, and specific scenario classification.

### Why Ground Truth is Included
Ground truth annotations represent the verified "gold standard" target state for the dataset. By including expected transaction mappings and scenario classifications (e.g., `exact_match`, `customer_name_variation`, `amount_mismatch`, `gateway_fee`, `duplicate_payment`, `missing_payment`, `currency_mismatch`), the project can automatically measure quantitative performance metrics in subsequent phases:
- **Match Rate**: Percentage of total invoices successfully resolved by matching algorithms.
- **Verified Accuracy**: Percentage of algorithmic matches that correctly match ground truth predictions.
- **Exception Rate**: Proportion of edge-case transactions routed to the manual/AI resolution workbench.
- **Throughput**: Records reconciled per second.

---

## Data Normalization

The backend includes a dedicated, reusable normalization service (`backend/services/normalization.py`) that standardizes raw multi-source financial records prior to multi-source 3-way matching.

### Why Normalization is Required Before Reconciliation
In real-world financial operations, multi-source records (ERP invoices, bank feeds, payment gateway settlements) exhibit syntax, formatting, and structural discrepancies:
- **Company Name Variations**: ERP ledgers store formal legal names (`ABC Private Limited`), bank feeds record abbreviated transfer strings (`ABC PVT LTD`), and gateways record truncated forms (`ABC Pvt Ltd`). Normalization strips legal suffixes (`Pvt`, `Limited`, `Inc`, `Corp`) and standardizes casing while retaining core entity distinctions (`ABC Technologies` vs `ABC Logistics`).
- **Reference Discrepancies**: Invoices contain hyphenated references (`INV-001`), bank statements omit hyphens (`inv001`), and gateway entries add spaces (`INV 001`). Reference normalization converts values to sanitized uppercase tokens (`INV001`).
- **Monetary Formatting**: Raw feeds format amounts as strings with currency symbols or commas (`₹12,500.00`, `12,500`). Amount normalization cleans string values into exact float numbers (`12500.0`).
- **Heterogeneous Date Formats**: Bank statements and payment processors export dates in varying regional formats (`01-08-2026`, `2026-08-01`, `01/08/2026`). Normalization casts valid dates into standardized ISO strings (`2026-08-01`).
- **Preservation of Raw Data**: Normalization generates separate normalized structures without mutating or overwriting original raw CSV fields, ensuring raw data remains available for auditability and manual review.

---

## Reconciliation Engine

The reconciliation engine ([`backend/services/reconciliation.py`](file:///c:/Users/yashwanthteja/Documents/razorpay/ai-finance-controller/backend/services/reconciliation.py) & [`backend/services/scoring.py`](file:///c:/Users/yashwanthteja/Documents/razorpay/ai-finance-controller/backend/services/scoring.py)) performs deterministic candidate search and 3-way matching across normalized Invoice, Bank Transaction, and Payment Gateway records.

### Candidate Search & Scoring Rules (0 to 100 points)
For every invoice, candidate bank and gateway records are scored against deterministic matching rules:

| Field | Max Score | Condition |
| :--- | :---: | :--- |
| **Amount Match** | **40 pts** | 40 pts for exact normalized monetary match (`abs(diff) < 0.001`); 0 pts otherwise. |
| **Customer Name Match** | **20 pts** | 20 pts (Exact match), 18 pts (Fuzzy 90–100), 15 pts (Fuzzy 80–89), 10 pts (Fuzzy 70–79), 0 pts (<70). |
| **Reference Match** | **20 pts** | 20 pts (Exact normalized match), 15 pts (Conservative fuzzy >= 90), 0 pts otherwise. |
| **Date Proximity** | **15 pts** | 15 pts (0 days diff), 13 pts (1 day diff), 10 pts (2 days diff), 7 pts (3 days diff), 0 pts (> 3 days). |
| **Currency Match** | **5 pts** | 5 pts for identical 3-letter ISO currency code; 0 pts otherwise. |

---

## Fuzzy Matching

Phase 5 integrates high-performance fuzzy text matching via [`RapidFuzz`](https://github.com/rapidfuzz/RapidFuzz) in [`backend/services/fuzzy_matching.py`](file:///c:/Users/yashwanthteja/Documents/razorpay/ai-finance-controller/backend/services/fuzzy_matching.py) to resolve minor spelling differences, name truncations, and bank statement description noise.

### Why Fuzzy Matching is Needed
Exact string matching fails when multi-source entities use informal abbreviations, truncated names, or extra description tokens (e.g. `ABC Technologies` vs `ABC Tech` or `NEFT CR ABC TECH PAYMENT`). Fuzzy matching measures token-level string similarity when exact normalization fails to match 100%.

### How Company-Name Similarity is Calculated
Company name similarity is computed using `RapidFuzz`'s composite weighted ratio algorithm (`fuzz.WRatio`):
* **`90 – 100` (Very Strong Similarity)**: E.g., `Ravi Enterprises` vs `RAVI ENTERPRISE` → Awarded **18 pts**.
* **`80 – 89` (Strong Similarity)**: E.g., `ABC Technologies` vs `ABC Tech` → Awarded **15 pts**.
* **`70 – 79` (Possible Similarity)**: Partial token overlap → Awarded **10 pts**.
* **`< 70` (Weak Similarity)**: E.g., `ABC Technologies` vs `ABC Logistics` → Awarded **0 pts**. Unrelated entities sharing prefixes are rejected.

### Strict Financial Controls: Why Fuzzy Matching Alone Cannot Finalize a Match
Fuzzy name similarity is a **supporting signal, not a financial guarantee**. High name similarity (18/20 pts) can NEVER override a major amount mismatch (0/40 pts) or currency mismatch (0/5 pts). If amount or currency differs, the maximum achievable total score drops below 70 pts, automatically routing the record to `EXCEPTION`.

### Ambiguous Candidate Resolution
When two top candidates (e.g., Bank 1 and Bank 2) achieve high scores with a score gap of less than 5 points (`best_candidate_score - second_best_candidate_score < 5.0`), the system automatically refrains from auto-matching. It flags the transaction for **`REVIEW`** with `matching_method = "AMBIGUOUS"` and `explanation = "Multiple possible matches identified"`.

---

## Tech Stack

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Language**: JavaScript (ESM)
- **Styling**: Tailwind CSS
- **Routing**: React Router (v7)
- **HTTP Client**: Axios
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Data Processing**: Pandas
- **Database**: SQLite
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2

### Testing
- **Backend Test Runner**: Pytest + HTTPX / Starlette TestClient

---

## Project Structure

```text
ai-finance-controller/
├── backend/
│   ├── routes/
│   │   ├── __init__.py
│   │   └── health.py          # GET /api/health endpoint
│   ├── services/
│   │   └── __init__.py        # Business logic & matching engine services
│   ├── utils/
│   │   └── __init__.py        # Helper utilities
│   ├── database.py            # SQLite & SQLAlchemy engine setup
│   ├── main.py                # FastAPI application entry point with CORS
│   ├── models.py              # SQLAlchemy database models
│   ├── requirements.txt       # Python dependencies
│   └── schemas.py             # Pydantic schemas & response contracts
├── data/
│   ├── README.md              # Data directory documentation
│   └── finance_controller.db  # SQLite database (auto-generated)
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components (Sidebar, Header, StatCard, Badge)
│   │   ├── hooks/             # Custom hooks (useApiHealth)
│   │   ├── layouts/           # Page layouts (MainLayout)
│   │   ├── pages/             # Route pages (Dashboard, Reconciliation, Exceptions, Upload, History, Settings)
│   │   ├── services/          # API client (Axios)
│   │   ├── utils/             # Formatters, constants, navigation configuration
│   │   ├── App.jsx            # React Router setup
│   │   ├── index.css          # Tailwind CSS styling
│   │   └── main.jsx           # Frontend entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── tests/
│   ├── __init__.py
│   └── test_health.py         # Pytest test suite
├── .gitignore
└── README.md
```

---

## Local Setup & Quick Start

### Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: v18 or higher (v20+ recommended)
- **npm**: v9 or higher

---

### 1. Backend Setup

From the `ai-finance-controller/` directory:

```bash
# Optional: Create and activate a Python virtual environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Start the FastAPI server
python backend/main.py
# Or directly via uvicorn:
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start at: `http://localhost:8000`
- API documentation (Swagger UI): `http://localhost:8000/docs`
- Root endpoint: `http://localhost:8000/`
- Health endpoint: `http://localhost:8000/api/health`

---

### 2. Frontend Setup

In a new terminal window, navigate to the `frontend/` directory:

```bash
# Navigate to frontend directory
cd frontend

# Install frontend dependencies
npm install

# Start the Vite development server
npm run dev
```

The frontend will run at: `http://localhost:5173`

---

### 3. Running Backend Tests

From the `ai-finance-controller/` root directory:

```bash
# Run pytest test suite
python -m pytest tests/ -v
```

---

## API Endpoints

### 1. Root Endpoint
- **Method**: `GET`
- **Path**: `/`
- **Response**:
```json
{
  "name": "AI Finance Controller",
  "status": "running"
}
```

### 2. Health Endpoint
- **Method**: `GET`
- **Path**: `/api/health`
- **Response**:
```json
{
  "status": "healthy"
}
```

---

## Exception Detection

All reconciliation records that cannot be cleanly resolved are classified by the dedicated `backend/services/exceptions.py` layer.

### Supported Exception Types

| Exception Type | Severity | Condition |
| :--- | :--- | :--- |
| `CURRENCY_MISMATCH` | CRITICAL | Invoice currency ≠ payment currency |
| `DUPLICATE_PAYMENT` | CRITICAL | Transaction ID used across multiple invoices |
| `AMBIGUOUS_MATCH` | HIGH | Multiple candidates with identical/close confidence scores |
| `AMOUNT_MISMATCH` | HIGH | Customer/reference match exists but amounts differ |
| `MISSING_BANK_PAYMENT` | HIGH | No viable bank transaction found for invoice |
| `MISSING_GATEWAY_PAYMENT` | HIGH | No viable gateway settlement found for invoice |
| `CUSTOMER_MISMATCH` | MEDIUM | Weak name alignment between invoice and payment records |
| `REFERENCE_MISMATCH` | MEDIUM | Reference IDs diverge between sources |
| `DATE_OUT_OF_RANGE` | MEDIUM | Payment date falls outside acceptable proximity tolerance |
| `POSSIBLE_GATEWAY_FEE` | MEDIUM | Gateway net_amount < invoice amount by gateway processing fee |

### Severity Matrix

```
CRITICAL → Immediate investigation required
HIGH     → Requires review before closing invoice
MEDIUM   → Flag for periodic audit, safe to defer
LOW      → Informational annotation only
```

---

## Frontend Routes

| Route | Page | Description |
| :--- | :--- | :--- |
| `/` | **Dashboard** | High-level financial controller overview, KPI placeholders, and data source status |
| `/reconciliation` | **Reconciliation** | 3-way multi-source matching engine architecture |
| `/exceptions` | **Exceptions** | Unresolved discrepancy classification and review workbench |
| `/upload` | **Data Ingestion** | Multi-source batch ingestion dropzones (50+ records) |
| `/history` | **Run History** | Historical audit trail of batch reconciliation executions |
| `/settings` | **Settings** | Matching tolerances, rule thresholds, and API connection status |

---

## Upcoming Phases

- **Phase 7: LLM/AI Exception Assistant**: AI-powered root-cause analysis for unresolved exceptions, natural-language explanations, and suggested corrective actions.
- **Phase 8: Human-in-the-Loop Review Workflow**: Manual override, exception resolution tracking, audit comment trails, and approval queues.
- **Phase 9: Performance & Analytics**: Live throughput metrics, match rate trends, exportable audit PDF reports, and interactive dashboards.
