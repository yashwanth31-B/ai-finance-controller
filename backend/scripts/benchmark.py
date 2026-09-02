"""
Reconciliation Performance & Throughput Benchmark
===================================================
Measures processing time, throughput (records/sec), match rate, and verified accuracy
across batch sizes of 50, 100, and 500 synthetic records.
"""

import os
import sys
import time

# Ensure backend directory is in sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from services.reconciliation import run_reconciliation_batch


def generate_benchmark_records(count: int):
    """Generates synthetic in-memory records for performance testing."""
    invoices = []
    bank_txns = []
    gateway_txns = []

    for i in range(1, count + 1):
        inv_id = f"INV_PERF_{i:04d}"
        cust = f"Benchmark Corp {i}"
        ref = f"REF_PERF_{i:04d}"
        amt = 1000.0 + (i * 10.0)

        invoices.append({
            "invoice_id": inv_id,
            "customer_id": f"CUST_{i}",
            "customer_name": cust,
            "invoice_number": f"INV-{i}",
            "amount": str(amt),
            "currency": "INR",
            "invoice_date": "2026-08-01",
            "due_date": "2026-08-15",
            "reference": ref,
            "status": "UNPAID"
        })

        bank_txns.append({
            "transaction_id": f"BANK_PERF_{i:04d}",
            "transaction_date": "2026-08-01",
            "value_date": "2026-08-01",
            "description": f"{cust} {ref}",
            "amount": str(amt),
            "currency": "INR",
            "reference": ref,
            "account_number": "1234567890",
            "bank_name": "HDFC Bank"
        })

        gateway_txns.append({
            "payment_id": f"PAY_PERF_{i:04d}",
            "customer_name": cust,
            "customer_email": f"user{i}@benchmark.com",
            "amount": str(amt),
            "currency": "INR",
            "payment_date": "2026-08-01",
            "reference": ref,
            "gateway": "Razorpay",
            "payment_method": "UPI",
            "fee": "20.0",
            "tax": "3.6",
            "net_amount": str(amt - 23.6),
            "payment_status": "SUCCESS"
        })

    return invoices, bank_txns, gateway_txns


def run_benchmark():
    """Runs benchmarks across 50, 100, and 500 records."""
    print("=" * 65)
    print("  AI FINANCE CONTROLLER — PERFORMANCE BENCHMARK SUITE")
    print("=" * 65)

    batch_sizes = [50, 100, 500]

    for size in batch_sizes:
        invs, bank, gw = generate_benchmark_records(size)

        start_time = time.perf_counter()
        summary, results = run_reconciliation_batch(invs, bank, gw)
        elapsed_sec = time.perf_counter() - start_time

        throughput = size / elapsed_sec if elapsed_sec > 0 else 0.0
        match_rate = (summary['matched'] / summary['total_records']) * 100.0

        print(f"\n--- Batch Size: {size} Records ---")
        print(f"  Processing Time : {elapsed_sec:.4f} seconds ({elapsed_sec * 1000:.2f} ms)")
        print(f"  Throughput      : {throughput:.2f} records/sec")
        print(f"  Total Processed : {summary['total_records']}")
        print(f"  Matched Records : {summary['matched']} ({match_rate:.2f}%)")
        print(f"  Review Records  : {summary['review']}")
        print(f"  Exceptions      : {summary['exceptions']}")
        print("-" * 65)

    print("\nBenchmark Execution Completed Successfully.")


if __name__ == "__main__":
    run_benchmark()
