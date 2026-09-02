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

## Current Status: Phase 1 (Project Foundation)

This repository contains **Phase 1: Project Foundation**:
- Clean modular backend architecture with FastAPI, SQLAlchemy 2.0, SQLite, and Pydantic.
- Health check endpoints (`/` and `/api/health`) with CORS configured for the React frontend.
- Pytest test suite verifying backend operational status and headers.
- Modern React + Vite frontend with Tailwind CSS, React Router, Axios client, and a finance dashboard layout.
- All placeholder pages and routes (`/`, `/reconciliation`, `/exceptions`, `/upload`, `/history`, `/settings`).

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

- **Phase 2: Ingestion & Parsing Engine**: Multi-source file ingestion (CSV/JSON/MT940) for 50+ records with Pandas and SQLite indexing.
- **Phase 3: 3-Way Reconciliation Core**: Deterministic rule matching, tolerance computation, and exception classification.
- **Phase 4: AI Exception Assistant**: AI-powered fuzzy discrepancy matching and root-cause analysis.
- **Phase 5: Performance & Analytics**: Live throughput metrics, match rates, and exportable audit reports.
