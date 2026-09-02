# 📌 Authentic Demo Highlight Records Directory

This document lists authentic sample record IDs from the reproducible synthetic dataset (`seed = 42`) for live presentation and testing.

---

## 🎯 Demo Record Reference Table

| Category / Scenario | Invoice ID | Customer Name | Expected Status | Key Highlight to Present |
| :--- | :--- | :--- | :--- | :--- |
| **Exact 3-Way Match** | `INV001` | Acme Corp | `MATCHED` | 100% exact reference, date, and amount alignment across 3 feeds |
| **Normalized Name Match** | `INV066` | Acme Pvt Ltd | `MATCHED` | Normalizes `Acme Pvt Ltd` vs `Acme Private Limited` to produce clean match |
| **Fuzzy Match / Date Shift**| `INV081` | Beta LLC | `MATCHED` | RapidFuzz string similarity handles minor name & 1-day date variations |
| **Amount Mismatch** | `INV091` | Gamma Logistics | `EXCEPTION` | Invoice amount ₹15,000 vs Bank payment ₹14,800 (₹200 variance) |
| **Duplicate Payment** | `INV099` | Delta Technologies | `EXCEPTION` | Multiple bank transactions referencing the same invoice ID |
| **Missing Bank Payment** | `INV104` | Epsilon Enterprises | `EXCEPTION` | Invoice settled on Gateway but missing in Bank feed |
| **Gateway Fee Variance** | `INV109` | Eta Global | `EXCEPTION` | Net settlement matches gross minus 2% payment gateway MDR fee |
| **Ambiguous Match** | `INV113` | Zeta Solutions | `REVIEW` | Multiple close candidate scores (candidate score gap < 10) |
| **AI Assistant Candidate** | `INV091` | Gamma Logistics | `EXCEPTION` | Trigger AI Assistant to view root cause analysis & recommended action |

---

## 🔍 How to Find These Records in the UI

1. Open **Reconciliation Workbench** (`http://localhost:5173/reconciliation`).
2. Type any of the Invoice IDs above (e.g. `INV001`, `INV091`, `INV109`) into the search bar.
3. Click **View** to inspect the 3-Way Record Comparison, Match Scores, and Human Review Workbench.
