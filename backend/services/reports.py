"""
Reports & Export Service
=========================
Generates downloadable CSV exports and PDF summary reports based on live reconciliation,
exception classification, operational metrics, and immutable audit trail records.
"""

import io
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from services.reconciliation import (
    get_latest_results,
    LATEST_RECONCILIATION_BATCH,
    load_csv_records,
    run_reconciliation_batch,
    os
)
from services.exceptions import get_all_exceptions
from services.metrics import compute_metrics
from services.review import get_audit_trail_events


def get_data_dir() -> str:
    """Resolve absolute path to data directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    return os.path.join(project_root, "data")


def ensure_reconciliation_data() -> List[Dict[str, Any]]:
    """Ensures reconciliation results exist, running a batch on data files if cached results are empty."""
    results = get_latest_results()
    if not results:
        data_dir = get_data_dir()
        invoices_csv = os.path.join(data_dir, "invoices.csv")
        bank_csv = os.path.join(data_dir, "bank_transactions.csv")
        gateway_csv = os.path.join(data_dir, "gateway_transactions.csv")

        if os.path.exists(invoices_csv):
            invoices = load_csv_records(invoices_csv)
            bank_txns = load_csv_records(bank_csv)
            gateway_txns = load_csv_records(gateway_csv)
            _, results = run_reconciliation_batch(invoices, bank_txns, gateway_txns)

    return results


def generate_reconciliation_csv() -> str:
    """
    Generates Full Reconciliation CSV Export.
    Columns: invoice_id, customer_name, invoice_amount, bank_transaction_id,
             gateway_payment_id, confidence_score, status, exception_type, severity, final_status
    """
    results = ensure_reconciliation_data()
    if not results:
        return ""

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "invoice_id",
        "customer_name",
        "invoice_amount",
        "bank_transaction_id",
        "gateway_payment_id",
        "confidence_score",
        "status",
        "exception_type",
        "severity",
        "final_status"
    ])

    for r in results:
        writer.writerow([
            r.get("invoice_id", ""),
            r.get("customer_name", ""),
            r.get("invoice_amount", 0.0),
            r.get("selected_bank_transaction_id") or "",
            r.get("selected_gateway_payment_id") or "",
            r.get("overall_confidence_score", 0.0),
            r.get("status", ""),
            r.get("exception_type") or "",
            r.get("severity") or "",
            r.get("final_status") or r.get("status", "")
        ])

    return output.getvalue()


def generate_exceptions_csv() -> str:
    """
    Generates Exception Report CSV.
    Columns: invoice_id, exception_type, severity, confidence_score, reason, suggested_action, status
    """
    ensure_reconciliation_data()
    exceptions = get_all_exceptions()
    if not exceptions:
        return ""

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "invoice_id",
        "exception_type",
        "severity",
        "confidence_score",
        "reason",
        "suggested_action",
        "status"
    ])

    for e in exceptions:
        writer.writerow([
            e.get("invoice_id", ""),
            e.get("exception_type", ""),
            e.get("severity", ""),
            e.get("confidence_score", 0.0),
            e.get("reason", ""),
            e.get("suggested_action", ""),
            e.get("status", "OPEN")
        ])

    return output.getvalue()


def generate_audit_csv(db: Optional[Session] = None) -> str:
    """
    Generates Audit Trail Report CSV.
    Columns: timestamp, invoice_id, actor, event_type, previous_state, new_state, note
    """
    audit_events = get_audit_trail_events(db=db)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "timestamp",
        "invoice_id",
        "actor",
        "event_type",
        "previous_state",
        "new_state",
        "note"
    ])

    for a in audit_events:
        writer.writerow([
            a.get("created_at", ""),
            a.get("invoice_id", ""),
            a.get("actor", ""),
            a.get("event_type", ""),
            a.get("previous_state", ""),
            a.get("new_state", ""),
            a.get("note", "")
        ])

    return output.getvalue()


def generate_summary_pdf(db: Optional[Session] = None) -> bytes:
    """
    Generates PDF Summary Report using ReportLab.
    Includes Title, timestamp, batch ID, KPI summary, exception breakdown, top unresolved exceptions, audit summary.
    """
    results = ensure_reconciliation_data()
    metrics = compute_metrics()
    exceptions = get_all_exceptions()
    audit_events = get_audit_trail_events(db=db)

    batch_id = (
        LATEST_RECONCILIATION_BATCH.get("batch_id")
        if LATEST_RECONCILIATION_BATCH
        else "N/A"
    )
    gen_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Build PDF in memory using ReportLab
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A')
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B')
    )

    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6
    )

    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # Title & Metadata Header
    story.append(Paragraph("AI Finance Controller — Reconciliation Report", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Generated: {gen_time} &nbsp;|&nbsp; Batch ID: <b>{batch_id}</b>", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceBefore=0, spaceAfter=10))

    # 1. KPI Summary Section
    story.append(Paragraph("Operational KPI Summary", h2_style))
    
    total_recs = metrics.get("total_records", 0)
    matched = metrics.get("automatically_matched", 0)
    review = metrics.get("needs_review", 0)
    exc_count = metrics.get("exceptions", 0)
    match_rate = metrics.get("match_rate", 0.0)
    verified_acc = metrics.get("verified_accuracy")
    verified_acc_str = f"{verified_acc:.1f}%" if verified_acc is not None else "N/A (Ground Truth Required)"
    throughput = metrics.get("throughput", 0.0)
    proc_time = LATEST_RECONCILIATION_BATCH.get("processing_time_seconds", 0.0) if LATEST_RECONCILIATION_BATCH else 0.0

    kpi_data = [
        [
            Paragraph("Total Records", cell_bold), Paragraph(str(total_recs), cell_style),
            Paragraph("Match Rate", cell_bold), Paragraph(f"{match_rate:.1f}%", cell_style)
        ],
        [
            Paragraph("Automatically Matched", cell_bold), Paragraph(str(matched), cell_style),
            Paragraph("Verified Accuracy", cell_bold), Paragraph(verified_acc_str, cell_style)
        ],
        [
            Paragraph("Needs Review", cell_bold), Paragraph(str(review), cell_style),
            Paragraph("System Throughput", cell_bold), Paragraph(f"{throughput} rec/sec", cell_style)
        ],
        [
            Paragraph("Exceptions Detected", cell_bold), Paragraph(str(exc_count), cell_style),
            Paragraph("Processing Time", cell_bold), Paragraph(f"{proc_time:.4f} sec", cell_style)
        ]
    ]

    kpi_table = Table(kpi_data, colWidths=[130, 140, 130, 140])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # 2. Exception Breakdown Section
    story.append(Paragraph("Exception Discrepancy Breakdown", h2_style))
    exc_breakdown = metrics.get("exception_breakdown", {})
    if exc_breakdown:
        exc_rows = [[Paragraph("Exception Type", cell_bold), Paragraph("Count", cell_bold)]]
        for exc_t, cnt in sorted(exc_breakdown.items(), key=lambda x: x[1], reverse=True):
            exc_rows.append([
                Paragraph(exc_t.replace("_", " ").title(), cell_style),
                Paragraph(str(cnt), cell_style)
            ])
        exc_table = Table(exc_rows, colWidths=[380, 160])
        exc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(exc_table)
    else:
        story.append(Paragraph("No active exceptions detected in latest run.", cell_style))

    story.append(Spacer(1, 12))

    # 3. Top Unresolved Exceptions Section
    story.append(Paragraph("Top Unresolved Exceptions", h2_style))
    unresolved = [e for e in exceptions if e.get("status") != "RESOLVED"][:8]
    if unresolved:
        unres_rows = [[
            Paragraph("Invoice ID", cell_bold),
            Paragraph("Type", cell_bold),
            Paragraph("Severity", cell_bold),
            Paragraph("Reason / Action", cell_bold)
        ]]
        for e in unresolved:
            inv_id = e.get("invoice_id", "")
            exc_t = e.get("exception_type", "").replace("_", " ")
            sev = e.get("severity", "")
            reason = e.get("reason", "")
            unres_rows.append([
                Paragraph(inv_id, cell_style),
                Paragraph(exc_t, cell_style),
                Paragraph(sev, cell_style),
                Paragraph(reason, cell_style)
            ])
        unres_table = Table(unres_rows, colWidths=[80, 110, 70, 280])
        unres_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(unres_table)
    else:
        story.append(Paragraph("All exceptions resolved or none detected.", cell_style))

    story.append(Spacer(1, 12))

    # 4. Audit Trail Summary Section
    story.append(Paragraph("Audit Trail Summary", h2_style))
    if audit_events:
        recent_audit = audit_events[:5]
        audit_rows = [[
            Paragraph("Timestamp", cell_bold),
            Paragraph("Invoice ID", cell_bold),
            Paragraph("Actor", cell_bold),
            Paragraph("Event Type", cell_bold),
            Paragraph("New State", cell_bold)
        ]]
        for a in recent_audit:
            ts = a.get("created_at", "")[:19].replace("T", " ")
            audit_rows.append([
                Paragraph(ts, cell_style),
                Paragraph(a.get("invoice_id", ""), cell_style),
                Paragraph(a.get("actor", ""), cell_style),
                Paragraph(a.get("event_type", ""), cell_style),
                Paragraph(a.get("new_state", ""), cell_style)
            ])
        audit_table = Table(audit_rows, colWidths=[110, 80, 100, 130, 120])
        audit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(audit_table)
    else:
        story.append(Paragraph("No human review audit actions recorded yet.", cell_style))

    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
