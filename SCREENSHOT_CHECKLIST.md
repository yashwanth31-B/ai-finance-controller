# 📸 UI Screenshot Checklist for Presentation Deck

Capture these 9 screenshots from the live web application (`http://localhost:5173`) to include in your presentation deck or submission repository.

---

## 📸 Screenshot Capture List

| # | Target UI View | Route / Component | Key Elements to Capture |
| :--- | :--- | :--- | :--- |
| **1** | **Executive Dashboard** | `/` | Top KPI Cards (Match Rate 83.3%, Accuracy 98.3%, Throughput 1,500 rec/sec), Recharts Donut Chart & Exception Bar Chart |
| **2** | **Reconciliation Workbench Table** | `/reconciliation` | Filter tabs (`ALL`, `MATCHED`, `REVIEW`, `EXCEPTION`), confidence badges, search bar with `INV001` |
| **3** | **Matched Record Detail Modal** | `/reconciliation` ➔ View `INV001` | Side-by-side 3-Way Record Breakdown (Invoice vs Bank vs Gateway), matched field badges, 100% confidence score |
| **4** | **Exception Record Detail Modal** | `/exceptions` ➔ View `INV091` | `AMOUNT_MISMATCH` header, severity badge, root cause analysis, discrepancy amounts |
| **5** | **AI Exception Assistant Diagnosis** | `/exceptions` ➔ View `INV091` ➔ **Analyze with AI** | AI Diagnosis card, AI Confidence score (92.5%), Recommended Action (`MARK_RESOLVED`), suggested audit note |
| **6** | **Human Review Workbench Panel** | Detail Modal for `INV091` | Reviewer Name input (`Finance Reviewer`), Action selector, Review Note textarea, Confirmation dialog |
| **7** | **Immutable Compliance Audit Log** | `/history` | Audit event table, event badges, actor, state transition (`REVIEW` ➔ `RESOLVED_MANUALLY`), timestamps |
| **8** | **Multi-Source CSV Ingestion Page** | `/upload` | 3 Drag-and-drop CSV upload cards (Invoices, Bank, Gateway), validation success badges, **Run Reconciliation** button |
| **9** | **10-Row Data Preview Tabs** | `/upload` ➔ Preview | Preview tabs for Invoices, Bank, and Gateway feeds showing sample row alignment (`120 total rows — displaying first 10`) |
