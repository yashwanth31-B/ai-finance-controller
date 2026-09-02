# ⏱️ 3-Minute Timed Presentation Pitch Script

A concise, spoken-English pitch for 3-minute hackathon judging presentations.

---

## 🕒 Pitch Timing & Script

### 0:00–0:30 — The Problem
*"Finance teams at high-growth companies spend hundreds of manual hours every month comparing invoices, bank statements, and payment gateway reports. It's slow, expensive, and prone to costly human errors like duplicate crediting or missed gateway fees. The fundamental challenge isn't generating answers — it's verifying whether financial records across multiple sources actually match."*

### 0:30–1:00 — The Solution
*"We built the **AI Finance Controller** — an autonomous multi-source reconciliation agent. It ingests ledgers from ERPs, bank statement feeds, and gateway logs like Razorpay or Stripe. It normalizes company names and references, executes fuzzy candidate scoring, automatically resolves high-confidence matches, and escalates uncertain cases with AI root-cause analysis."*

### 1:00–2:00 — Architecture & Agent Workflow
*"Here's how the engine works: First, raw records pass through a normalization layer that standardizes company suffixes like 'Pvt Ltd' and cleans dates. Next, deterministic rules check exact references, while RapidFuzz calculates fuzzy name similarity and candidate score gaps. 

Records with scores above 85% automatically resolve as MATCHED. Uncertain records are classified into 11 exception types like AMOUNT_MISMATCH or DUPLICATE_PAYMENT. For these exceptions, our AI Assistant diagnoses the root cause — such as a gateway fee deduction or currency rounding variance — and recommends a human action. Every reviewer override is immutably logged in an audit trail."*

### 2:00–2:45 — Live Demo & Measured Results
*"Let's look at the numbers from our demo run: On a batch of 120 multi-source records, the engine processed the entire batch in just 80 milliseconds — that's **1,500 records per second**! 

It achieved an **83.3% automated match rate** and a **98.3% verified ground-truth accuracy** against our benchmark dataset, escalating exactly 20 exception cases for human review without forcing false matches."*

### 2:45–3:00 — Strong Closing Statement
*"In closing: The AI Finance Controller automates routine reconciliation at ultra-high throughput, self-evaluates its own accuracy against ground truth, and escalates exceptions for human auditability instead of pretending every record is correct. Thank you!"*
