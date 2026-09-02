# ❓ Judge Q&A Preparation — AI Finance Controller

Concise, technically sound answers for anticipated hackathon judge questions.

---

### Q1: Why is this an AI agent and not just a chatbot?
**Answer**:
Our system is an autonomous financial agent, not a text chatbot. It independently ingests multi-source data feeds, normalizes records, scores candidates, detects exceptions, evaluates ground-truth accuracy, and runs AI root-cause analysis on uncertain records. The chatbot interface is merely an optional presentation layer; the core system executes background financial workflows autonomously.

---

### Q2: Why not send every transaction to an LLM?
**Answer**:
Sending thousands of routine financial matches to an LLM is slow, expensive, non-deterministic, and unsafe. Deterministic rules and RapidFuzz fuzzy algorithms process 1,500+ records per second at zero API cost with 100% mathematical auditability. We reserve AI specifically for ambiguous or exception cases where root-cause analysis requires contextual reasoning.

---

### Q3: How do you measure accuracy?
**Answer**:
We evaluate the engine against `data/ground_truth.csv` — an independent benchmark mapping each invoice to its known correct bank and gateway records and scenario type. The backend compares actual reconciliation output against ground truth to compute **Verified Accuracy** (`correct_results / total_records * 100`).

---

### Q4: What is the difference between Match Rate and Verified Accuracy?
**Answer**:
- **Match Rate**: Measures the percentage of records automatically resolved without manual intervention (`matched_count / total_records`).
- **Verified Accuracy**: Measures whether the automated matches are *correct* when evaluated against known ground truth benchmarks.

---

### Q5: What happens when the AI is wrong?
**Answer**:
AI recommendations are never allowed to automatically finalize financial ledger postings. All AI outputs are presented to a finance reviewer with confidence scores and audit rationale. The reviewer must explicitly approve or reject the action, and every human action is recorded in an immutable SQLite audit log.

---

### Q6: Why use fuzzy matching?
**Answer**:
Real-world bank statements and gateway logs contain string variations (e.g. `Acme Pvt Ltd` vs `Acme Private Limited` or `HDFC BANK / ACME CORP REF001`). RapidFuzz string similarity allows the engine to recognize matching counterparties without requiring rigid 100% string matches.

---

### Q7: What happens with duplicate transactions?
**Answer**:
When multiple bank or gateway payments match the same invoice reference, the engine suppresses automatic matching, classifies the record as a `DUPLICATE_PAYMENT` exception, and alerts the reviewer to prevent double crediting or duplicate refund processing.

---

### Q8: What happens without an AI API key?
**Answer**:
The platform includes an intelligent heuristic financial rule engine fallback. If `AI_API_KEY` is not provided or network access is offline, the system seamlessly uses financial domain rules to generate root-cause analyses, ensuring 100% uptime during live demos.

---

### Q9: Can this use real company data?
**Answer**:
Yes. While the demo uses a synthetic dataset for benchmarking, the CSV Ingestion Pipeline (`/upload`) accepts real billing ledger CSVs, bank statement feeds, and Razorpay/Stripe settlement logs, validating schemas and executing 3-way matching dynamically.

---

### Q10: Is this production-ready?
**Answer**:
This is an enterprise-grade hackathon prototype demonstrating core matching architecture, AI diagnosis, and audit logging. Production deployment would require live banking API integrations (e.g. Plaid/Yodlee), enterprise SSO/RBAC, and GL accounting ledger connectors.
