# ⏱️ AI Finance Controller — 5-Minute Hackathon Demo Script

This script guides a 5-minute presentation for hackathon judges, demonstrating the core value proposition, live 3-way reconciliation, AI exception analysis, and human audit trail.

---

## 🕒 Timeline Breakdown

| Time | Stage | Action / Visual | Spoken Script |
| :--- | :--- | :--- | :--- |
| **0:00–0:30** | **1. The Problem** | Open Dashboard (`http://localhost:5173`) | *"Finance teams spend hundreds of hours every month manually cross-referencing billing invoices, bank statements, and payment gateway reports. This manual work is slow, expensive, and prone to costly human errors. The challenge isn't just matching numbers — it's verifying whether financial transactions actually reconcile."* |
| **0:30–1:00** | **2. The Solution** | Highlight Header & Cards | *"Our AI Finance Controller automates multi-source 3-way reconciliation. It normalizes company names, dates, and references, executes fuzzy candidate scoring, classifies records into MATCHED, REVIEW, or EXCEPTION, and self-evaluates match rate, ground-truth accuracy, and throughput."* |
| **1:00–2:00** | **3. Live Execution** | Click **Run Reconciliation** (or **Use Demo Data**) | *"Let's run reconciliation on 120 multi-source records. In under 100 milliseconds, the engine reconciles 3 sources, achieving an 83.3% automated match rate, 98.3% verified ground truth accuracy, and over 1,500 records per second throughput!"* |
| **2:00–2:45** | **4. Successful Match** | Click **View** on Invoice `INV001` | *"Here is an exact 3-way match for invoice INV001 (Acme Corp). The system presents side-by-side evidence across Invoice, Bank, and Gateway feeds, showing a 100% confidence score and green matched field badges."* |
| **2:45–3:30** | **5. Show Exception** | Open Invoice `INV091` (`AMOUNT_MISMATCH`) | *"Instead of forcing uncertain matches, our engine suppresses low-confidence predictions. Here on invoice INV091, the system flags an AMOUNT_MISMATCH exception: Invoice amount ₹15,000 vs Bank payment ₹14,800."* |
| **3:30–4:15** | **6. AI Assistant** | Click **Analyze with AI** on `INV091` | *"For unresolved exceptions, our AI Assistant analyzes discrepancy metadata to diagnose root cause. Here, the AI identifies a ₹200 variance (likely currency rounding or tax deduction), recommends a resolution, and suggests an audit note with 92.5% confidence."* |
| **4:15–4:45** | **7. Human Review** | Submit **Approve Match** or **Mark Resolved** | *"Financial transactions cannot be finalized by AI alone. A finance reviewer inspects the recommendation, enters a note, and confirms. Looking at the Audit History (`/history`), the original system decision is immutably preserved while recording the human override."* |
| **4:45–5:00** | **8. Final Closing** | Show Dashboard KPIs & Audit Log | *"In summary: the AI Finance Controller automates high-confidence reconciliation, measures its own accuracy, and escalates exceptions for auditability rather than pretending every record is correct."* |

---

## 💡 Pro Tips for Presenters

1. **Keep the Pace**: Spend no more than 45 seconds per section.
2. **Emphasize Accuracy vs. Match Rate**: Highlight that match rate measures automation volume, while verified accuracy measures engine correctness against ground truth.
3. **Demonstrate Fallback Uptime**: Mention that the AI Assistant runs on LLM APIs or an intelligent heuristic rule engine, ensuring 100% demo uptime.
