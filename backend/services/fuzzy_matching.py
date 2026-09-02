"""
Fuzzy String Matching Service
=============================
Provides high-performance fuzzy text similarity functions using RapidFuzz.

Similarity Thresholds (0 to 100):
- 90 to 100: Very Strong Similarity
- 80 to 89:  Strong Similarity
- 70 to 79:  Possible Similarity
- Below 70:  Weak Similarity (Rejected as insufficient match)
"""

from typing import Optional
from rapidfuzz import fuzz
from services.normalization import normalize_company_name


def fuzzy_company_name_similarity(name1: Optional[str], name2: Optional[str]) -> float:
    """
    Computes fuzzy string similarity ratio between two company/customer names.
    Returns a score between 0.0 and 100.0 using RapidFuzz WRatio.
    
    Ensures that similar names (e.g., 'ABC Technologies' vs 'ABC Tech') score high (80+),
    while distinct entities (e.g., 'ABC Technologies' vs 'ABC Logistics') score weak (<70).
    """
    if not name1 or not name2:
        return 0.0

    s1 = name1.strip().lower()
    s2 = name2.strip().lower()

    if not s1 or not s2:
        return 0.0

    if s1 == s2:
        return 100.0

    # Use WRatio (weighted composite fuzzy ratio) for abbreviations and partial token matches
    ratio = float(fuzz.WRatio(s1, s2))
    return round(ratio, 2)


def fuzzy_description_similarity(customer_name: Optional[str], bank_description: Optional[str]) -> float:
    """
    Computes fuzzy token similarity between an invoice customer name and a bank feed description
    after normalizing both strings to strip bank transaction noise.
    """
    if not customer_name or not bank_description:
        return 0.0

    c_norm = normalize_company_name(customer_name)
    b_norm = normalize_company_name(bank_description)

    if not c_norm or not b_norm:
        return 0.0

    if c_norm == b_norm:
        return 100.0

    ratio = float(fuzz.WRatio(c_norm, b_norm))
    return round(ratio, 2)


def fuzzy_reference_similarity(ref1: Optional[str], ref2: Optional[str]) -> float:
    """
    Conservative fuzzy comparison for reference IDs.
    Returns ratio only if similarity is >= 90.0; otherwise returns 0.0 to prevent
    completely different references from becoming false positive matches.
    """
    if not ref1 or not ref2:
        return 0.0

    r1 = ref1.strip().upper()
    r2 = ref2.strip().upper()

    if not r1 or not r2:
        return 0.0

    if r1 == r2:
        return 100.0

    ratio = float(fuzz.ratio(r1, r2))
    # Conservative threshold: completely different references score 0.0
    if ratio < 90.0:
        return 0.0

    return round(ratio, 2)
