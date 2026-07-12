# Excel Forms & Grids Documentation
## Shiraz Project (پروژه 2000 واحدی مسکن ملی کمیل‌آباد شیراز)
### Source Files Analysis — IPCAS Module Mapping

---

## Summary Table

| # | File | Persian Name | Module in IPCAS | Type |
|---|---|---|---|---|
| 1 | `data_base_shiraz__1_.xlsx` | بانک اطلاعاتی (فاز 1) | Daily Report + Resources | Master database |
| 2 | `data_base_shiraz_2_from_14040701_to_140401208.xlsx` | بانک اطلاعاتی (فاز 2 — دوره 1) | Daily Report + Resources | Master database |
| 3 | `data_base_shiraz_2_from_14040801_.xlsx` | بانک اطلاعاتی (فاز 2 — دوره 2) | Daily Report + Resources | Master database |
| 4 | `گزارش_روزانه_پروژه_2000_واحدی_کمیل_آباد_شیراز.xlsx` | گزارش روزانه کل پروژه | Daily Report | Input form |
| 5 | `اجرای_ابنیه_شیراز__1_.xlsx` | گزارش روزانه ابنیه | Daily Report — Civil | Discipline sub-report |
| 6 | `_اجرای_تاسیسات_برقی__1_.xlsx` | گزارش روزانه تأسیسات برقی | Daily Report — Electrical | Discipline sub-report |
| 7 | `گزارش_بالانس_مصالح_شیراز.xlsx` | بالانس مصالح | Materials & Warehouse | Inventory tracking |
| 8 | `فرم_درخواست_اضافه_کاری_شیراز.xlsx` | فرم اضافه‌کاری | Human Resources | Request form |
| 9 | `تایید_مرخصی_شیراز.xlsx` | تأیید مرخصی / مأموریت | Human Resources | Request form |

---

---

## FILE 1 — بانک اطلاعاتی فاز 1
**Filename:** `data_base_shiraz__1_.xlsx`
**Date range:** 1402/06/28 to ~1403/07/30
**Purpose:** Master project database for Phase 1. A single workbook aggregating all daily operational data across 9 sheets.

---

### Sheet 1: ACTIVITY (بانک اطلاعات فعالیت‌های روزانه)

**Purpose:** Cumulative log of every site activity performed since project start. This is the primary source of truth for physical progress.

**Columns:**

| Column | Persian Label | Type | Description |
|---|---|---|---|
| A | ردیف | Integer | Row number (sequential) |
| B | تاریخ | Date (Jalali) | Date the activity was performed |
| C | شرح فعالیت | Text | Description of the activity |
| D | شیفت | Text | Work shift (شیفت 1 / 2 / 3) |
| E | پیمانکار | Text | Subcontractor name or "نفر شرکت" for direct labor |
| F | نفرات | Integer | Number of workers on this activity |
| G | قطعه | Text | Site zone/lot (e.g. قطعه 10) |
| H | بلوک | Text | Block number (e.g. 32-33, 42-43) |
| I | طبقه | Text | Floor level |
| J | موقعیت | Text | Specific location within the floor |
| K | مقدار | Numeric / Text | Quantity executed (or * if not measured) |
| L | واحد | Text | Unit of measurement (متر مکعب، متر مربع، تن، عدد…) |

**Observed activity types:** survey work, rebar bending/cutting, formwork, concrete pouring, scaffolding, rebar installation, earthworks

**Notes for IPCAS:**
- Each row maps to one `daily_activities` record
- `پیمانکار` maps to `subcontractor` FK or "direct" flag
- `قطعه / بلوک / طبقه` maps to the `work_front` / location fields
- `مقدار = *` means the activity was performed but quantity was not measured — store as NULL with a boolean flag `quantity_measured = false`
- This sheet is the data source for the Physical Progress Control module

---

### Sheet 2: Sheet12 (کارکرد آقای خنکا)

**Purpose:** Individual subcontractor performance log — tracking all activities performed by the "Khanaka" subcontractor crew from project start.

**Columns:** Same structure as ACTIVITY sheet plus:

| Column | Persian Label | Type | Description |
|---|---|---|---|
| L | توضیحات | Text | Additional notes (e.g. "با جرثقیل 25" = using 25-ton crane) |

**Notes for IPCAS:**
- This sheet demonstrates the requirement for **per-subcontractor activity filtering**
- In IPCAS, this becomes a filtered view of `daily_activities` where `subcontractor = 'خنکا'`
- No separate table needed — it is a report query, not a distinct data source
- In Phase 2 databases this sheet is renamed to `Khaneka`

---

### Sheet 3: weather (وضعیت جوی)

**Purpose:** Daily weather log for the project site.

**Columns:**

| Column | Persian Label | Type | Description |
|---|---|---|---|
| A | تاریخ | Date (Jalali) | Date |
| B | روز | Text | Day of week |
| C | حداکثر دما | Numeric | Maximum temperature (°C) |
| D | حداقل دما | Numeric | Minimum temperature (°C) |
| E | وضعیت جوی | Text | Weather condition (آفتابی، ابری، بارانی، طوفانی، برفی) |
| F | وضعیت کارگاه | Text | Site activity status (فعال / غیرفعال) |

