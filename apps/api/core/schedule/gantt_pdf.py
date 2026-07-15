"""Landscape PDF table export for Gantt schedule."""

from __future__ import annotations

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from common.jalali import gregorian_to_jalali
from field_reports.pdf import _fa, _register_font
from projects.models import Project


def render_gantt_pdf(project_id, gantt_data: dict) -> bytes:
    font = _register_font()
    project = Project.objects.get(pk=project_id)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(_fa(f'گantt — {project.project_name}'), styles['Title']),
        Paragraph(_fa(f'خط مبنا: {gantt_data.get("baseline_name") or "—"}'), styles['Normal']),
        Spacer(1, 12),
    ]

    rows = [[_fa(h) for h in ['کد WBS', 'فعالیت', 'شروع', 'پایان', 'پیشرفت', 'وضعیت']]]
    for task in gantt_data.get('tasks', []):
        start_j = gregorian_to_jalali(task['start']) if task.get('start') else '—'
        end_j = gregorian_to_jalali(task['end']) if task.get('end') else '—'
        rows.append([
            _fa(task.get('wbs_code', '')),
            _fa(task.get('name', '')),
            _fa(start_j or '—'),
            _fa(end_j or '—'),
            _fa(f"{task.get('progress', 0)}%"),
            _fa(task.get('status', '')),
        ])

    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
    ]))
    story.append(table)
    doc.build(story)
    return buf.getvalue()
