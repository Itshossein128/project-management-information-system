# Graph Report - building-management  (2026-11-03)

## Corpus Check
- 29 files · ~52,400 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 71 nodes · 110 edges · 11 communities (9 shown, 2 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.92)
- Token cost: 14,200 input · 6,800 output

## Community Hubs (Navigation)
- لجستیک مصالح، بچینگ و انبار شیراز
- راهبری و سند تثبیت قرارداد تحویل (R.0)
- راهبری و سند تثبیت قرارداد تحویل (R.0)
- برنامه زمان‌بندی و اکیپ‌های اجرایی شیراز
- گزارش‌های عملیاتی روزانه و ساب‌ریپورت‌ها
- راهبری و سند تثبیت قرارداد تحویل (R.0)
- لجستیک مصالح، بچینگ و انبار شیراز
- ممیزی‌های فنی، شکاف‌ها و ریسک‌های پلتفرم
- گزارش‌های عملیاتی روزانه و ساب‌ریپورت‌ها
- جامعه معنایی 9
- جامعه معنایی 10

## God Nodes (most connected - your core abstractions)
1. `برنامه تحویل ولورا — بازبینی دوم (نسخه ۲)` - 18 edges
2. `کاتالوگ داده‌ها و فیکسچرهای مرجع کارفرما` - 13 edges
3. `گزارش روزانه جامع کارگاهی شیراز (فایل ۴ با ۳۶۷ شیت)` - 13 edges
4. `فاز A.1: تطبیق و تحویل اولیه گزارش روزانه` - 7 edges
5. `سند تثبیت دامنه و قرارداد تحویل ولورا (R.0.01)` - 6 edges
6. `مرزهای مصوب دامنه (Scope Boundaries)` - 6 edges
7. `فاز A.7: ورود گروهی WBS و اطلاعات پایه` - 6 edges
8. `فاز A.8: عملیات، پیشرفت و تجمیع ساب‌ریپورت‌ها` - 6 edges
9. `کاتالوگ گزارش‌های استاندارد سیستم (FILE 4 & PDF)` - 5 edges
10. `فاز A.9: اسناد، نسخه‌ها و کارتابل تایید` - 5 edges

## Surprising Connections (you probably didn't know these)
- `مرزهای مصوب دامنه (Scope Boundaries)` --references--> `سرویس ورود زمان‌بندی MSP/P6 (msp_import.py)`  [EXTRACTED]
  docs/delivery/R0-scope-and-reports-contract.md → apps/api/core/schedule/services/msp_import.py
- `فاز A.10: داشبورد تجمیعی و گزارش‌های دوره‌ای` --implements--> `کامپوننت گزارش‌های دوره‌ای فرانت‌اند (PeriodReportsPanel.tsx)`  [EXTRACTED]
  output/delivery-plan-2026-11-03/delivery-plan.md → apps/web/src/components/progress/PeriodReportsPanel.tsx
- `مرزهای مصوب دامنه (Scope Boundaries)` --references--> `مدل نسخه‌بندی مدارک مهندسی (DocumentRevision)`  [EXTRACTED]
  docs/delivery/R0-scope-and-reports-contract.md → apps/api/core/documents/models.py
- `مرزهای مصوب دامنه (Scope Boundaries)` --references--> `مدل ذینفعان و ماتریس ارتباطات (Stakeholder & CommunicationPlan)`  [EXTRACTED]
  docs/delivery/R0-scope-and-reports-contract.md → apps/api/core/projects/models.py
- `مرزهای مصوب دامنه (Scope Boundaries)` --references--> `موتور گردش کار و کارتابل تاییدات (WorkflowInstance)`  [EXTRACTED]
  docs/delivery/R0-scope-and-reports-contract.md → apps/api/core/workflow/models.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **چرخه راهبری و گیت‌های تثبیت تحویل سامانه ولورا** — docs_delivery_r0_scope_and_reports_contract_contract, output_delivery_plan_2026_11_03_delivery_plan_plan_v2, output_delivery_plan_2026_11_03_reviewer_corrections_corrections, output_delivery_plan_2026_11_03_delivery_plan_phase_r0 [EXTRACTED 1.00]