**Notes for IPCAS:**
- One row per calendar day (including weekends / holidays with `غیرفعال` status)
- Maps directly to the `weather` section of `daily_reports` model
- `وضعیت کارگاه = غیرفعال` means no report is expected for that day — useful for alert suppression ("missing daily report" alert should not fire on inactive days)
- Weather condition values should be an enum/dropdown in IPCAS

---

### Sheet 4: problems (موانع و مشکلات)

**Purpose:** Running log of site problems, barriers, and issues.

**Columns:**

| Column | Persian Label | Type | Description |
|---|---|---|---|
| A | موانع و مشکلات | Text | Description of the problem or barrier |
| B | تاریخ | Date (Jalali) | Date the issue was recorded |

**Sample data:**
- Drawing changes causing rework in excavation
- Generator engine failure (cylinder/head issue)
- Ground concrete pump hydraulic oil and fuel hose failures
- Payment delays causing masonry work to proceed with minimum crew

**Notes for IPCAS:**
- Maps to the `risk_events` table with `event_type = 'barrier'`
- The `responsible_party`, `severity`, and `corrective_action` fields are missing in the Excel — they need to be added in the IPCAS form
- These entries are currently free-text. IPCAS should provide a category dropdown (equipment failure / payment delay / design change / weather / subcontractor / other) to enable reporting

---

### Sheet 5: labor camp report (گزارش نفرات کمپ)

**Purpose:** Daily headcount report for the labor camp (residential connex units on site).

**Columns:**

| Column | Persian Label | Type | Description |
|---|---|---|---|
| A | تاریخ | Date (Jalali) | Date |
| B | شماره کانکس | Text | Connex unit number (کانکس شماره 1, 2, 3…) |
| C | تعداد افراد مستقر | Integer | Total residents in the connex |
| D | پیمانکار | Text | Subcontractor the residents belong to |
| E | تعداد افراد حاضر | Integer | Present headcount |
| F | تعداد افراد مرخصی | Integer | Workers on leave |
| G | ظرفیت کانکس | Integer | Maximum capacity of the connex |
| H | ظرفیت خالی کانکس | Integer | Empty/available slots |

**Notes for IPCAS:**
- This is a specialized sub-module of Human Resources
- Multiple rows per date (one per connex unit)
- Maps to a `labor_camp_report` table or can be a sub-section of the daily report
- Calculated field: `ظرفیت خالی = ظرفیت - تعداد مستقر` — compute this in the system, don't ask the user to enter it

---

### Sheet 6: personnel report (گزارش آماری نفرات)

**Purpose:** Daily staff count summary broken down by job category and shift.

**Columns:**

| Column | Persian Label | Type | Description |
|---|---|---|---|
| A | تاریخ | Date (Jalali) | Date |
| B | شرح | Text | Job category (e.g. نیروهای ستادی، راننده و اپراتور، حراست…) |
| C | نفرات شیفت 1 (7–17) | Integer | Headcount in shift 1 |
| D | نفرات شیفت 2 (18–24) | Integer | Headcount in shift 2 |
| E | نفرات شیفت 3 (1–6) | Integer | Headcount in shift 3 |

**Observed job categories:**
نیروهای ستادی، راننده و اپراتور، حراست، کارگر روزمزد شرکتی (and more)

**Notes for IPCAS:**
- This is a summary/aggregate view of `daily_labor` entries
- In IPCAS, this becomes an auto-generated report from the daily labor entries — not a separate manual input
- The three-shift structure is identical to the daily report form structure

---

### Sheet 7: MACHINE DATA BANK 1 (ماشین‌آلات و تجهیزات)

**Purpose:** Detailed daily equipment log — the master database of all equipment status and working hours.

**Columns:**

| Column | Persian Label | Type | Description |
|---|---|---|---|
| A | ردیف | Integer | Row number |
| B | تاریخ | Date (Jalali) | Date |
| C | عنوان | Text | Equipment name |
| D | شیفت روز — فعال | Boolean | Active in day shift |
| E | شیفت روز — آماده | Boolean | Standby in day shift |
| F | شیفت روز — خراب | Boolean | Broken down in day shift |
| G | نوع مالکیت — تملیکی | Boolean | Owned by company |
| H | نوع مالکیت — اجاره‌ای | Boolean | Rented |
| I | ساعت شروع کار | Time | Work start time |
| J | ساعت پایان کار | Time | Work end time |
| K | تعمیرات (ساعت) | Numeric | Repair/maintenance hours |
| L | کارکرد مفید | Numeric | Productive working hours |
| M | توضیحات | Text | Notes |

**Notes for IPCAS:**
- Maps to `daily_equipment` table
- `فعال / آماده / خراب` → `status` enum field
- `تملیکی / اجاره‌ای` → `ownership_type` field on the equipment master record
- Productive hours = (end time − start time) − repair hours. Validate this in IPCAS rather than making the user calculate it.

