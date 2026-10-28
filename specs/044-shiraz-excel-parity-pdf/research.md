# Technical Research & Architecture Notes: Shiraz Excel Forms Parity & Official PDF Standardization

## 1. Overview & Context

This research documents implementation details, formula structures, typography, and API patterns needed to achieve 100% parity with the Shiraz National Housing (2,000-unit Komeil Abad project) reporting forms and official PDF documentation.

The implementation spans:
1. **Shiraz FILE 4 Daily Report Excel Generation** (`openpyxl` with RTL layout, Persian typography, 34 staff labor rows, 32 direct worker rows, materials, concrete volumes, machinery, and daily activities with native `=SUM(...)` formulas).
2. **Discipline Sub-Report Excel Exports** (`openpyxl`):
   - FILE 5 (Civil / Buildings): includes `قطعه` (parcel) and `درصد اجرا` with Excel percentage formatting `0.0%`.
   - FILE 6 (Electrical): includes block and floor, omitting parcel and percentage.
3. **Official PDF Standardization** (`reportlab`):
   - 3 formal signature blocks: Preparer (Site Supervisor), Reviewer (Technical Office), Approver (Project Manager / Resident Engineer).
   - Deterministic 16-character cryptographic Audit Hash (SHA-256) embedded in the approval signature block.
   - Semi-transparent diagonal draft watermark (`«پیش‌نویس — غیرقابل استناد رسمی (DRAFT)»`) on canvas for unapproved reports.
   - Standardized attachment filename: `daily-report-{report_date}-{shift}.pdf`.
4. **Frontend Multidimensional Filter Synchronization**:
   - URL search parameter bi-directional sync (`useSearchParams`) for `daily-reports-list.tsx` and `project-activity-log.tsx`.
   - Summary metric bar calculating total man-days and grouped unit quantities.
   - Master activity log Excel export matching Shiraz FILE 1 (`ACTIVITY` sheet).

---

## 2. openpyxl Layout & Formatting Patterns

### 2.1 RTL Orientation & Font Styling
To configure right-to-left layout in `openpyxl`:
```python
ws.sheet_view.rightToLeft = True
```
Font family: `Tahoma` or `Arial` (universally supported across Excel on Windows/macOS/Linux/LibreOffice with complete Persian glyph sets).
Header fill: `#1F4E79` or `#2E75B6` (Navy/Steel blue) with white bold text, or `#D9E1F2` for subheaders.
Borders: Thin light gray border (`#D3D3D3` or `#999999`) for all data cells to replicate clean construction grid lines.

```python
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

THIN_BORDER = Border(
    left=Side(style='thin', color='BFBFBF'),
    right=Side(style='thin', color='BFBFBF'),
    top=Side(style='thin', color='BFBFBF'),
    bottom=Side(style='thin', color='BFBFBF')
)
HEADER_FILL = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
HEADER_FONT = Font(name='Tahoma', size=10, bold=True, color='FFFFFF')
SUBHEADER_FILL = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
SUBHEADER_FONT = Font(name='Tahoma', size=9, bold=True, color='1F4E79')
REGULAR_FONT = Font(name='Tahoma', size=9)
BOLD_FONT = Font(name='Tahoma', size=9, bold=True)
ALIGN_CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
ALIGN_RIGHT = Alignment(horizontal='right', vertical='center', wrap_text=True)
```

### 2.2 Shiraz FILE 4 Layout & Formula Geometry
In Shiraz FILE 4:
- Rows 1–8: Unified project header (Project name, contract number, Jalali date, day of week, shift hours, workshop status, weather).
- Rows 10–50: Manpower Sections side-by-side or stacked:
  - Section A: Indirect Staff (34 fixed roles).
    - Subtotal formula: `=SUM(C11:C44)`
  - Section B: Direct Labor (32 fixed worker roles).
    - Subtotal formula: `=SUM(C47:C78)`
  - Grand Total: `=C45+C79` or `=SUM(C45,C79)`.