- **اکوسیستم تجمیع داده‌های میدانی در گزارش روزانه شیراز (FILE 4)** — real_data_daily_report_shiraz_file4, real_data_batching_report_16, real_data_warehouse_daily_report_3, real_data_machinery_report_3, real_data_civil_execution_1, real_data_electrical_execution_1, real_data_mechanical_execution_1, apps_api_core_field_reports_shiraz_file4_excel [INFERRED 0.95]
- **زنجیره لجستیک مصالح، تولید بتن و تراز مصرف کارگاهی** — real_data_warehouse_daily_report_3, real_data_batching_report_16, real_data_materials_balance_report, apps_api_core_inventory_project_urls [INFERRED 0.85]
- **مدل شکست کار زمان‌بندی MSP و تخصیص اکیپ‌های نازک‌کاری و تاسیسات** — real_data_plan_mpp_schedule, real_data_plan_wbs_structure, real_data_plan_mep_finishes_blocks, real_data_plan_crews, apps_api_core_schedule_services_msp_import [INFERRED 0.95]

## Communities (11 total, 2 thin omitted)

### Community 0 - "لجستیک مصالح، بچینگ و انبار شیراز"
Cohesion: 0.18
Nodes (10): ماژول تولید PDF روزانه و واترمارک (pdf.py), موتور تجمیع گزارش روزانه (daily_report_aggregation.py), ماژول خروجی اکسل چندشیته شیراز (shiraz_file4_excel.py), مسیرهای کاردکس و تراز انبار (inventory/project_urls.py), سرویس ساب‌ریپورت‌های تخصصی کارگاه (unit_report_views.py), کامپوننت گزارش‌های دوره‌ای فرانت‌اند (PeriodReportsPanel.tsx), کاتالوگ گزارش‌های استاندارد سیستم (FILE 4 & PDF), فاز A.1: تطبیق و تحویل اولیه گزارش روزانه (+2 more)

### Community 1 - "راهبری و سند تثبیت قرارداد تحویل (R.0)"
Cohesion: 0.24
Nodes (12): صفحه ذینفعان پروژه (project-stakeholders.tsx), مدل ظرفیت مهندسی و تقویم پذیرش, فاز A.10: داشبورد تجمیعی و گزارش‌های دوره‌ای, فاز A.11: آزمون جامع، امنیت و سناریوی UAT, فاز A.12: استقرار، آموزش و تحویل نهایی, فاز A.3: فهرست ذینفعان و ماتریس ارتباطات, فاز A.4: مکاتبات، ارجاع داخلی و پیوست‌ها, فاز A.6: کاربران و مرز دسترسی (+4 more)

### Community 2 - "راهبری و سند تثبیت قرارداد تحویل (R.0)"
Cohesion: 0.36
Nodes (6): مدل نسخه‌بندی مدارک مهندسی (DocumentRevision), مدل ذینفعان و ماتریس ارتباطات (Stakeholder & CommunicationPlan), موتور گردش کار و کارتابل تاییدات (WorkflowInstance), سند تثبیت دامنه و قرارداد تحویل ولورا (R.0.01), فاز A.3.C: ارتباطات یکپارچه ذینفعان, فاز A.9: اسناد، نسخه‌ها و کارتابل تایید

### Community 3 - "برنامه زمان‌بندی و اکیپ‌های اجرایی شیراز"
Cohesion: 0.25
Nodes (8): سرویس ورود زمان‌بندی MSP/P6 (msp_import.py), صفحه پیمانکاران پروژه (project-subcontractors.tsx), فاز A.2: تکمیل مدیریت پیمانکاران, فاز A.7: ورود گروهی WBS و اطلاعات پایه, ساب‌ریپورت اجرای ابنیه شیراز (۴), سامانه ۱۷ اکیپ تخصصی اجرایی کارگاه شیراز, برنامه زمان‌بندی پروژه ۲۰۰۰ واحدی کمیل‌آباد شیراز (plan.mpp), ساختار WBS فونداسیون و اسکلت بتنی بلوک‌های ۲۴ واحدی

### Community 4 - "گزارش‌های عملیاتی روزانه و ساب‌ریپورت‌ها"
Cohesion: 0.33
Nodes (6): نمونه روزانه تفصیلی پروژه شیراز (نسخه ۷), گزارش روزانه جامع کارگاهی شیراز (فایل ۴ با ۳۶۷ شیت), بانک داده رابطه‌ای عملیات شیراز (بخش ۱), بانک داده عملیات شیراز (از ۱۴۰۴/۰۸/۰۱ به بعد), گزارش کارکرد و توقف ماشین‌آلات سنگین کارگاه (۳), گزارش گیت حراست و شیفت‌های حفاظتی شیراز (۳)