---

### Sheet 8: manpower (نیروی انسانی)

**Purpose:** Daily headcount per job title — a structured version of personnel report.

**Columns:**

| Column | Persian Label | Type | Description |
|---|---|---|---|
| A | تاریخ | Date (Jalali) | Date |
| B | عنوان شغلی | Text | Job title |
| C–D | (merged/empty) | — | Reserved columns |
| E | تعداد (نفر/روز) | Numeric | Headcount for that day |

**Observed job titles (34 listed):** مدیرشعبه، مدیر پروژه، سرپرست کارگاه، معاونت کارگاه، سرپرست دفتر فنی، برنامه‌ریزی و کنترل پروژه، کارشناس دفتر فنی، سرپرست اجرا، کارشناس اجرا، حسابداری، واحد مکانیک، واحد برق، اداری و مالی، کارمند اداری، تدارکات، کنترل کیفیت، سرپرست ایمنی و بهداشت، کارشناس ایمنی و بهداشت، انباردار، نقشه‌بردار، نگهبان، خدمات، تأسیسات، مسئول ماشین‌آلات، تکنسین اجرا، فناوری اطلاعات، سرپرست بچینگ، آزمایشگاه، مهمان

**Notes for IPCAS:**
- This becomes the `daily_labor` table, `labor_type = 'indirect'` (staff/overhead)
- The job title list is a fixed dropdown in the system — seed from this list
- One row per job title per day. In IPCAS this is entered as a grid inside the daily report form

---

### Sheet 9: mashinery (گزارش ماشین‌آلات)

**Purpose:** Summary equipment status table — a simpler view of the MACHINE DATA BANK.

**Columns:**

| Column | Persian Label | Type | Description |
|---|---|---|---|
| A | تاریخ | Date (Jalali) | Date |
| B | دستگاه و تجهیزات | Text | Equipment type name |
| C–E | (grouped sub-columns) | — | Count columns |
| F | کل | Integer | Total units on site |
| G | فعال | Integer | Active units |
| H | آماده به کار | Integer | Standby units |
| I | غیرفعال | Integer | Inactive units |
| J | در دست تعمیر | Integer | Under repair |

**Observed equipment types:** بچینگ 1.5 متری اتوماتیک، موتور سیکلت، جرثقیل تا 10 تن، خودرو مزدا-نیسان (and more)

**Notes for IPCAS:**
- This is a daily aggregated summary — auto-generated from `daily_equipment` entries
- One row per equipment type per day
- `کل = فعال + آماده + غیرفعال + در دست تعمیر` — always validate this constraint

---

---

## FILE 2 — بانک اطلاعاتی فاز 2 (دوره اول)
**Filename:** `data_base_shiraz_2_from_14040701_to_140401208.xlsx`
**Date range:** 1404/07/01 to 1404/12/08

## FILE 3 — بانک اطلاعاتی فاز 2 (دوره دوم)
**Filename:** `data_base_shiraz_2_from_14040801_.xlsx`
**Date range:** 1404/08/01 onwards

**Both files have identical sheet structure to File 1** with these differences:

| Item | Phase 1 (File 1) | Phase 2 (Files 2 & 3) |
|---|---|---|
| Sheet "Sheet12" | Named "Sheet12" | Renamed to "Khaneka" |
| ACTIVITY columns | 12 columns | Simplified — quantity/unit columns removed, shift moved to col K |
| Activity data | Structural/civil works dominant | Finishing works dominant (plastering, ceramics, MEP, Kknauf) |
| Weather data | Fully populated | Partially populated (some dates blank) |
| Problems sheet | Rich entries | Has entries but some dates are empty rows |

**Notes for IPCAS:**
- The three files together cover the full project timeline — they must all import into the same `daily_activities`, `daily_equipment`, and `daily_labor` tables
- The column structure difference in ACTIVITY between phases indicates the customer used evolving Excel templates. IPCAS must standardize this into a single consistent form
- The "Khaneka" sheet in Phase 2 is identical data structure to Phase 1 — confirmed as the same subcontractor tracking sheet

---

---

## FILE 4 — گزارش روزانه کل پروژه
**Filename:** `گزارش_روزانه_پروژه_2000_واحدی_کمیل_آباد_شیراز.xlsx`
**Date range:** 1403/11/14 to 1404/12/08 (330+ sheets)
**Structure:** One sheet per calendar day, each sheet is a full daily report form

This is the most important file — it defines the complete structure of the daily report that IPCAS must replicate as a digital form.

---

### Daily Report Form Structure (per sheet/day)

**Header Section (Rows 1–8):**