- Section C: Incoming Materials (`ردیف`, `شرح مصالح`, `مقدار`, `واحد`, `تأمین‌کننده`, `شماره بارنامه`).
- Section D: Concrete Volume (`ردیف`, `شرح بتن (عیار)`, `حجم (متر مکعب)`, `قطعه`, `بلوک`, `طبقه`, `موقعیت بتن‌ریزی`).
- Section E: Machinery & Equipment (`ردیف`, `دستگاه و تجهیزات`, `وضعیت`, `نوع مالکیت`, `ساعت کارکرد`, `ساعت تعمیرات`).
- Section F: Daily Activities Executed (`ردیف`, `شرح فعالیت`, `شیفت`, `پیمانکار`, `تعداد نفر`, `قطعه`, `بلوک`, `طبقه`, `واحد`, `مقدار`).

### 2.3 34 Indirect Staff Roles (Seeded in 0010_shiraz_labor_titles)
1. مدیرشعبه
2. معاونت فنی شعبه
3. سرپرست کنترل پروژه
4. کنترل کیفیت شعبه
5. مدیر مالی
6. تدارکات
7. مدیر پروژه
8. سرپرست کارگاه
9. معاونت کارگاه
10. سرپرست دفتر فنی
11. برنامه‌ریزی و کنترل پروژه
12. کارشناس دفتر فنی
13. سرپرست اجرا
14. کارشناس اجرا
15. حسابداری
16. واحد مکانیک
17. واحد برق
18. اداری و مالی
19. کارمند اداری
20. کنترل کیفیت
21. سرپرست ایمنی
22. کارشناس ایمنی
23. انباردار
24. نقشه‌بردار
25. نگهبان روز و شب
26. خدمات
27. تأسیسات
28. مسئول ماشین‌آلات
29. تکنسین اجرا
30. فناوری اطلاعات
31. سرپرست بچینگ
32. آزمایشگاه
33. مهمان
34. متفرقه ستادی

### 2.4 32 Direct Labor Roles (Seeded in 0010_shiraz_labor_titles)
1. کارگر ساده
2. کارگر ماهر
3. بنا
4. آرماتور بند و قالب بند
5. اکیپ بتن‌ریزی
6. جوشکار
7. اکیپ حفاری
8. سرویس‌کار
9. متفرقه (تعمیرکار-برق‌کار)
10. پیمانکار برق و تأسیسات
11. پلاستر کار
12. لوله‌کش تأسیسات
13. نصاب تاور
14. داربست‌بند
15. نیروی انسانی ماشین‌آلات
16. راننده بابکت
17. راننده کامیون
18. راننده لودر
19. راننده بیل مکانیکی
20. راننده تراک میکسر
21. راننده غلتک
22. راننده بیل بکهو
23. راننده جرثقیل
24. راننده تانکر آب
25. راننده گریدر
26. اپراتور پمپ بتن
27. اپراتور بچینگ
28. اپراتور باسکول
29. کنترل‌چی عملیات خاکی
30. راننده سواری
31. اپراتور دستگاه حفاری
32. اپراتور تاور

### 2.5 openpyxl Percentage Number Formatting
In openpyxl, native percentage format is applied using:
```python
cell.number_format = '0.0%'
```
When `execution_percentage` is given as a number (e.g., `45.5` for 45.5% or `0.455`), in Excel standard percentages represent 1.0 as 100%. Therefore, if `val` is stored as `45.5`, we write `val / 100.0` to the cell and format with `0.0%` so it displays as `45.5%`.

---

## 3. ReportLab Official PDF Export Architecture