### Community 5 - "راهبری و سند تثبیت قرارداد تحویل (R.0)"
Cohesion: 0.40
Nodes (4): مدل‌های تراکنش نقدی و جریان نقدینگی (cash_flow), مدل‌های ساختار CBS و کنترل تعهدات مالی (cost_control), گزارش بازرسی مالی، قراردادها و جریان نقدی, فاز A.5: هزینه، پرداخت و جریان نقد

### Community 6 - "لجستیک مصالح، بچینگ و انبار شیراز"
Cohesion: 0.40
Nodes (5): گزارش ایستگاه بچینگ و تولید بتن شیراز (۱۶), ساب‌ریپورت اجرای ابنیه شیراز (۱), بانک داده عملیات شیراز (۱۴۰۴/۰۷/۰۱ تا ۱۴۰۴/۱۲/۰۸), گزارش تراز و بالانس مصالح پروژه شیراز, گزارش روزانه انبار مرکزی شیراز (ورود و خروج مصالح ۳)

### Community 8 - "گزارش‌های عملیاتی روزانه و ساب‌ریپورت‌ها"
Cohesion: 0.83
Nodes (4): کاتالوگ داده‌ها و فیکسچرهای مرجع کارفرما, فرم‌های تایید مرخصی پرسنل کارگاه شیراز, فرم درخواست اضافه‌کاری پرسنل شیراز, گزارش حضور و غیاب و گیت حراست شیراز

### Community 9 - "جامعه معنایی 9"
Cohesion: 0.50
Nodes (4): ساب‌ریپورت اجرای تاسیسات برقی (۱), ساب‌ریپورت اجرای تاسیسات برقی (۳), ساب‌ریپورت اجرای تاسیسات مکانیکی (۱), زمان‌بندی نازک‌کاری و تاسیسات جفت‌بلوک‌ها (۴۲-۴۳، ۳۸-۳۹، ۳۰-۳۱)

## Knowledge Gaps
- **19 isolated node(s):** `مدل ظرفیت مهندسی و تقویم پذیرش`, `مجموعه ۷۲ بسته کاری تحویل ولورا (Work Packages)`, `تقویم زمان‌بندی و گیت‌های پذیرش کارفرما`, `گزارش بازرسی مالی، قراردادها و جریان نقدی`, `سیاق دانش، تعاریف مفهومی و شواهد بازبینی ولورا` (+14 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 21 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `برنامه تحویل ولورا — بازبینی دوم (نسخه ۲)` connect `راهبری و سند تثبیت قرارداد تحویل (R.0)` to `لجستیک مصالح، بچینگ و انبار شیراز`, `راهبری و سند تثبیت قرارداد تحویل (R.0)`, `برنامه زمان‌بندی و اکیپ‌های اجرایی شیراز`, `راهبری و سند تثبیت قرارداد تحویل (R.0)`?**
  _High betweenness centrality (0.417) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `گزارش روزانه جامع کارگاهی شیراز (فایل ۴ با ۳۶۷ شیت)` (e.g. with `گزارش ایستگاه بچینگ و تولید بتن شیراز (۱۶)` and `ساب‌ریپورت اجرای ابنیه شیراز (۱)`) actually correct?**
  _`گزارش روزانه جامع کارگاهی شیراز (فایل ۴ با ۳۶۷ شیت)` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `مدل ظرفیت مهندسی و تقویم پذیرش`, `مجموعه ۷۲ بسته کاری تحویل ولورا (Work Packages)`, `تقویم زمان‌بندی و گیت‌های پذیرش کارفرما` to the rest of the system?**
  _19 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `فاز A.1: تطبیق و تحویل اولیه گزارش روزانه` connect `لجستیک مصالح، بچینگ و انبار شیراز` to `راهبری و سند تثبیت قرارداد تحویل (R.0)`, `برنامه زمان‌بندی و اکیپ‌های اجرایی شیراز`, `گزارش‌های عملیاتی روزانه و ساب‌ریپورت‌ها`?**
  _High betweenness centrality (0.225) - this node is a cross-community bridge._
- **Why does `گزارش روزانه جامع کارگاهی شیراز (فایل ۴ با ۳۶۷ شیت)` connect `گزارش‌های عملیاتی روزانه و ساب‌ریپورت‌ها` to `گزارش‌های عملیاتی روزانه و ساب‌ریپورت‌ها`, `لجستیک مصالح، بچینگ و انبار شیراز`, `لجستیک مصالح، بچینگ و انبار شیراز`, `جامعه معنایی 9`?**
  _High betweenness centrality (0.204) - this node is a cross-community bridge._