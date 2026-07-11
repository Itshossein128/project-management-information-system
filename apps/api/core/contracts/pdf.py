"""ReportLab PDF export for IPC certificates."""

from __future__ import annotations

import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from common.jalali import gregorian_to_jalali
from field_reports.pdf import _fa, _register_font


def render_ipc_pdf(ipc) -> bytes:
    font = _register_font()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title = _fa(f'صدور موقت شماره {ipc.ipc_number}')
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 12))

    contract = ipc.contract
    meta = [
        [_fa('قرارداد'), _fa(contract.contract_number or '—')],
        [_fa('طرف مقابل'), _fa(contract.counterparty or '—')],
        [_fa('دوره'), _fa(f'{gregorian_to_jalali(ipc.period_start) or "—"} تا {gregorian_to_jalali(ipc.period_end) or "—"}')],
        [_fa('مبلغ ناخالص'), _fa(f'{float(ipc.gross_amount or 0):,.0f}')],
        [_fa('مبلغ خالص'), _fa(f'{float(ipc.net_amount or 0):,.0f}')],
        [_fa('وضعیت'), _fa(ipc.status)],
    ]
    t = Table(meta, colWidths=[120, 360])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, (0.7, 0.7, 0.7)),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    rows = [[_fa('شرح'), _fa('این دوره'), _fa('مبلغ')]]
    for item in ipc.items.filter(is_deleted=False):
        rows.append([
            _fa(item.description or '—'),
            _fa(str(item.qty_current)),
            _fa(f'{float(item.amount_current or 0):,.0f}'),
        ])
    if len(rows) > 1:
        items_table = Table(rows, colWidths=[240, 80, 160])
        items_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), font),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, (0.7, 0.7, 0.7)),
            ('BACKGROUND', (0, 0), (-1, 0), (0.9, 0.9, 0.9)),
        ]))
        story.append(items_table)

    doc.build(story)
    return buf.getvalue()
