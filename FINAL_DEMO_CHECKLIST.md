# ✅ Final Demo Checklist & Offline Local Backup Plan

Use this verification checklist and offline local execution guide to ensure a smooth hackathon presentation.

---

## 📋 Live Demo Verification Checklist

- [x] **Frontend Running**: Web application loads at `http://localhost:5173`.
- [x] **Backend Running**: FastAPI backend runs on `http://localhost:8000`.
- [x] **Health Check Endpoint**: `GET /api/health` returns `{"status": "healthy"}`.
- [x] **Demo Synthetic Dataset**: `data/invoices.csv`, `data/bank_transactions.csv`, `data/gateway_transactions.csv`, `data/ground_truth.csv` present.
- [x] **Run Reconciliation Execution**: Clicking **Run Reconciliation** processes batch in < 100 ms.
- [x] **Executive KPI Cards**: Displays Total Records (120), Match Rate (83.3%), Verified Accuracy (98.3%), Throughput (1,500 rec/sec).
- [x] **Matched Record Detail**: `INV001` opens 3-way alignment view with 100% confidence score.
- [x] **Exception Record Detail**: `INV091` opens `AMOUNT_MISMATCH` view with discrepancy details.
- [x] **AI Assistant Diagnosis**: Clicking **Analyze with AI** on `INV091` renders root-cause summary and recommended action.
- [x] **Human Review Action**: Submitting **Approve Match** or **Mark Resolved** with note succeeds and updates status.
- [x] **Compliance Audit Trail**: `/history` route displays immutable event timeline.
- [x] **CSV Upload Pipeline**: `/upload` drag-and-drop cards validate 3 files and display 10-row preview tabs.
- [x] **No Console Errors**: Zero unhandled frontend exceptions or raw stack traces.

---

## ⚡ Offline Local Backup Plan

If cloud deployment or internet access fails during judging, run the project locally using these exact terminal commands:

### Terminal 1: Backend Startup
```bash
cd c:\Users\yashwanthteja\Documents\razorpay\ai-finance-controller\backend
# Activate virtual environment if using venv
uvicorn main:app --reload --port 8000
```
- Verify API is online: Open browser to `http://localhost:8000/api/health`.

### Terminal 2: Frontend Startup
```bash
cd c:\Users\yashwanthteja\Documents\razorpay\ai-finance-controller\frontend
npm run dev
```
- Open application: `http://localhost:5173`.

### Offline Demo Reset Command (If needed)
If you want to reset database state during judging:
```bash
python -c "import os; os.remove('data/finance_controller.db') if os.path.exists('data/finance_controller.db') else None"
```
Then click **Run Reconciliation** on the dashboard to regenerate fresh demo results instantly.
