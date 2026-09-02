"""
Data Normalization Layer
========================
Provides reusable in-memory data normalization functions for preparing multi-source
financial records (Invoices, Bank Transactions, Payment Gateway entries) for matching.

All functions keep original data intact while generating standardized values.
"""

import re
from datetime import datetime, date
from typing import Any, Dict, Optional


LEGAL_SUFFIXES = {
    "private limited", "pvt ltd", "pvt. ltd.", "pvt. ltd", "pvt.ltd.", "pvt.ltd",
    "private ltd", "pvt limited", "limited", "ltd", "ltd.", "inc", "inc.",
    "incorporated", "corp", "corp.", "corporation", "llp", "co", "co.", "company",
    "pvtltd"
}

# Transaction description noise tokens commonly found in bank feeds
TRANSACTION_NOISE_WORDS = {
    "payment", "neft", "rtgs", "cr", "dr", "upi", "settlement",
    "inward", "forex", "remittance", "transfer", "imps", "fd",
    "val", "nps", "nach", "cms", "fund", "funds"
}

# Synonyms for standardizing core word variations
WORD_SYNONYMS = {
    "enterprise": "enterprises",
    "tech": "technologies",
    "soln": "solutions",
    "solns": "solutions",
    "prod": "products",
    "ind": "industries",
    "vent": "ventures"
}


def normalize_company_name(name: Optional[str]) -> str:
    """
    Normalizes company/customer names by:
    - Converting to lowercase
    - Replacing punctuation with spaces
    - Collapsing extra whitespace
    - Stripping bank statement noise tokens (PAYMENT, NEFT, RTGS, CR, etc.) and reference pattern tokens
    - Removing legal company suffixes (Pvt, Private, Ltd, Limited, Inc, Corp, LLP, Co, etc.)
    - Standardizing common abbreviations (e.g. Enterprise -> Enterprises)
    
    Retains core entity names so distinct companies (e.g., 'ABC Technologies' vs 'ABC Logistics')
    do NOT become identical.
    """
    if not name or not isinstance(name, str):
        return ""

    # Convert to lowercase
    clean_name = name.lower()

    # Replace punctuation with spaces (keep alphanumeric and space)
    clean_name = re.sub(r"[^\w\s]", " ", clean_name)

    # Collapse multiple spaces and tokenize
    raw_tokens = [t for t in clean_name.split() if t]

    # Filter out bank feed noise words and reference pattern tokens (e.g. ref001, inv001, 2026-001)
    tokens = []
    for t in raw_tokens:
        if t in TRANSACTION_NOISE_WORDS:
            continue
        if re.match(r"^(ref|inv|pay)\d+$", t) or re.match(r"^\d{4}\d+$", t):
            continue
        tokens.append(t)

    # Iteratively remove legal suffixes from the end of token list
    while tokens:
        # Check two-token suffix (e.g., 'pvt', 'ltd' or 'private', 'limited')
        if len(tokens) >= 2:
            two_word_suffix = f"{tokens[-2]} {tokens[-1]}"
            if two_word_suffix in LEGAL_SUFFIXES:
                tokens = tokens[:-2]
                continue

        # Check single-token suffix
        if tokens[-1] in LEGAL_SUFFIXES:
            tokens.pop()
            continue

        break

    # Apply word synonym standardization (e.g. enterprise -> enterprises)
    normalized_tokens = [WORD_SYNONYMS.get(t, t) for t in tokens]

    return " ".join(normalized_tokens)


def normalize_reference(ref: Optional[str]) -> str:
    """
    Normalizes reference IDs (e.g., INV-001, inv001, INV 001) by:
    - Converting to uppercase
    - Stripping hyphens, spaces, underscores, and punctuation
    """
    if not ref or not isinstance(ref, str):
        return ""

    # Convert to uppercase and remove non-alphanumeric characters
    cleaned = re.sub(r"[^\w]", "", ref.upper())
    return cleaned