### 3.1 Watermark Drawing via Canvas Callbacks
ReportLab's `SimpleDocTemplate.build(story, onFirstPage=..., onLaterPages=...)` allows decorating each page canvas prior to/after flowable layout.
To draw a semi-transparent diagonal watermark across the page center:
```python
def make_draft_watermark(font_name: str):
    def _draw(canvas, doc):
        canvas.saveState()
        canvas.setFont(font_name, 34)
        canvas.setFillColor(colors.Color(0.7, 0.7, 0.7, alpha=0.25))
        canvas.translate(doc.pagesize[0] / 2.0, doc.pagesize[1] / 2.0)
        canvas.rotate(45)
        # Persian text shaped
        canvas.drawCentredString(0, 0, _fa("پیش‌نویس — غیرقابل استناد رسمی (DRAFT)"))
        canvas.restoreState()
    return _draw
```
When `report.status == 'approved'`, this watermark function is omitted (`None`), ensuring clean official output.

### 3.2 Cryptographic Audit Hash Generation
The audit security fingerprint is computed as a SHA-256 digest over the immutable report identity, lineage, date, shift, status, and approval metadata:
```python
import hashlib

def generate_report_audit_hash(report) -> str:
    raw = (
        f"{report.id}:{report.lineage_id}:{report.report_date}:"
        f"{report.shift}:{report.status}:{report.approved_at}:"
        f"{report.approved_by_id}"
    )
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16].upper()
```

### 3.3 Three-Tier Digital Signature Block
A 3-column ReportLab Table at the end of the document:
1. **تنظیم‌کننده (سرپرست کارگاه)**: Submitter name, role, `submitted_at`.
2. **بررسی‌کننده (دفتر فنی)**: Reviewer name, role, `reviewed_at` (or "تأیید مستقیم بدون بررسی دفتر فنی" if skipped).
3. **تأییدکننده (مدیر پروژه / ناظر مقیم)**: Approver name, role, `approved_at`, and `کد رهگیری امنیتی: {hash}`.

```python
sig_data = [
    [
        _fa("تنظیم‌کننده (سرپرست کارگاه)"),
        _fa("بررسی‌کننده (دفتر فنی)"),
        _fa("تأییدکننده (مدیر پروژه / ناظر مقیم)"),
    ],
    [
        _fa(f"{preparer_name}\n{preparer_title}\n{submitted_time}"),
        _fa(f"{reviewer_name}\n{reviewer_title}\n{reviewed_time}"),
        _fa(f"{approver_name}\n{approver_title}\n{approved_time}\nکد امنیتی: {audit_hash}"),
    ]
]
```

---

## 4. Multi-Dimensional Filter URL Synchronization (`useSearchParams`)

In React Router 7 / React applications:
- Instead of keeping filter inputs purely in local component state (`useState`), filter state is synchronized with `useSearchParams()`:
  - On initial render: load query parameters from `searchParams` with default fallbacks.
  - On user change: invoke `setSearchParams(newParams, { replace: true })`.
  - Shareable links: copying the URL includes `?date_from=...&date_to=...&discipline=...&parcel=...&status=...`.
  - Back/Forward browser navigation works seamlessly.

---

## 5. Summary Metrics Aggregation & FILE 1 Export

### 5.1 Real-Time Aggregate Summary
In `project-activity-log.tsx`:
- Compute total man-days (`sum(headcount)`).
- Group executed quantities by measurement unit (`sum(quantity)` per `unit`): e.g., `متر مکعب: 420.5`, `کیلوگرم: 15,200`, `متر طول: 850`.
- Display in a summary card above the data table.

### 5.2 FILE 1 Excel Export
Endpoint: `GET /api/v1/projects/{project_pk}/activity-log/excel/`
- Replicates Shiraz FILE 1 (`ACTIVITY` sheet):
  - Columns: `ردیف`, `تاریخ`, `شرح فعالیت`, `شیفت`, `پیمانکار`, `نفرات`, `قطعه`, `بلوک`, `طبقه`, `موقعیت`, `مقدار`, `واحد`.
  - RTL worksheet orientation, Tahoma font, auto-width columns.