| Field | Value / Type | Notes |
|---|---|---|
| Project name | پروژه 2000 واحدی مسکن ملی کمیل آباد شیراز | Fixed for this project |
| Contract number | شماره قرارداد: 1402/25319/ص | Fixed |
| تاریخ | Date (Jalali) | Auto-populated from sheet name |
| روز | Day of week (فارسی) | Auto-calculated |
| Shift 1 hours | از 7 الی 17 | Configurable |
| Shift 2 hours | از 18 الی 24 | Configurable |
| Shift 3 hours | از 1 الی 6 | Configurable |
| وضعیت کارگاه | فعال / غیرفعال | Checkbox |
| شرایط جوی | طوفانی / برفی / بارانی / ابری / آفتابی | Checkbox group |

---

**Section A — Indirect Labor / Staff (نیروی انسانی غیرمستقیم — ستادی)**
Rows 14–58, left panel

| Column | Field | Type |
|---|---|---|
| ردیف | Row number | Integer (1–45) |
| عنوان شغلی | Job title | Text (fixed list, 34 items) |
| تعداد (نفر/روز) | Headcount | Integer |

Fixed job title list (34 items, same as File 1 Sheet 8 manpower):
مدیرشعبه، معاونت فنی شعبه، سرپرست کنترل پروژه، کنترل کیفیت شعبه، مدیر مالی، تدارکات، مدیر پروژه، سرپرست کارگاه، معاونت کارگاه، سرپرست دفتر فنی، برنامه‌ریزی و کنترل پروژه، کارشناس دفتر فنی، سرپرست اجرا، کارشناس اجرا، حسابداری، واحد مکانیک، واحد برق، اداری و مالی، کارمند اداری، تدارکات، کنترل کیفیت، سرپرست ایمنی، کارشناس ایمنی، انباردار، نقشه‌بردار، نگهبان روز و شب، خدمات، تأسیسات، مسئول ماشین‌آلات، تکنسین اجرا، فناوری اطلاعات، سرپرست بچینگ، آزمایشگاه، مهمان

**Subtotal row:** `جمع نیروی انسانی غیرمستقیم` — auto-calculated

---

**Section B — Direct Labor (نیروی انسانی مستقیم)**
Rows 14–58, center panel

| Column | Field | Type |
|---|---|---|
| ردیف | Row number | Integer (1–45) |
| عنوان شغلی | Labor type | Text (fixed list) |
| تعداد (نفر/روز) | Headcount | Integer |

Fixed labor type list (32 items):
کارگر ساده، کارگر ماهر، بنا، آرماتور بند و قالب بند، اکیپ بتن‌ریزی، جوشکار، اکیپ حفاری، سرویس‌کار، متفرقه (تعمیرکار-برق‌کار)، پیمانکار برق و تأسیسات، پلاستر کار، لوله‌کش تأسیسات، نصاب تاور، داربست‌بند، نیروی انسانی ماشین‌آلات، راننده بابکت، راننده کامیون، راننده لودر، راننده بیل مکانیکی، راننده تراک میکسر، راننده غلتک، راننده بیل بکهو، راننده جرثقیل، راننده تانکر آب، راننده گریدر، اپراتور پمپ بتن، اپراتور بچینگ، اپراتور باسکول، کنترل‌چی عملیات خاکی، راننده سواری، اپراتور دستگاه حفاری، اپراتور تاور

**Subtotal row:** `جمع نیروی انسانی مستقیم` — auto-calculated
**Grand total row:** `جمع کل نیروی انسانی` — sum of indirect + direct

---

**Section C — Incoming Materials (مصالح وارده)**
Rows 14–58, right panel

| Column | Field | Type |
|---|---|---|
| ردیف | Row number | Integer (1–20) |
| شرح مصالح | Material description | Text |
| (quantity and unit implied) | مقدار و واحد | Numeric + Text |

**Commonly recorded materials:** سیمان فله، ماسه شسته، شن بادامی، شن نخودی، مش تیپ 3، مش تیپ 1، تری دی پانل، آب غیر آشامیدنی

---

**Section D — Concrete Volume (حجم بتن ریخته شده)**
Rows 37–58, lower right panel

| Column | Field | Type |
|---|---|---|
| ردیف | Row number | Integer |
| شرح | Concrete type description | Text |
| مقدار | Volume (m³) | Numeric |

**Concrete types observed:** بتن عیار 450

---

**Section E — Daily Activities Executed (فعالیت‌های اجرا شده کارگاه)**
Rows 63 onwards

| Column | Field | Type |
|---|---|---|
| ردیف | Row number | Integer |
| شرح فعالیت | Activity description | Text |
| نوع شیفت کاری | Work shift | Dropdown (شیفت 1/2/3) |
| نام پیمانکار | Subcontractor name | Text |
| تعداد نفر | Worker count | Integer |
| قطعه | Zone/lot | Text |
| بلوک | Block | Text |
| طبقه | Floor | Text |

**Notes for IPCAS digital form:**
- This section is the most data-rich — typically 15–25 activities per day
- Each row maps to one `daily_activities` record
- The activity description is free-text but should be linkable to a WBS activity in IPCAS
- `نام پیمانکار` is free-text in Excel; in IPCAS it should be a FK to the subcontractors table
- The form should allow attaching site photos to individual activity rows