def normalize_amount(val: Any) -> float:
    """
    Converts monetary amounts into cleaned floating-point numbers rounded to 2 decimals.
    
    Handles strings with currency symbols (₹, $, €, £), commas, and spaces.
    Raises ValueError for invalid, non-numeric, or empty amounts.
    """
    if val is None or val == "":
        raise ValueError(f"Invalid amount value: {val}")

    if isinstance(val, (int, float)):
        return round(float(val), 2)

    if isinstance(val, str):
        # Remove currency symbols, commas, and whitespace
        cleaned = re.sub(r"[^\d.-]", "", val.strip())
        if not cleaned or cleaned == "-":
            raise ValueError(f"Invalid amount format: {val}")
        try:
            return round(float(cleaned), 2)
        except ValueError:
            raise ValueError(f"Could not parse amount string: {val}")

    raise ValueError(f"Unsupported amount type: {type(val)}")


def normalize_date(date_val: Any) -> str:
    """
    Converts dates into standard ISO format (YYYY-MM-DD).
    
    Supports formats:
    - YYYY-MM-DD
    - DD-MM-YYYY
    - DD/MM/YYYY
    - YYYY/MM/DD
    - DD.MM.YYYY
    - YYYY.MM.DD
    
    Raises ValueError for invalid date strings or unparseable formats.
    """
    if not date_val:
        raise ValueError(f"Invalid empty date value: {date_val}")

    if isinstance(date_val, (datetime, date)):
        return date_val.strftime("%Y-%m-%d")

    if isinstance(date_val, str):
        cleaned_str = date_val.strip()
        supported_formats = [
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%d.%m.%Y",
            "%Y.%m.%d"
        ]

        for fmt in supported_formats:
            try:
                dt = datetime.strptime(cleaned_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        raise ValueError(f"Unparseable date format: '{date_val}'")

    raise ValueError(f"Unsupported date type: {type(date_val)}")


def normalize_currency(curr: Optional[str]) -> str:
    """
    Normalizes currency codes into standard uppercase 3-letter ISO string (e.g. INR, USD, EUR).
    Raises ValueError if input is empty or invalid.
    """
    if not curr or not isinstance(curr, str):
        raise ValueError(f"Invalid currency code: {curr}")

    cleaned = curr.strip().upper()
    if not cleaned or len(cleaned) != 3:
        raise ValueError(f"Currency code must be a 3-letter string: {curr}")

    return cleaned


def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processes a complete invoice, bank, or gateway record dict.
    Returns a dictionary structure containing both original raw values and normalized values.
    
    Does NOT mutate raw CSV data or original input records.
    """
    if not isinstance(record, dict):
        raise ValueError("Record must be a dictionary")

    normalized_data = {}

    # Company / Customer Name
    customer_key = next((k for k in ("customer_name", "description") if k in record and record[k]), None)
    if customer_key:
        normalized_data["customer_name"] = normalize_company_name(str(record[customer_key]))

    # Reference
    ref_key = next((k for k in ("reference", "ref") if k in record and record[k]), None)
    if ref_key:
        normalized_data["reference"] = normalize_reference(str(record[ref_key]))

    # Amount
    amt_key = next((k for k in ("amount", "net_amount") if k in record and record[k] is not None), None)
    if amt_key:
        try:
            normalized_data["amount"] = normalize_amount(record[amt_key])
        except ValueError:
            normalized_data["amount"] = None

    # Currency
    curr_key = next((k for k in ("currency", "curr") if k in record and record[k]), None)
    if curr_key:
        try:
            normalized_data["currency"] = normalize_currency(str(record[curr_key]))
        except ValueError:
            normalized_data["currency"] = None

    # Date
    date_key = next((k for k in ("invoice_date", "transaction_date", "payment_date", "date", "due_date") if k in record and record[k]), None)
    if date_key:
        try:
            normalized_data["date"] = normalize_date(str(record[date_key]))
        except ValueError:
            normalized_data["date"] = None

    return {
        "original": dict(record),
        "normalized": normalized_data
    }
