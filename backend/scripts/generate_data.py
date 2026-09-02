"""
Synthetic Financial Dataset Generator
====================================
Generates realistic multi-source financial transaction records:
1. data/invoices.csv - Billing ledger invoices (ERP export)
2. data/bank_transactions.csv - Bank statement feed (CREDIT records)
3. data/gateway_transactions.csv - Payment gateway settlements (Razorpay, Stripe, PayU)
4. data/ground_truth.csv - Ground truth annotations for measuring reconciliation metrics

Scenarios included (120 total invoices):
- 65 exact matches
- 15 customer-name variations (abbreviations, legal suffix variations)
- 10 payment date variations (delayed settlements / late payments)
- 8 amount mismatches (withholding tax / TDS / deductions / partial payments)
- 5 duplicate payments (double bank credits / repeated settlements)
- 5 missing payments (unpaid invoices, missing gateway or bank records)
- 4 gateway fee cases (net settlement vs gross invoice amount)
- 4 ambiguous matches (identical amounts, shared customer candidates)
- 2 reference mismatches (typos in reference numbers)
- 2 currency mismatches (cross-border USD/EUR billing vs domestic settlement)
"""

import os
import random
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Fixed random seed for complete reproducibility
RANDOM_SEED = 42

# Base enterprise customer list with official legal names
ENTERPRISE_CUSTOMERS = [
    "ABC Private Limited",
    "Ravi Enterprises Private Limited",
    "Apex Global Technologies Pvt Ltd",
    "Zenith Logistics Solutions Limited",
    "Tata Consultancy Services Limited",
    "Infosys BPM Private Limited",
    "Reliance Retail Ventures Limited",
    "Mahindra Logistics Solutions Ltd",
    "Larsen and Toubro Infotech Ltd",
    "Wipro Digital Solutions Pvt Ltd",
    "HCL Technologies India Pvt Ltd",
    "Bharat Heavy Electricals Limited",
    "Sun Pharmaceutical Industries Ltd",
    "Godrej Consumer Products Limited",
    "Adani Ports and SEZ Private Limited",
    "Bajaj Finserv Direct Limited",
    "Tech Mahindra Solutions Limited",
    "Zomato Media Private Limited",
    "Swiggy Bundl Technologies Pvt Ltd",
    "Flipkart Internet Private Limited",
    "One97 Communications Limited",
    "Nykaa E-Retail Private Limited",
    "Delhivery Logistics Private Limited",
    "Urban Company Technologies Ltd",
    "Razorpay Software Private Limited",
    "Freshworks Technologies Pvt Ltd",
    "Zoho Corporation Private Limited",
    "Pine Labs Private Limited",
    "Policybazaar Insurance Brokers Ltd",
    "PhonePe India Private Limited",
    "MakeMyTrip India Private Limited",
    "Ola ANI Technologies Private Limited",
    "PayU Payments Private Limited",
    "CRED Dreamplug Technologies Ltd",
    "Groww Nextbillion Technology Ltd",
    "Zerodha Broking Limited",
    "BigBasket Supermarket Grocery Ltd",
    "Blinkit Commerce Private Limited",
    "Dunzo Digital Private Limited",
    "Meesho Fashnear Technologies Ltd",
    "Cars24 Services Private Limited",
    "Spinny Valuedrive Technologies Ltd",
    "Lenskart Solutions Private Limited",
    "Pharmeasy API Holdings Limited",
    "Tata Digital Private Limited",
    "Jio Platforms Limited",
    "Airtel Digital Limited",
    "Vodafone Idea Enterprise Solutions",
    "ITC Infotech India Limited",
    "Cognizant Technology Solutions Ltd"
]

GATEWAYS = ["Razorpay", "Stripe", "PayU"]