**IPCAS Implementation Notes — Complete Daily Report:**
- The daily report is a single-page form with 5 sections submitted once per day per site
- Recommended digital flow: each section can be saved independently (partial save), with final submit locking the form for approval
- The fixed job title lists (Section A & B) should be seeded from this document as system defaults
- Total headcount calculation (Section A + B) must be automatic
- The form must support RTL layout throughout

---

---

## FILE 5 — گزارش روزانه ابنیه (Civil Daily Sub-Report)
**Filename:** `اجرای_ابنیه_شیراز__1_.xlsx`
**Date range:** 1404/04/17 to 1404/12/08 (200+ sheets)
**Submitter:** Civil discipline supervisor (سرپرست ابنیه)
**Company:** شرکت پی‌چین

This is the **civil/structural discipline sub-report** — submitted separately from the main project daily report and focused only on civil execution activities.

---

### Civil Sub-Report Form Structure (per sheet/day)

**Header (Rows 1–4):**

| Field | Value | Notes |
|---|---|---|
| Company | شرکت پی‌چین | Contractor name |
| Report title | گزارش روزانه واحدهای اجرا | Fixed |
| Form code | کد فرم | Document control code |
| Revision number | شماره بازنگری | Version tracking |
| Project name | پروژه مسکن ملی کمیل آباد | Fixed |
| Discipline | اجرای ابنیه | Fixed (Civil) |
| Weather | وضعیت هوا | Text (آفتابی، ابری…) |
| Date | تاریخ | Date (Jalali) |
| Day of week | روز | Auto-calculated |

**Activity Log (Rows 6 onwards):**

| Column | Field | Type | Description |
|---|---|---|---|
| ردیف | Row number | Integer | Sequential |
| شیفت | Work shift | Text (شیفت1/2/3) | |
| نام | Crew name | Text | Subcontractor or "نفر شرکت" |
| استاد کار | Foreman count | Integer | Number of skilled masters |
| کارگر | Worker count | Integer | Number of laborers |
| قطعه | Zone/lot | Text | Site zone |
| بلوک | Block | Text | Block number |
| طبقه | Floor | Text | Floor level |
| شرح فعالیت | Activity description | Text | What was done |
| واحد | Unit | Text | Measurement unit |
| مقدار | Quantity | Numeric | Amount executed |
| درصد اجرا | Execution % | Numeric | Progress percentage for this activity |

**Observed civil activities:** اجرای دیوار داخلی کناف، اجرای سازه 3D پنل، آزمایشگاه و بچینگ، نصب وال‌پست جان‌پناه بام، جوشکاری، نصب قاب پنجره، نصب پله داربست، کمک نقشه‌بردار جابجایی نبشی رامکا

**Notes for IPCAS:**
- This is a **discipline sub-report** that feeds into the main daily report
- The `درصد اجرا` (execution percentage) column is unique to this file — not present in the main daily report. Include it in the IPCAS civil sub-report form.
- Submitter: site civil supervisor (role: `site_supervisor` with discipline = `civil`)
- After approval by civil supervisor, data feeds into the master `daily_activities` table
- The `استاد کار` (foreman count) and `کارگر` (laborer count) as separate columns is more granular than the main report — preserve both in the database
- This file confirms the **multi-discipline daily report** requirement: civil, electrical, and mechanical each submit their own sub-report that rolls up into one master daily report

---

---

## FILE 6 — گزارش روزانه تأسیسات برقی (Electrical Daily Sub-Report)
**Filename:** `_اجرای_تاسیسات_برقی__1_.xlsx`
**Date range:** 1404/03/10 to 1404/12/07 (200+ sheets)
**Submitter:** Electrical installations supervisor
**Company:** شرکت پی‌چین

This is the **electrical/MEP discipline sub-report** — identical structure to the civil sub-report but for electrical installations.

---

### Electrical Sub-Report Form Structure (per sheet/day)

**Header (Rows 1–4):** Same as civil sub-report, discipline = `اجرای تاسیسات برقی`

**Activity Log (Rows 6 onwards):**

| Column | Field | Type | Description |
|---|---|---|---|
| ردیف | Row number | Integer | Sequential |
| شیفت | Work shift | Integer (1/2/3) | Shift number |
| نام | Crew name | Text | Crew/sub name (e.g. رضایی) |
| استاد کار | Foreman count | Integer | |
| کارگر | Worker count | Integer | |
| بلوک | Block | Text | Block number (no قطعه column here) |
| طبقه | Floor | Text | Floor level |
| شرح فعالیت | Activity description | Text | |
| واحد | Unit | Text | (مورد، متر طول، عدد…) |
| مقدار | Quantity | Numeric | |

**Observed electrical activities:** رفع گرفتگی و تخریب بتن و اصلاح لوله، اجرای لوله‌کشی سقف، اجرای قوطی کلید و پریز، نصب کابل‌کشی، نصب تابلو برق، اجرای سینی کابل

