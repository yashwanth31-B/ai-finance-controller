# ⏱️ 5-Minute Timed Presentation Pitch Script

A comprehensive spoken pitch for 5-minute hackathon judging presentations.

---

## 🕒 Pitch Timing & Script

### 0:00–0:40 — The Problem
*"Finance teams at digital businesses spend hundreds of hours every month manually comparing invoice ledgers, bank statements, and payment processor logs from gateways like Razorpay or Stripe. 

This manual work is a massive bottleneck. Amounts differ due to gateway fees or tax deductions; company names vary between 'Acme Pvt Ltd' and 'Acme Private Limited'; and duplicate payments sneak through undetected. The hard challenge in fintech isn't asking a chatbot a question — it's verifying multi-source financial truth."*

### 0:40–1:20 — Why Now & Solution
*"As transaction volumes explode, manual spreadsheets simply can't scale. But blindly sending thousands of transactions to an LLM is too expensive, slow, and risky. 

That's why we built the **AI Finance Controller** — a hybrid multi-source reconciliation platform. It combines deterministic rules, RapidFuzz string matching, and an AI Exception Assistant. High-confidence pairs resolve automatically at zero LLM cost, while ambiguous discrepancies get AI root-cause analysis and human oversight."*

### 1:20–2:20 — Architecture & Workflow
*"Let's walk through the architecture:
1. **Data Normalization**: Cleans company suffixes, reference formatting, and currencies.
2. **Deterministic Matching**: Evaluates exact reference numbers, dates, and amounts.
3. **RapidFuzz Scoring**: Measures counterparty name similarity and candidate score gaps.
4. **Exception Classification**: Categorizes unresolved records into 11 exception types like AMOUNT_MISMATCH, DUPLICATE_PAYMENT, or POSSIBLE_GATEWAY_FEE.
5. **AI Exception Assistant**: Analyzes exception metadata, identifies root causes (like 2% gateway MDR fees), and suggests human review actions.
6. **Immutable Audit Trail**: Every human review decision is recorded with notes and timestamps in an SQLite compliance log."*

### 2:20–3:40 — Live Demo & Measured Results
*"Let's look at the live demo: When we run reconciliation on our 120-record synthetic benchmark:
- **Processing Time**: 0.0800 seconds (80 milliseconds)
- **Engine Throughput**: **1,500 records per second**
- **Automated Match Rate**: **83.33%** (100 records auto-resolved)
- **Verified Accuracy**: **98.33%** against our ground-truth benchmark
- **Exceptions Escalated**: Exactly 20 records flagged for review

Looking at invoice `INV001`, we see a 100% exact 3-way match. Looking at invoice `INV091`, the engine detects an AMOUNT_MISMATCH. Clicking 'Analyze with AI' diagnoses a ₹200 variance due to withholding tax. When a reviewer approves the resolution, the original system prediction remains immutably preserved while recording the human override in the audit log."*

### 3:40–4:20 — AI Safety & Verification
*"Safety is core to our design. AI is never allowed to directly post or alter financial transactions. The AI Assistant acts purely as an investigative copilot. If no AI API key is configured, the system seamlessly falls back to our deterministic heuristic financial rule engine, ensuring 100% uptime during live demos."*

### 4:20–5:00 — Future Scope & Closing
*"In the future, we plan to add direct Open Banking APIs, enterprise ERP connectors for NetSuite and SAP, and real-time multi-currency FX spot rate normalization. 

In closing: The AI Finance Controller automates high-confidence reconciliation at 1,500 records/sec, self-evaluates its own accuracy, and maintains a strict audit trail instead of pretending every record is correct. Thank you!"*