def get_project_paths() -> Tuple[str, str]:
    """Resolve project root and data directory paths."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    data_dir = os.path.join(project_root, "data")
    return project_root, data_dir


def generate_all_datasets(data_dir: str = None, seed: int = RANDOM_SEED) -> Dict[str, int]:
    """
    Generate reproducible synthetic datasets across all 4 CSV files.
    
    Returns a dictionary with record counts for each file.
    """
    if data_dir is None:
        _, data_dir = get_project_paths()

    os.makedirs(data_dir, exist_ok=True)
    rng = random.Random(seed)

    invoices: List[Dict] = []
    bank_txns: List[Dict] = []
    gateway_txns: List[Dict] = []
    ground_truth: List[Dict] = []

    bank_counter = 1
    gateway_counter = 1
    base_date = datetime(2026, 8, 1)

    def next_bank_id() -> str:
        nonlocal bank_counter
        b_id = f"BANK{bank_counter:03d}"
        bank_counter += 1
        return b_id

    def next_gateway_id() -> str:
        nonlocal gateway_counter
        g_id = f"PAY{gateway_counter:03d}"
        gateway_counter += 1
        return g_id

    # -------------------------------------------------------------
    # 1. EXACT MATCHES (65 invoices: INV001 - INV065)
    # -------------------------------------------------------------
    for i in range(1, 66):
        inv_id = f"INV{i:03d}"
        cust_id = f"CUST{((i - 1) % len(ENTERPRISE_CUSTOMERS)) + 1:03d}"
        cust_name = ENTERPRISE_CUSTOMERS[(i - 1) % len(ENTERPRISE_CUSTOMERS)]
        inv_num = f"2026-{i:03d}"
        amount = round(rng.choice([12500, 24000, 35000, 48000, 62000, 75000, 89000, 115000, 150000, 225000]), 2)
        currency = "INR"
        inv_date = (base_date + timedelta(days=rng.randint(0, 14))).strftime("%Y-%m-%d")
        due_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d")
        ref = f"REF{i:03d}"
        status = "PAID"

        invoices.append({
            "invoice_id": inv_id,
            "customer_id": cust_id,
            "customer_name": cust_name,
            "invoice_number": inv_num,
            "amount": amount,
            "currency": currency,
            "invoice_date": inv_date,
            "due_date": due_date,
            "reference": ref,
            "status": status
        })

        b_id = next_bank_id()
        b_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=rng.randint(1, 3))).strftime("%Y-%m-%d")
        bank_txns.append({
            "transaction_id": b_id,
            "description": f"{cust_name.upper()} PAYMENT {ref}",
            "amount": amount,
            "currency": currency,
            "transaction_date": b_date,
            "reference": ref,
            "transaction_type": "CREDIT"
        })

        g_id = next_gateway_id()
        gateway = rng.choice(GATEWAYS)
        fee_rate = 0.02 if gateway == "Razorpay" else (0.025 if gateway == "Stripe" else 0.018)
        fee = round(amount * fee_rate, 2)
        net_amount = round(amount - fee, 2)
        gateway_txns.append({
            "payment_id": g_id,
            "gateway": gateway,
            "customer_name": cust_name,
            "amount": amount,
            "fee": fee,
            "net_amount": net_amount,
            "currency": currency,
            "payment_date": b_date,
            "reference": ref,
            "payment_status": "SUCCESS"
        })

        ground_truth.append({
            "invoice_id": inv_id,
            "expected_bank_transaction_id": b_id,
            "expected_gateway_payment_id": g_id,
            "expected_status": "MATCHED",
            "scenario_type": "exact_match"
        })

    # -------------------------------------------------------------
    # 2. CUSTOMER-NAME VARIATIONS (15 invoices: INV066 - INV080)
    # -------------------------------------------------------------
    name_variation_samples = [
        ("ABC Private Limited", "ABC PVT LTD", "ABC Pvt Ltd"),
        ("Ravi Enterprises Private Limited", "RAVI ENTERPRISE", "Ravi Enterprises"),
        ("Apex Global Technologies Pvt Ltd", "APEX GLOBAL TECH", "Apex Global Tech Ltd"),
        ("Zenith Logistics Solutions Limited", "ZENITH LOGISTICS SOLN", "Zenith Logistics Ltd"),
        ("Tata Consultancy Services Limited", "TCS LTD PAYMENT", "Tata Consultancy Services"),
        ("Infosys BPM Private Limited", "INFOSYS BPM PVT", "Infosys BPM"),
        ("Reliance Retail Ventures Limited", "RELIANCE RETAIL VENT", "Reliance Retail"),
        ("Mahindra Logistics Solutions Ltd", "M&M LOGISTICS", "Mahindra Logistics"),
        ("Larsen and Toubro Infotech Ltd", "L&T INFOTECH", "L&T Infotech Ltd"),
        ("Wipro Digital Solutions Pvt Ltd", "WIPRO DIGITAL", "Wipro Digital Solutions"),
        ("HCL Technologies India Pvt Ltd", "HCL TECH INDIA", "HCL Technologies"),
        ("Sun Pharmaceutical Industries Ltd", "SUN PHARMA IND", "Sun Pharma Ltd"),
        ("Godrej Consumer Products Limited", "GODREJ CONSUMER PROD", "Godrej Consumer"),
        ("Adani Ports and SEZ Private Limited", "ADANI PORTS SEZ", "Adani Ports Ltd"),
        ("Bajaj Finserv Direct Limited", "BAJAJ FINSERV DIR", "Bajaj Finserv Direct")
    ]

    for idx, (legal_name, bank_name_var, gw_name_var) in enumerate(name_variation_samples, start=66):
        inv_id = f"INV{idx:03d}"
        cust_id = f"CUST{idx:03d}"
        inv_num = f"2026-{idx:03d}"
        amount = round(rng.choice([18000, 32000, 54000, 78000, 96000, 142000]), 2)
        currency = "INR"
        inv_date = (base_date + timedelta(days=rng.randint(2, 16))).strftime("%Y-%m-%d")
        due_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d")
        ref = f"REF{idx:03d}"
        status = "PAID"

        invoices.append({
            "invoice_id": inv_id,
            "customer_id": cust_id,
            "customer_name": legal_name,
            "invoice_number": inv_num,
            "amount": amount,
            "currency": currency,
            "invoice_date": inv_date,
            "due_date": due_date,
            "reference": ref,
            "status": status
        })

        b_id = next_bank_id()
        b_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=rng.randint(1, 3))).strftime("%Y-%m-%d")
        bank_txns.append({
            "transaction_id": b_id,
            "description": f"{bank_name_var} NEFT CR {ref}",
            "amount": amount,
            "currency": currency,
            "transaction_date": b_date,
            "reference": ref,
            "transaction_type": "CREDIT"
        })

        g_id = next_gateway_id()
        gateway = rng.choice(GATEWAYS)
        fee = round(amount * 0.02, 2)
        net_amount = round(amount - fee, 2)
        gateway_txns.append({
            "payment_id": g_id,
            "gateway": gateway,
            "customer_name": gw_name_var,
            "amount": amount,
            "fee": fee,
            "net_amount": net_amount,
            "currency": currency,
            "payment_date": b_date,
            "reference": ref,
            "payment_status": "SUCCESS"
        })

        ground_truth.append({
            "invoice_id": inv_id,
            "expected_bank_transaction_id": b_id,
            "expected_gateway_payment_id": g_id,
            "expected_status": "MATCHED",
            "scenario_type": "customer_name_variation"
        })

    # -------------------------------------------------------------
    # 3. PAYMENT DATE VARIATIONS (10 invoices: INV081 - INV090)
    # -------------------------------------------------------------
    for i in range(81, 91):
        inv_id = f"INV{i:03d}"
        cust_id = f"CUST{((i - 1) % len(ENTERPRISE_CUSTOMERS)) + 1:03d}"
        cust_name = ENTERPRISE_CUSTOMERS[(i - 1) % len(ENTERPRISE_CUSTOMERS)]
        inv_num = f"2026-{i:03d}"
        amount = round(rng.choice([25000, 42000, 68000, 88000, 130000]), 2)
        currency = "INR"
        inv_date = (base_date + timedelta(days=rng.randint(0, 5))).strftime("%Y-%m-%d")
        due_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d")
        ref = f"REF{i:03d}"
        status = "PAID"

        invoices.append({
            "invoice_id": inv_id,
            "customer_id": cust_id,
            "customer_name": cust_name,
            "invoice_number": inv_num,
            "amount": amount,
            "currency": currency,
            "invoice_date": inv_date,
            "due_date": due_date,
            "reference": ref,
            "status": status
        })

        # Payment happens 20 to 35 days later (delayed settlement)
        delayed_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=rng.randint(20, 35))).strftime("%Y-%m-%d")

        b_id = next_bank_id()
        bank_txns.append({
            "transaction_id": b_id,
            "description": f"{cust_name.upper()} DELAYED SETTLEMENT {ref}",
            "amount": amount,
            "currency": currency,
            "transaction_date": delayed_date,
            "reference": ref,
            "transaction_type": "CREDIT"
        })

        g_id = next_gateway_id()
        gateway = rng.choice(GATEWAYS)
        fee = round(amount * 0.02, 2)
        net_amount = round(amount - fee, 2)
        gateway_txns.append({
            "payment_id": g_id,
            "gateway": gateway,
            "customer_name": cust_name,
            "amount": amount,
            "fee": fee,
            "net_amount": net_amount,
            "currency": currency,
            "payment_date": delayed_date,
            "reference": ref,
            "payment_status": "SUCCESS"
        })

        ground_truth.append({
            "invoice_id": inv_id,
            "expected_bank_transaction_id": b_id,
            "expected_gateway_payment_id": g_id,
            "expected_status": "MATCHED",
            "scenario_type": "payment_date_variation"
        })

    # -------------------------------------------------------------
    # 4. AMOUNT MISMATCHES (8 invoices: INV091 - INV098)
    # -------------------------------------------------------------
    amount_mismatch_configs = [
        (20000.00, 19500.00, "TDS deduction mismatch ₹500"),
        (45000.00, 44100.00, "2% withholding tax discrepancy"),
        (15800.00, 15000.00, "Customer rounded off transfer"),
        (82000.00, 80000.00, "Short payment / dispute deduction"),
        (34500.00, 35000.00, "Customer slight overpayment"),
        (12000.00, 11000.00, "Partial payment received"),
        (67500.00, 66150.00, "2% tax deducted at source"),
        (29000.00, 28500.00, "Short payment received")
    ]

    for idx, (inv_amt, bank_amt, desc_note) in enumerate(amount_mismatch_configs, start=91):
        inv_id = f"INV{idx:03d}"
        cust_id = f"CUST{idx:03d}"
        cust_name = ENTERPRISE_CUSTOMERS[(idx - 1) % len(ENTERPRISE_CUSTOMERS)]
        inv_num = f"2026-{idx:03d}"
        currency = "INR"
        inv_date = (base_date + timedelta(days=rng.randint(3, 15))).strftime("%Y-%m-%d")
        due_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d")
        ref = f"REF{idx:03d}"
        status = "PARTIAL_PAID"

        invoices.append({
            "invoice_id": inv_id,
            "customer_id": cust_id,
            "customer_name": cust_name,
            "invoice_number": inv_num,
            "amount": inv_amt,
            "currency": currency,
            "invoice_date": inv_date,
            "due_date": due_date,
            "reference": ref,
            "status": status
        })

        b_id = next_bank_id()
        b_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=rng.randint(1, 4))).strftime("%Y-%m-%d")
        bank_txns.append({
            "transaction_id": b_id,
            "description": f"{cust_name.upper()} PAYMENT {ref} ({desc_note})",
            "amount": bank_amt,
            "currency": currency,
            "transaction_date": b_date,
            "reference": ref,
            "transaction_type": "CREDIT"
        })

        g_id = next_gateway_id()
        gateway = rng.choice(GATEWAYS)
        fee = round(bank_amt * 0.02, 2)
        net_amount = round(bank_amt - fee, 2)
        gateway_txns.append({
            "payment_id": g_id,
            "gateway": gateway,
            "customer_name": cust_name,
            "amount": bank_amt,
            "fee": fee,
            "net_amount": net_amount,
            "currency": currency,
            "payment_date": b_date,
            "reference": ref,
            "payment_status": "SUCCESS"
        })

        ground_truth.append({
            "invoice_id": inv_id,
            "expected_bank_transaction_id": b_id,
            "expected_gateway_payment_id": g_id,
            "expected_status": "AMOUNT_MISMATCH",
            "scenario_type": "amount_mismatch"
        })

    # -------------------------------------------------------------
    # 5. DUPLICATE PAYMENTS (5 invoices: INV099 - INV103)
    # -------------------------------------------------------------
    for i in range(99, 104):
        inv_id = f"INV{i:03d}"
        cust_id = f"CUST{((i - 1) % len(ENTERPRISE_CUSTOMERS)) + 1:03d}"
        cust_name = ENTERPRISE_CUSTOMERS[(i - 1) % len(ENTERPRISE_CUSTOMERS)]
        inv_num = f"2026-{i:03d}"
        amount = round(rng.choice([35000, 52000, 74000, 91000, 112000]), 2)
        currency = "INR"
        inv_date = (base_date + timedelta(days=rng.randint(4, 18))).strftime("%Y-%m-%d")
        due_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d")
        ref = f"REF{i:03d}"
        status = "PAID"

        invoices.append({
            "invoice_id": inv_id,
            "customer_id": cust_id,
            "customer_name": cust_name,
            "invoice_number": inv_num,
            "amount": amount,
            "currency": currency,
            "invoice_date": inv_date,
            "due_date": due_date,
            "reference": ref,
            "status": status
        })

        b_id_1 = next_bank_id()
        b_date_1 = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        bank_txns.append({
            "transaction_id": b_id_1,
            "description": f"{cust_name.upper()} PAYMENT {ref}",
            "amount": amount,
            "currency": currency,
            "transaction_date": b_date_1,
            "reference": ref,
            "transaction_type": "CREDIT"
        })

        # Second accidental duplicate bank transfer
        b_id_2 = next_bank_id()
        b_date_2 = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=2)).strftime("%Y-%m-%d")
        bank_txns.append({
            "transaction_id": b_id_2,
            "description": f"{cust_name.upper()} DUPLICATE PAYMENT {ref}",
            "amount": amount,
            "currency": currency,
            "transaction_date": b_date_2,
            "reference": ref,
            "transaction_type": "CREDIT"
        })

        g_id = next_gateway_id()
        gateway = rng.choice(GATEWAYS)
        fee = round(amount * 0.02, 2)
        net_amount = round(amount - fee, 2)
        gateway_txns.append({
            "payment_id": g_id,
            "gateway": gateway,
            "customer_name": cust_name,
            "amount": amount,
            "fee": fee,
            "net_amount": net_amount,
            "currency": currency,
            "payment_date": b_date_1,
            "reference": ref,
            "payment_status": "SUCCESS"
        })

        ground_truth.append({
            "invoice_id": inv_id,
            "expected_bank_transaction_id": f"{b_id_1},{b_id_2}",
            "expected_gateway_payment_id": g_id,
            "expected_status": "DUPLICATE_PAYMENT",
            "scenario_type": "duplicate_payment"
        })

    # -------------------------------------------------------------
    # 6. MISSING PAYMENTS (5 invoices: INV104 - INV108)
    # -------------------------------------------------------------
    # 3 completely missing (no bank, no gateway), 2 missing gateway only (invoice matches bank)
    missing_configs = [
        ("OVERDUE", False, False),  # no bank, no gateway
        ("PENDING", False, False),  # no bank, no gateway
        ("UNPAID", False, False),   # no bank, no gateway
        ("PAID", True, False),      # bank exists, gateway missing
        ("PAID", True, False),      # bank exists, gateway missing
    ]

    for idx, (inv_status, has_bank, has_gw) in enumerate(missing_configs, start=104):
        inv_id = f"INV{idx:03d}"
        cust_id = f"CUST{idx:03d}"
        cust_name = ENTERPRISE_CUSTOMERS[(idx - 1) % len(ENTERPRISE_CUSTOMERS)]
        inv_num = f"2026-{idx:03d}"
        amount = round(rng.choice([16500, 31000, 49000, 72000, 95000]), 2)
        currency = "INR"
        inv_date = (base_date + timedelta(days=rng.randint(1, 10))).strftime("%Y-%m-%d")
        due_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d")
        ref = f"REF{idx:03d}"

        invoices.append({
            "invoice_id": inv_id,
            "customer_id": cust_id,
            "customer_name": cust_name,
            "invoice_number": inv_num,
            "amount": amount,
            "currency": currency,
            "invoice_date": inv_date,
            "due_date": due_date,
            "reference": ref,
            "status": inv_status
        })

        expected_b_id = "NONE"
        if has_bank:
            b_id = next_bank_id()
            expected_b_id = b_id
            b_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=2)).strftime("%Y-%m-%d")
            bank_txns.append({
                "transaction_id": b_id,
                "description": f"{cust_name.upper()} DIRECT RTGS PAYMENT {ref}",
                "amount": amount,
                "currency": currency,
                "transaction_date": b_date,
                "reference": ref,
                "transaction_type": "CREDIT"
            })

        expected_g_id = "NONE"
        if has_gw:
            g_id = next_gateway_id()
            expected_g_id = g_id
            # not executed for current missing_configs

        ground_truth.append({
            "invoice_id": inv_id,
            "expected_bank_transaction_id": expected_b_id,
            "expected_gateway_payment_id": expected_g_id,
            "expected_status": "MISSING_PAYMENT",
            "scenario_type": "missing_payment"
        })

    # -------------------------------------------------------------
    # 7. GATEWAY FEE CASES (4 invoices: INV109 - INV112)
    # -------------------------------------------------------------
    gateway_fee_configs = [
        (50000.00, 1180.00),
        (75000.00, 1770.00),
        (100000.00, 2360.00),
        (32000.00, 755.20)
    ]

    for idx, (gross_amt, fee_amt) in enumerate(gateway_fee_configs, start=109):
        inv_id = f"INV{idx:03d}"
        cust_id = f"CUST{idx:03d}"
        cust_name = ENTERPRISE_CUSTOMERS[(idx - 1) % len(ENTERPRISE_CUSTOMERS)]
        inv_num = f"2026-{idx:03d}"
        currency = "INR"
        inv_date = (base_date + timedelta(days=rng.randint(5, 17))).strftime("%Y-%m-%d")
        due_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d")
        ref = f"REF{idx:03d}"
        status = "PAID"

        net_settlement = round(gross_amt - fee_amt, 2)

        invoices.append({
            "invoice_id": inv_id,
            "customer_id": cust_id,
            "customer_name": cust_name,
            "invoice_number": inv_num,
            "amount": gross_amt,
            "currency": currency,
            "invoice_date": inv_date,
            "due_date": due_date,
            "reference": ref,
            "status": status
        })

        b_id = next_bank_id()
        b_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=2)).strftime("%Y-%m-%d")
        gateway_name = rng.choice(GATEWAYS)
        # Bank receives net amount directly from gateway payout
        bank_txns.append({
            "transaction_id": b_id,
            "description": f"{gateway_name.upper()} NODAL PAYOUT {ref} NET SETTLEMENT",
            "amount": net_settlement,
            "currency": currency,
            "transaction_date": b_date,
            "reference": ref,
            "transaction_type": "CREDIT"
        })

        g_id = next_gateway_id()
        gateway_txns.append({
            "payment_id": g_id,
            "gateway": gateway_name,
            "customer_name": cust_name,
            "amount": gross_amt,
            "fee": fee_amt,
            "net_amount": net_settlement,
            "currency": currency,
            "payment_date": b_date,
            "reference": ref,
            "payment_status": "SUCCESS"
        })

        ground_truth.append({
            "invoice_id": inv_id,
            "expected_bank_transaction_id": b_id,
            "expected_gateway_payment_id": g_id,
            "expected_status": "FEE_MISMATCH",
            "scenario_type": "gateway_fee"
        })

    # -------------------------------------------------------------
    # 8. AMBIGUOUS MATCHES (4 invoices: INV113 - INV116)
    # -------------------------------------------------------------
    # Pairs of identical invoices for same customer with overlapping candidate amounts
    ambiguous_pairs = [
        (113, 114, "Zomato Media Private Limited", 25000.00),
        (115, 116, "Freshworks Technologies Pvt Ltd", 48000.00)
    ]

    for inv_id_1, inv_id_2, shared_cust, shared_amt in ambiguous_pairs:
        for cur_id in [inv_id_1, inv_id_2]:
            inv_id = f"INV{cur_id:03d}"
            cust_id = f"CUST{cur_id:03d}"
            inv_num = f"2026-{cur_id:03d}"
            currency = "INR"
            inv_date = "2026-08-12"
            due_date = "2026-08-26"
            ref = f"REF{cur_id:03d}"
            status = "PAID"

            invoices.append({
                "invoice_id": inv_id,
                "customer_id": cust_id,
                "customer_name": shared_cust,
                "invoice_number": inv_num,
                "amount": shared_amt,
                "currency": currency,
                "invoice_date": inv_date,
                "due_date": due_date,
                "reference": ref,
                "status": status
            })

            b_id = next_bank_id()
            b_date = "2026-08-14"
            # Bank statement has generic description without specific invoice number
            bank_txns.append({
                "transaction_id": b_id,
                "description": f"{shared_cust.upper()} BULK PAYMENT TRF",
                "amount": shared_amt,
                "currency": currency,
                "transaction_date": b_date,
                "reference": "GENERIC_TRANSFER",
                "transaction_type": "CREDIT"
            })

            g_id = next_gateway_id()
            gateway = "Razorpay"
            fee = round(shared_amt * 0.02, 2)
            net_amount = round(shared_amt - fee, 2)
            gateway_txns.append({
                "payment_id": g_id,
                "gateway": gateway,
                "customer_name": shared_cust,
                "amount": shared_amt,
                "fee": fee,
                "net_amount": net_amount,
                "currency": currency,
                "payment_date": b_date,
                "reference": "GENERIC_TRANSFER",
                "payment_status": "SUCCESS"
            })

            ground_truth.append({
                "invoice_id": inv_id,
                "expected_bank_transaction_id": b_id,
                "expected_gateway_payment_id": g_id,
                "expected_status": "AMBIGUOUS_MATCH",
                "scenario_type": "ambiguous_match"
            })

    # -------------------------------------------------------------
    # 9. REFERENCE MISMATCHES (2 invoices: INV117 - INV118)
    # -------------------------------------------------------------
    ref_mismatch_configs = [
        (117, "REF117", "REF711_TYPO", 38000.00),
        (118, "REF118", "REF811_ERR", 64000.00)
    ]

    for idx, correct_ref, typo_ref, amt in ref_mismatch_configs:
        inv_id = f"INV{idx:03d}"
        cust_id = f"CUST{idx:03d}"
        cust_name = ENTERPRISE_CUSTOMERS[(idx - 1) % len(ENTERPRISE_CUSTOMERS)]
        inv_num = f"2026-{idx:03d}"
        currency = "INR"
        inv_date = (base_date + timedelta(days=rng.randint(6, 18))).strftime("%Y-%m-%d")
        due_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d")
        status = "PAID"

        invoices.append({
            "invoice_id": inv_id,
            "customer_id": cust_id,
            "customer_name": cust_name,
            "invoice_number": inv_num,
            "amount": amt,
            "currency": currency,
            "invoice_date": inv_date,
            "due_date": due_date,
            "reference": correct_ref,
            "status": status
        })

        b_id = next_bank_id()
        b_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=2)).strftime("%Y-%m-%d")
        bank_txns.append({
            "transaction_id": b_id,
            "description": f"{cust_name.upper()} PAYMENT {typo_ref}",
            "amount": amt,
            "currency": currency,
            "transaction_date": b_date,
            "reference": typo_ref,
            "transaction_type": "CREDIT"
        })

        g_id = next_gateway_id()
        gateway = rng.choice(GATEWAYS)
        fee = round(amt * 0.02, 2)
        net_amount = round(amt - fee, 2)
        gateway_txns.append({
            "payment_id": g_id,
            "gateway": gateway,
            "customer_name": cust_name,
            "amount": amt,
            "fee": fee,
            "net_amount": net_amount,
            "currency": currency,
            "payment_date": b_date,
            "reference": typo_ref,
            "payment_status": "SUCCESS"
        })

        ground_truth.append({
            "invoice_id": inv_id,
            "expected_bank_transaction_id": b_id,
            "expected_gateway_payment_id": g_id,
            "expected_status": "REFERENCE_MISMATCH",
            "scenario_type": "reference_mismatch"
        })

    # -------------------------------------------------------------
    # 10. CURRENCY MISMATCHES (2 invoices: INV119 - INV120)
    # -------------------------------------------------------------
    curr_mismatch_configs = [
        (119, "USD", 1200.00, 100200.00, "INR", "Stripe"),   # USD $1200 invoice settled as INR 100,200
        (120, "EUR", 1500.00, 138000.00, "INR", "Razorpay")  # EUR €1500 invoice settled as INR 138,000
    ]

    for idx, inv_curr, inv_amt, bank_amt, bank_curr, gw in curr_mismatch_configs:
        inv_id = f"INV{idx:03d}"
        cust_id = f"CUST{idx:03d}"
        cust_name = ENTERPRISE_CUSTOMERS[(idx - 1) % len(ENTERPRISE_CUSTOMERS)]
        inv_num = f"2026-{idx:03d}"
        inv_date = (base_date + timedelta(days=rng.randint(7, 19))).strftime("%Y-%m-%d")
        due_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d")
        ref = f"REF{idx:03d}"
        status = "PAID"

        invoices.append({
            "invoice_id": inv_id,
            "customer_id": cust_id,
            "customer_name": cust_name,
            "invoice_number": inv_num,
            "amount": inv_amt,
            "currency": inv_curr,
            "invoice_date": inv_date,
            "due_date": due_date,
            "reference": ref,
            "status": status
        })

        b_id = next_bank_id()
        b_date = (datetime.strptime(inv_date, "%Y-%m-%d") + timedelta(days=3)).strftime("%Y-%m-%d")
        bank_txns.append({
            "transaction_id": b_id,
            "description": f"INWARD FOREX REMITTANCE {cust_name.upper()} {inv_curr} {inv_amt} {ref}",
            "amount": bank_amt,
            "currency": bank_curr,
            "transaction_date": b_date,
            "reference": ref,
            "transaction_type": "CREDIT"
        })

        g_id = next_gateway_id()
        fee = round(bank_amt * 0.02, 2)
        net_amount = round(bank_amt - fee, 2)
        gateway_txns.append({
            "payment_id": g_id,
            "gateway": gw,
            "customer_name": cust_name,
            "amount": bank_amt,
            "fee": fee,
            "net_amount": net_amount,
            "currency": bank_curr,
            "payment_date": b_date,
            "reference": ref,
            "payment_status": "SUCCESS"
        })

        ground_truth.append({
            "invoice_id": inv_id,
            "expected_bank_transaction_id": b_id,
            "expected_gateway_payment_id": g_id,
            "expected_status": "CURRENCY_MISMATCH",
            "scenario_type": "currency_mismatch"
        })

    # -------------------------------------------------------------
    # Write CSV files
    # -------------------------------------------------------------
    invoice_path = os.path.join(data_dir, "invoices.csv")
    bank_path = os.path.join(data_dir, "bank_transactions.csv")
    gateway_path = os.path.join(data_dir, "gateway_transactions.csv")
    ground_truth_path = os.path.join(data_dir, "ground_truth.csv")

    with open(invoice_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "invoice_id", "customer_id", "customer_name", "invoice_number",
            "amount", "currency", "invoice_date", "due_date", "reference", "status"
        ])
        writer.writeheader()
        writer.writerows(invoices)

    with open(bank_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "transaction_id", "description", "amount", "currency",
            "transaction_date", "reference", "transaction_type"
        ])
        writer.writeheader()
        writer.writerows(bank_txns)

    with open(gateway_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "payment_id", "gateway", "customer_name", "amount", "fee",
            "net_amount", "currency", "payment_date", "reference", "payment_status"
        ])
        writer.writeheader()
        writer.writerows(gateway_txns)

    with open(ground_truth_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "invoice_id", "expected_bank_transaction_id", "expected_gateway_payment_id",
            "expected_status", "scenario_type"
        ])
        writer.writeheader()
        writer.writerows(ground_truth)

    stats = {
        "invoice_records": len(invoices),
        "bank_records": len(bank_txns),
        "gateway_records": len(gateway_txns),
        "ground_truth_records": len(ground_truth)
    }

    print("Synthetic Financial Dataset successfully generated:")
    print(f"  - Invoices ({invoice_path}): {stats['invoice_records']} records")
    print(f"  - Bank Transactions ({bank_path}): {stats['bank_records']} records")
    print(f"  - Gateway Transactions ({gateway_path}): {stats['gateway_records']} records")
    print(f"  - Ground Truth Annotations ({ground_truth_path}): {stats['ground_truth_records']} records")

    return stats


if __name__ == "__main__":
    generate_all_datasets()