**Key difference from civil sub-report:**
- No `قطعه` (zone) column — only `بلوک` and `طبقه`
- No `درصد اجرا` column
- Shift is recorded as an integer (1, 2, 3) not text

**Notes for IPCAS:**
- Same database table as civil activities — `daily_activities` with `discipline = 'electrical'`
- The absence of `قطعه` suggests electrical crews work across lots and only reference block numbers — make `قطعه` optional in the form
- Crew names like `رضایی` match subcontractor names in the main daily report — confirm FK linkage
- Units include `مورد` (item/case) which is equivalent to `عدد` — standardize in the unit master table

---

---

## FILE 7 — بالانس مصالح (Material Balance Report)
**Filename:** `گزارش_بالانس_مصالح_شیراز.xlsx`
**Sheets:** 6 sheets
**Purpose:** Material planning, request tracking, and consumption balance across all disciplines.

---

### Sheet 1: ثبت درخواست‌ها (Material Requests Register)

**Purpose:** Master list of all material requests — tracks estimated quantities vs multiple purchase requests over time.

**Columns:**

| Column | Field | Type | Description |
|---|---|---|---|
| ردیف | Row number | Integer | |
| شرح مصالح | Material name | Text | Material description |
| موقعیت | Location | Text | Where it's used (e.g. فونداسیون) |
| تیپ بلوک | Block type | Text | Block type (e.g. بلوک 40 واحدی) |
| مقدار برآورد شده | Estimated quantity | Numeric | |
| واحد | Unit | Text | |
| درخواست 1 — مقدار | Request 1 qty | Numeric | |
| درخواست 1 — واحد | Request 1 unit | Text | |
| درخواست 1 — تاریخ | Request 1 date | Date (Jalali) | |
| درخواست 2 — مقدار | Request 2 qty | Numeric | |
| درخواست 2 — واحد | Request 2 unit | Text | |
| درخواست 2 — تاریخ | Request 2 date | Date (Jalali) | |
| درخواست 3 … | Request 3 | Numeric/Text/Date | (pattern repeats) |

**Observed materials:** سیمان، شن نخودی، شن بادامی، ماسه شسته، آرماتور 10/12/14/16/18/25

**Notes for IPCAS:**
- Each row is one material in one location/block type
- The repeating request columns (درخواست 1, 2, 3…) are a normalized purchase request sequence
- In IPCAS this becomes: one `material` record + multiple `purchase_requests` linked to it
- This sheet is the source for the Procurement module's "Material Needs" view

---

### Sheet 2: ابنیه (Civil Material Balance)

**Purpose:** Full material balance for civil/structural works — estimated vs requested vs received vs consumed quantities, broken down by block.

**Columns:**

| Column | Field | Type | Description |
|---|---|---|---|
| ردیف | Row number | Integer | |
| تیپ بلوک | Block type | Text | (بلوک 20/24 واحدی) |
| شرح مصالح | Material name | Text | |
| موقعیت | Work position | Text | (e.g. فونداسیون، ستون، دیوار) |
| واحد | Unit | Text | |
| مقدار کل | Total estimated | Numeric | |
| مقدار یک بلوک | Qty per block | Numeric | |
| مقدار کل درخواست شده | Total requested | Numeric | |
| مقدار وارده | Total received | Numeric | |
| مقدار وارده به ازای یک بلوک | Received per block | Numeric | |
| مقدار خارج شده از انبار | Issued from warehouse | Numeric | |
| تجهیز کارگاه | Site setup column | (varies) | |
| قطعه 12 — بلوک 1, 2… | Per-block columns | Numeric | Consumption per block |

**Notes for IPCAS:**
- This is the core **Material Balance** view: Estimated → Requested → Received → Consumed
- Each column group maps to the `inventory_transactions` table
- The per-block breakdown confirms that material tracking is at the block level, not just site-wide
- The `مقدار یک بلوک` (per-block quantity) is the planning baseline — derived from the project BOQ
- Formula: `Balance = مقدار وارده − مقدار خارج شده از انبار`

---

### Sheets 3 & 4: برق and مکانیک (Electrical & Mechanical Material Balance)

**Purpose:** Same structure as ابنیه sheet but for electrical and mechanical materials respectively.

**Notes for IPCAS:**
- The material balance module must support filtering by discipline (civil / electrical / mechanical)
- The `discipline` field on `materials` or on the WBS linkage handles this

---

### Sheet 5: خلاصه مالی (Financial Summary)

**Purpose:** Financial summary of material costs — links quantity consumed to unit price to give total material expenditure.

**Notes for IPCAS:**
- This sheet connects the Material module to the Cost Control module
- Material cost = `مقدار خارج شده × نرخ واحد`
- In IPCAS this is computed automatically from `inventory_transactions.unit_cost`

---

### Sheet 6: لیست درخواست مصالح در ساختمان (In-Building Material Request List)

**Purpose:** Room-level material request list for final fit-out stage.

**Notes for IPCAS:**
- Sub-level of procurement — requests at residential unit level rather than block level
- Relevant when the project enters finishing/handover phase

---

**Overall Notes for IPCAS Material Module:**
- The balance formula across all sheets: `موجودی = وارده − خارج شده` — auto-compute, never manual entry
- Alert threshold: when `موجودی < حداقل مجاز` (minimum stock level), fire a materials shortage alert
- The three discipline sheets (civil, electrical, mechanical) should be tabs/filters in one unified material balance view

---

---

## FILE 8 — فرم درخواست اضافه‌کاری (Overtime Request Form)
**Filename:** `فرم_درخواست_اضافه_کاری_شیراز.xlsx`
**Sheet:** Form Responses 1 (Google Forms export)
**Purpose:** Overtime request and approval tracking for all project staff.

---

### Form Fields & Columns

| Column | Field | Type | Description |
|---|---|---|---|
| Timestamp | زمان ثبت | DateTime | Google Forms auto-timestamp |
| تاریخ ثبت درخواست | Request registration date | Date (Jalali) | When the form was submitted |
| واحد درخواست کننده | Requesting unit/department | Text | e.g. ماشین‌آلات، کنترل کیفیت، IT |
| نام و نام خانوادگی | Full name | Text | Employee requesting overtime |
| تاریخ درخواست | Overtime date | Date (Jalali) | The date overtime is requested for |
| ساعت شروع اضافه‌کاری | Start time | Time | Overtime start time |
| ساعت پایان اضافه‌کاری | End time | Time | Overtime end time |
| مدت اضافه‌کاری (ساعت) | Duration (hours) | Text/Time | Duration — note: mixed formats (text "3:00" and Time objects) |
| علت اضافه‌کاری | Reason for overtime | Text | Free text description |
| Email Address | Email | Email | Submitter's email |
| توضیحات مسئول مربوطه | Supervisor comments | Text | Optional notes from supervisor |
| تایید مسئول مربوطه | Supervisor approval | Text | "تایید" or blank |
| تایید مدیر مربوطه | Manager approval | Text | "تایید" or blank |
| مدت ساعت تأییدشده توسط مدیر | Approved hours by manager | Numeric | May differ from requested hours |

---

**Approval workflow observed:**
1. Employee submits via Google Form
2. `تایید مسئول مربوطه` — direct supervisor approves
3. `تایید مدیر مربوطه` — department manager approves (may reduce hours)
4. `مدت ساعت تأییدشده` — final approved duration (can be less than requested)

**Observed departments:** ماشین‌آلات، کنترل کیفیت، IT

**Data quality issues in the Excel:**
- `مدت اضافه‌کاری` has mixed formats — some as text ("3:00"), some as Time objects, some blank
- Start and end times sometimes blank even when duration is filled
- Some requests show manager approval without supervisor approval (approval chain skipped)

**Notes for IPCAS:**
- This maps to an `overtime_requests` table in the Human Resources module
- The approval workflow is: Draft → Supervisor Approved → Manager Approved → Finalized
- `مدت ساعت تأییدشده` may be different from `مدت اضافه‌کاری` — store both and flag discrepancies
- Requesting unit should be a FK to the department/unit master
- Employee name should be a FK to `users` table
- IPCAS should enforce: `start_time` and `end_time` are both required if duration is entered
- The "Email Address" column (Google Forms) is replaced by user authentication in IPCAS

**Database table: `overtime_requests`**

```
overtime_id       UUID PK
project_id        FK → projects
user_id           FK → users (requester)
department        FK → departments or VARCHAR
request_date      DATE (Jalali stored as Gregorian)
overtime_date     DATE
start_time        TIME nullable
end_time          TIME nullable
requested_hours   DECIMAL(5,2)
reason            TEXT
supervisor_id     FK → users nullable
supervisor_approved BOOLEAN nullable
supervisor_notes  TEXT nullable
manager_id        FK → users nullable
manager_approved  BOOLEAN nullable
approved_hours    DECIMAL(5,2) nullable
status            ENUM(draft, supervisor_approved, manager_approved, rejected)
created_at        TIMESTAMPTZ
```

---

---

## FILE 9 — تأیید مرخصی / مأموریت (Leave & Mission Approval Form)
**Filename:** `تایید_مرخصی_شیراز.xlsx`
**Sheet:** Form Responses 1 (Google Forms export)
**Purpose:** Leave request and mission assignment approval tracking.

---

### Form Fields & Columns

| Column | Field | Type | Description |
|---|---|---|---|
| Timestamp | زمان ثبت | DateTime | Google Forms auto-timestamp |
| تاریخ ثبت درخواست | Registration date | Date (Jalali) | |
| نوع درخواست | Request type | Text | ماموریت / ساعتی / روزانه |
| نام و نام خانوادگی درخواست کننده | Requester full name | Text | |
| واحد درخواست کننده | Requesting unit | Text | Department name |
| تاریخ درخواست | Request date | Date (Jalali) | Date of leave/mission |
| تاریخ / ساعت شروع | Start date/time | Mixed | Sometimes date+time together, sometimes just time |
| تاریخ / ساعت پایان | End date/time | Mixed | Same issue |
| همکار جایگزین | Replacement colleague | Text | Who covers while requester is away |
| موضوع مأموریت | Mission subject | Text | Free text (required for مأموریت type) |
| تایید مسئول مربوطه | Supervisor approval | Text | "تایید" or blank |
| تایید مدیر مربوطه | Manager approval | Text | "تایید" or blank |
| تایید حراست کارگاه | Site security approval | Text | "تایید" or blank (required for leaving site) |

---

**Request types observed:**
- `ماموریت` — Off-site mission/errand (requires mission subject and site security sign-off)
- `ساعتی` — Hourly leave (partial day)
- `روزانه` — Full day leave

**Three-level approval chain:**
1. `تایید مسئول مربوطه` — Direct supervisor
2. `تایید مدیر مربوطه` — Department manager
3. `تایید حراست کارگاه` — Site security (especially for missions leaving the site)

**Data quality issues:**
- Start/end date-time fields are inconsistently formatted: some show date+time concatenated (e.g. "09:00-1403/04/25"), some show only time, some show full date
- `همکار جایگزین` sometimes blank even for mission type
- Security approval often blank (appears optional in practice for short missions)

**Notes for IPCAS:**
- Maps to a `leave_requests` table in the Human Resources module
- `نوع درخواست` determines which fields are required: `ماموریت` requires `موضوع مأموریت`; `ساعتی` requires exact times
- `همکار جایگزین` should be a FK to `users` — a required field in IPCAS (currently unenforced in Excel)
- Site security approval (`تایید حراست کارگاه`) should be a separate approval step triggered only when request type = `ماموریت`
- Start and end should be separate date + time fields (not concatenated) in IPCAS to avoid the data quality issues seen here

**Database table: `leave_requests`**

```
leave_id              UUID PK
project_id            FK → projects
user_id               FK → users (requester)
department            FK → departments or VARCHAR
request_type          ENUM(mission, hourly, daily)
leave_date            DATE
start_datetime        TIMESTAMPTZ
end_datetime          TIMESTAMPTZ
replacement_user_id   FK → users nullable
mission_subject       TEXT nullable (required if type=mission)
supervisor_id         FK → users nullable
supervisor_approved   BOOLEAN nullable
manager_id            FK → users nullable
manager_approved      BOOLEAN nullable
security_approved     BOOLEAN nullable (required if type=mission)
status                ENUM(draft, supervisor_approved, manager_approved, security_approved, rejected, cancelled)
created_at            TIMESTAMPTZ
```

---

---

## Cross-File Relationships & IPCAS Module Mapping

```
                    ┌─────────────────────────┐
                    │   Daily Report (File 4)  │
                    │   Master Form per Day    │
                    └────────┬────────┬────────┘
                             │        │
              ┌──────────────▼──┐   ┌─▼──────────────┐
              │ Civil Sub-Report│   │Electrical Sub-  │
              │    (File 5)     │   │Report (File 6)  │
              └──────────────┬──┘   └─┬───────────────┘
                             │        │
                    ┌────────▼────────▼──────────┐
                    │   daily_activities table    │
                    │   daily_labor table         │
                    │   daily_equipment table     │
                    └─────────────────────────────┘
                             │
                    ┌────────▼─────────────────────┐
                    │   Database Files 1, 2, 3      │
                    │   (Aggregated master views)   │
                    └──────────────────────────────┘

┌──────────────────────────────┐   ┌──────────────────────────────┐
│  Material Balance (File 7)   │   │  HR Forms (Files 8 & 9)      │
│  → Materials & Warehouse     │   │  → Human Resources           │
│  → Procurement               │   │  overtime_requests            │
└──────────────────────────────┘   │  leave_requests               │
                                   └──────────────────────────────┘
```

---

## Sprint Implications

| Finding | Impact |
|---|---|
| Daily report has 34 fixed indirect job titles | Seed `labor_types` table from this list in Sprint 4 |
| Daily report has 32 fixed direct labor types | Same — seed in Sprint 4 |
| Civil and electrical sub-reports are separate files | Implement discipline sub-report in Sprint 4 (multi-discipline form) |
| `درصد اجرا` column only in civil sub-report | Add `execution_percentage` to `daily_activities` model |
| Leave has 3-level approval (supervisor + manager + security) | More complex than the 2-level approval in the daily report — plan for Sprint 4 or Sprint 10 (HR module) |
| Overtime approved hours may differ from requested | Store both `requested_hours` and `approved_hours` |
| All date data is Jalali | Confirm Jalali ↔ Gregorian conversion layer is in place before Sprint 4 |
| Material balance sheet has per-block breakdown | Material tracking is at block level — ensure `work_front` / block FK is on `inventory_transactions` |
| `مقدار = *` in activity log | Add `quantity_measured: Boolean` flag to `daily_activities` |
| Three database files cover different phases | Import wizard must handle column structure variation between Phase 1 and Phase 2 formats |
