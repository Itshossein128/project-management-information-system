# سند نهایی ارزیابی شکاف‌ها و تحلیل انطباق: انطباق با فرم‌های اکسل شیراز، خروجی PDF و فیلترهای گزارش‌گیری

**شناسه سند:** `GAP-SPEC-11-SHIRAZ-EXCEL-PARITY-PDF`  
**سند مشخصات فنی هدف:** [`SPEC-11-SHIRAZ-EXCEL-PARITY-PDF.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/atomic-specs/SPEC-11-SHIRAZ-EXCEL-PARITY-PDF.md)  
**اسناد مرجع همبسته:**  
- [`reports_documentation/01-core-requirements-and-excel-blueprints/مستندات فرم‌های اکسل شیراز (Shiraz Excel Forms Documentation).md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/01-core-requirements-and-excel-blueprints/مستندات%20فرم‌های%20اکسل%20شیراز%20(Shiraz%20Excel%20Forms%20Documentation).md)  
- [`reports_documentation/03-daily-field-reports-and-apis/field_reports_ENDPOINTS.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/03-daily-field-reports-and-apis/field_reports_ENDPOINTS.md)  
- [`apps/api/core/field_reports/models.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/models.py)  
- [`apps/api/core/field_reports/pdf.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/pdf.py)  
- [`apps/api/core/field_reports/daily_report_views.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py)  
- [`apps/api/core/sub_reports/models.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/models.py)  
- [`apps/api/core/sub_reports/unit_report_views.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/unit_report_views.py)  
- [`apps/web/src/app/routes/daily-reports-list.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/daily-reports-list.tsx)  
- [`apps/web/src/app/routes/daily-report-view.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/daily-report-view.tsx)  
- [`apps/web/src/app/routes/project-activity-log.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/project-activity-log.tsx)  
- [`apps/web/src/components/department/unit-daily-report-panel.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/department/unit-daily-report-panel.tsx)  
- [`docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-daily-reports]/`](file:///home/hossein/Desktop/projects/building-management/docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-daily-reports]/)  
**تاریخ ارزیابی:** ۶ آبان ۱۴۰۵ (2026-10-28)  
**وضعیت کلی انطباق:** ⚠️ **دارای شکاف‌های بحرانی و نیازمند پیاده‌سازی اکسل شیراز و استانداردسازی PDF (Fail - Action Required)**

---

## ۱. خلاصه‌ی اجرایی و تحلیل انطباق (Executive Summary)

سند مشخصات فنی اتمیک **`SPEC-11-SHIRAZ-EXCEL-PARITY-PDF`** ناظر بر انطباق صد در صدی ساختار گزارش‌دهی پروژه با فرم‌های کارگاهی اکسل پروژه ۲۰۰۰ واحدی مسکن ملی کمیل‌آباد شیراز (شامل شیت اصلی گزارش روزانه کل **FILE 4**، ساب‌ریپورت ابنیه **FILE 5**، ساب‌ریپورت تأسیسات الکتریکی **FILE 6** و دیتابیس جامع فعالیت‌ها **FILE 1**)، تولید گزارش رسمی چاپی و PDF در ابعاد استاندارد با الصاق سه کادر امضای دیجیتال و هش امنیتی ممیزی (Audit Hash)، واترمارک پیش‌نویس، نام‌گذاری یکپارچه فایل‌ها، و همچنین فیلترهای چندبعدی گزارش‌گیری با ماندگاری کامل در URL مرورگر (`useSearchParams`) می‌باشد.

ارزیابی عمیق فنی و موشکافانه کدهای جاری سامانه نشان می‌دهد که اگرچه مدل‌های داده‌ای پایه در `field_reports` و `sub_reports` فیلدهای لازم را نگهداری می‌کنند، اما در لایه خروجی‌ها و صادرات اطلاعات (Exports)، فرمت‌بندی رسمی، و تجربه کاربری گزارش‌گیری، **۵ شکاف اصلی و بحرانی** وجود دارد:

1. **فقدان کامل خروجی اکسل گزارش روزانه کل کارگاه (FILE 4 Daily Report Excel Generation - G01):**  
   در سراسر پکیج `field_reports`، هیچ متد یا تولیدکننده فایلی بر مبنای `openpyxl` وجود ندارد. هیچ اندپوینتی برای دریافت اکسل گزارش روزانه (`GET /api/v1/projects/{pk}/daily-reports/{id}/excel/`) پیاده‌سازی نشده است. شیت مادر FILE 4 شیراز (شامل هدر جوی و شیفت، جدول پرسنل ستادی ۳۴ ردیفه با فرمول جمع، جدول کارگری ۳۲ ردیفه با فرمول جمع، جدول مصالح وارده، جدول بتن‌ریزی، جدول وضعیت ماشین‌آلات و جدول فعالیت‌های روزانه در ساختار راست‌به‌چپ RTL) کلاً در سیستم غایب است.
2. **فقدان خروجی اکسل و انطباق ساب‌ریپورت‌های ابنیه و تأسیسات برقی (FILE 5 & FILE 6 Parity - G02):**  
   در ماژول `sub_reports`، با اینکه مدل `DisciplineSubReportActivity` ستون‌هایی نظیر `foreman_count`، `worker_count` و `execution_percentage` را داراست، هیچ متد یا اندپوینتی برای استخراج فایل اکسل اختصاصی ابنیه (FILE 5) با فرمت‌بندی درصد (`0.0%`) و ستون‌های قطعه/بلوک/طبقه یا اکسل تأسیسات الکتریکی (FILE 6) بدون قطعه و درصد وجود ندارد و دکمه‌های مربوطه در فرانت‌اند تعبیه نشده‌اند.
3. **نقص ساختاری خروجی PDF، فقدان کادرهای سه‌گانه امضای دیجیتال، هش امنیتی، نام استاندارد و واترمارک (Official PDF Export Deficiencies - G03):**  
   فایل `field_reports/pdf.py`:
   - فاقد ۳ بلوک رسمی امضای انتهای گزارش است: ۱. تنظیم‌کننده (سرپرست کارگاه)، ۲. بررسی‌کننده (دفتر فنی)، ۳. تأییدکننده (مدیر پروژه / ناظر مقیم).
   - هیچ شناسه یکتای امنیتی (Audit Fingerprint / SHA-256 Hash) یا ثبت دقیق زمان تأیید را در بدنه سند درج نمی‌کند.
   - نام فایل تولیدی به جای الگوی الزام‌شده در سناریوی ۱ (`daily-report-{report_date}-{shift}.pdf`) با فرمت غیراستاندارد `report_{jalali}.pdf` ساخته می‌شود.
   - گزارش‌های تاییدنشده و پیش‌نویس بدون واترمارک امنیتی («پیش‌نویس / غیررسمی») خروجی داده می‌شوند که ریسک سوءاستفاده سندی دارد.
4. **فقدان همگام‌سازی فیلترها با URL و نقص فیلترهای چندبعدی (Multi-dimensional Filtering & URL State Persistence - G04):**  
   - در نمای فهرست گزارش‌های روزانه (`daily-reports-list.tsx`)، فیلترها در `useState` موضعی نگهداری می‌شوند و با `useSearchParams` سینک نیستند. همچنین فیلترهای پیمانکار، دیسیپلین، و بلوک/زون در این صفحه تعبیه نشده‌اند.
   - در صفحه دیتابیس جامع فعالیت‌ها (`project-activity-log.tsx` منطبق بر FILE 1)، تمامی فیلترها در `useState` ذخیره شده و با بارگذاری مجدد یا کپی آدرس از بین می‌روند. علاوه بر این، خروجی اکسل این دیتابیس و ردیف جمع مقادیر و متراژ در فرانت‌اند پیاده نشده است.
5. **عدم پوشش درخت تصمیم‌گیری (Decision Tree Synchronization - G05):**  
   در مستندات `docs/decision-tree/`، تصمیم‌های دانلود اکسل FILE 4، ساب‌ریپورت‌های ابنیه و برق، تایید اعتبار امضای دیجیتال و فیلترهای دارای ماندگاری آدرس درج نشده‌اند.

---

### جدول ماتریس ارزیابی انطباق سناریوها

| شناسه سناریو | شرح در سند مشخصات فنی (SPEC-11) | وضعیت انطباق | علت و شواهد در کد موجود |
| :--- | :--- | :---: | :--- |
| **US-EX-01 (سناریو ۱)** | انطباق چیدمان و سکشن‌های جدول اکسل FILE 4 با ۳۴ ردیف ستادی، ۳۲ ردیف کارگری، ماشین‌آلات، مصالح و فعالیت‌ها | ❌ شکاف بحرانی (P1) | هیچ فایل یا کدی برای تولید اکسل روزانه کل در `field_reports` وجود ندارد؛ اندپوینت اکسل تعریف نشده است. |
| **US-EX-01 (سناریو ۲)** | ترازبندی راست‌به‌چپ (RTL)، تایپوگرافی استاندارد فارسی و فرمول‌های بومی جمع در اکسل | ❌ شکاف بحرانی (P1) | به دلیل فقدان کامل ماژول اکسل گزارش روزانه، این سناریو به کلی محقق نشده است. |
| **US-EX-02 (سناریو ۱)** | خروجی اکسل ساب‌ریپورت ابنیه (FILE 5) شامل شرح فعالیت، قطعه، بلوک، طبقه، استادکار، کارگر و ستون درصد اجرا (`0.0%`) | ❌ شکاف بحرانی (P1) | ماژول `sub_reports` فاقد اکسپورت اکسل است؛ دکمه اکسل در پنل ساب‌ریپورت وجود ندارد. |
| **US-EX-02 (سناریو ۲)** | خروجی اکسل ساب‌ریپورت تأسیسات برقی (FILE 6) منطبق بر ساختار شیراز (بدون قطعه و بدون درصد اجرا) | ❌ شکاف بحرانی (P1) | هیچ اندپوینت یا تابعی برای استخراج اکسل ساب‌ریپورت برق پیاده‌سازی نشده است. |
| **US-EX-03 (سناریو ۱)** | دانلود PDF رسمی با نام استاندارد `daily-report-{date}-{shift}.pdf` و هدر `application/pdf` | ⚠️ انطباق ناقص (P2) | اندپوینت PDF وجود دارد اما نام فایل `report_{jalali}.pdf` است و با استاندارد اسپک مطابقت ندارد. |
| **US-EX-03 (سناریو ۲)** | الصاق کادرهای ۳ گانه امضای دیجیتال (تنظیم‌کننده، بررسی‌کننده، تأییدکننده) با تاریخ/ساعت دقیق و هش امنیتی (Audit Hash) | ❌ شکاف بحرانی (P1) | در `field_reports/pdf.py` هیچ کادر امضایی در انتهای سند رسم نمی‌شود و هش ممیزی تولید نمی‌گردد. |
| **US-EX-04 (سناریو ۱)** | فیلتر ترکیبی چندبعدی فعالیت‌ها (دیسیپلین، پیمانکار، بازه زمانی، لوکیشن) همراه با جمع متراژ و احجام | ⚠️ انطباق ناقص (P2) | بک‌اند `ActivityLogView` فیلترها را دارد اما فرانت‌اند فاقد جمع احجام و متراژهای دوره‌ای است. |
| **US-EX-04 (سناریو ۲)** | ذخیره و بازیابی کلیه فیلترهای گزارش در URL مرورگر (`useSearchParams`) جهت اشتراک‌گذاری مستقیم لینک | ❌ شکاف بحرانی (P1) | هر دو صفحه `daily-reports-list.tsx` و `project-activity-log.tsx` از `useState` استفاده کرده و پارامترها در URL ذخیره نمی‌شوند. |

---

## ۲. یافته‌های تفصیلی و شواهد کد (Detailed Findings & Code Evidence)

### G01 — P1 — عدم وجود خروجی اکسل گزارش روزانه کل کارگاه منطبق بر تمپلیت FILE 4 شیراز
**مرجع در SPEC-11 (داستان US-EX-01، سناریوهای ۱ و ۲):**
> «فرمت خروجی گزارش روزانه کل سیستم از نظر جانمایی جدول‌ها، فونت فارسی، هدرها و عناوین شغلی دقیقاً منطبق بر شیت استاندارد FILE 4 شیراز باشد... جدول هدر در بالا (تاریخ شمسی، شیفت، وضعیت جوی)، بلوک نیروی انسانی با ۳۴ ردیف ستادی در سمت راست و ۳۲ ردیف کارگری در سمت چپ، بلوک ماشین‌آلات در زیر آن و جدول فعالیت‌های اجرایی در بخش اصلی قرار داشته باشد... جهت شیت راست به چپ (`right-to-left = true`) و فونت کلیه اعداد فارسی باشد.»

**شواهد در کد جاری:**
1. بررسی کنترلر گزارش‌های روزانه [`apps/api/core/field_reports/daily_report_views.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L421-L432):
   ```python
   @extend_schema(summary='Export report as PDF', tags=['Daily Reports'])
   @action(detail=True, methods=['get'])
   def pdf(self, request, *args, **kwargs):
       ...
   ```
   تنها اکشن صادراتی موجود `pdf` است؛ هیچ اکشن `excel` یا `xlsx` برای کلاس `DailyReportViewSet` تعریف نشده است.
2. بررسی فایل‌های پکیج [`apps/api/core/field_reports/`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/):
   هیچ فایلی برای بیلدر اکسل (نظیر `excel.py` یا `shiraz_file4_export.py`) وجود ندارد. دستور جستجوی `openpyxl` در دایرکتوری `field_reports` صفر نتیجه برمی‌گرداند.
3. در فرانت‌اند [`apps/web/src/app/routes/daily-report-view.tsx:243-252`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/daily-report-view.tsx#L243-L252):
   تنها دکمه «خروجی PDF» تعبیه شده و هیچ سازوکاری برای «خروجی اکسل (FILE 4)» تعریف نشده است.

**تحلیل نقص فنی:**
- پروژه ۲۰۰۰ واحدی شیراز دارای ۳۳۰+ شیت تاریخی با فرمت دقیق و شناخته‌شده است. ناظران مقیم، مشاور و دفتر فنی کارفرما صورت‌جلسات روزانه را صرفاً با این شیت تایید می‌کنند.
- ساختار ۳۴ عنوان شغلی نیروی انسانی غیرمستقیم (مدیرشعبه، معاونت فنی، سرپرست کارگاه، دفتر فنی، کنترل پروژه، ایمنی، آزمایشگاه، بچینگ و ...) و ۳۲ عنوان شغلی نیروی مستقیم (کارگر ساده، ماهر، بنا، آرماتوربند، اکیپ بتن‌ریزی، جوشکار، رانندگان ماشین‌آلات و ...) قبلاً در مایگریشن `0010_shiraz_labor_titles.py` به عنوان رکورد اولیه ذخیره شده‌اند، اما در خروجی اکسل به عنوان سطر‌های ثابت جدول با مقادیر و فرمول‌های `=SUM(...)` ظاهر نمی‌شوند.
- بخش‌های ۵ گانه تمپلیت FILE 4 (هدر، نیروی انسانی A/B، مصالح وارده C، بتن‌ریزی D، ماشین‌آلات E و لاگ فعالیت‌ها F) باید به طور کامل توسط یک سرویس اختصاصی با کتابخانه `openpyxl` طراحی و پیاده‌سازی شوند.

---

### G02 — P1 — فقدان خروجی اکسل ساب‌ریپورت‌های ابنیه (FILE 5) و برق (FILE 6)
**مرجع در SPEC-11 (داستان US-EX-02، سناریوهای ۱ و ۲):**
> «بتوانم خروجی اکسل و نمای چاپی ساب‌ریپورت اختصاصی واحدم را منطبق بر شیت‌های تفکیک‌شده شیراز (FILE 5 برای ابنیه و FILE 6 برای برق) چاپ کنم... در ابنیه فیلدهای شرح فعالیت، بلوک، طبقه، قطعه، استادکار، کارگر، واحد، مقدار و ستون درصد اجرا با فرمت درصد در اکسل تعبیه شده باشند... در برق ستون‌های شرح کارهای تأسیسات الکتریکی با تعداد سیم‌کش و شاگرد و احجام با واحد متر و عدد درج شده باشند (بدون قطعه و درصد اجرا).»

**شواهد در کد جاری:**
1. در مدل [`DisciplineSubReportActivity`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/models.py#L231-L253)، فیلدهای مورد نیاز وجود دارند:
   - `crew_name`, `foreman_count`, `worker_count`, `zone`, `parcel`, `block`, `floor`, `activity_description`, `unit`, `quantity`, `execution_percentage`.
2. اما در کنترلر [`DisciplineSubReportViewSet`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/unit_report_views.py#L195-L260):
   هیچ اکشنی برای `excel` یا `export` وجود ندارد. متدهای موجود فقط شامل `history`, `correct`, `submit`, `approve`, `reject` هستند.
3. در کامپوننت فرانت‌اند [`apps/web/src/components/department/unit-daily-report-panel.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/department/unit-daily-report-panel.tsx):
   هیچ دکمه‌ای برای دریافت گزارش اکسل ساب‌ریپورت دپارتمان وجود ندارد. سرپرستان ابنیه و برق نمی‌توانند سند روزانه تأییدشده خود را در قالب اکسل رسمی دریافت یا آرشیو کنند.

**تحلیل نقص فنی:**
- طبق مستندات شیراز، فرم FILE 5 متعلق به سرپرست ابنیه و فرم FILE 6 متعلق به سرپرست تأسیسات برقی است. تفاوت کلیدی این دو فرم در شیت‌های شیراز این است که FILE 5 دارای ستون «قطعه» (Zone/Parcel) و ستون حیاتی «درصد اجرا» (`execution_percentage`) با فرمت عددی درصد (`0.0%`) است، در حالی که FILE 6 ستون قطعه و درصد اجرا ندارد و روی متراژ لوله‌گذاری/سیم‌کشی و تعداد قوطی/تابلو تمرکز دارد.
- این تمایزات باید در دو قالب استاندارد اکسل به تفکیک دیسیپلین با هدر شرکتی (شرکت پی‌چین / مسکن ملی) و خروجی RTL پیاده‌سازی شوند.

---

### G03 — P1 — نقص خروجی چاپی و PDF رسمی، فقدان بلوک ۳ امضای دیجیتال و هش ممیزی
**مرجع در SPEC-11 (داستان US-EX-03، سناریوهای ۱ و ۲):**
> «پاسخ با هدر `Content-Type: application/pdf` و نام فایل استاندارد `daily-report-{date}-{shift}.pdf` ارسال شود... سه کادر مجزا شامل «تنظیم‌کننده (سرپرست کارگاه)»، «بررسی‌کننده (دفتر فنی)» و «تأییدکننده (مدیر پروژه / ناظر مقیم)» همراه با نام کاربر، تاریخ و ساعت دقیق تأیید و شناسه یکتای امنیتی (Audit Hash) درج شده باشد.»

**شواهد در کد جاری ([`apps/api/core/field_reports/pdf.py:76-224`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/pdf.py#L76-L224)):**
1. **نام فایل ارسالی:**
   در خط ۲۲۲:
   ```python
   filename = f'report_{jalali.replace("/", "-") or report.id}.pdf'
   ```
   در حالی که استاندارد اسپک صریحاً `daily-report-{report_date}-{shift}.pdf` (مانند `daily-report-1403-11-14-full.pdf` یا با تاریخ ایزو `daily-report-2025-02-02-full.pdf`) را تعیین کرده است. همچنین در فرانت‌اند `daily-report-view.tsx:150` به صورت هاردکد `daily-report-${reportId}.pdf` نام‌گذاری شده است!
2. **فقدان کادرهای امضای دیجیتال در انتهای سند:**
   در تابع `generate_daily_report_pdf`، گزارش پس از بخش حوادث و توضیحات کلی مستقیماً با `doc.build(story)` ساخته می‌شود و هیچ تابلوی امضایی در انتهای صفحه درج نمی‌شود. در حالی که مدل `DailyReport` دارای فیلدهای زیر است:
   - `prepared_by` / `submitted_by` + `submitted_at`
   - `reviewed_by` + `reviewed_at`
   - `approved_by` + `approved_at`
3. **عدم تولید و درج شناسه امنیتی (Audit Fingerprint / SHA-256):**
   هیچ رشته هش برای اعتبارسنجی اصالت گزارش محاسبه و در PDF چاپ نمی‌شود.
4. **فقدان واترمارک برای گزارش‌های پیش‌نویس / غیر مصوب:**
   چنانچه گزارش هنوز به وضعیت `approved` نرسیده باشد (در وضعیت `draft`، `submitted` یا `under_review` باشد)، بدون هیچ علامت مشخصه‌ای چاپ می‌شود که خلاف اصول اسناد کارگاهی است. باید یک واترمارک مورب کم‌رنگ («پیش‌نویس — غیرقابل استناد» یا «DRAFT») در پس‌زمینه صفحات درج شود.

---

### G04 — P2 — فیلترهای چندبعدی و عدم همگام‌سازی وضعیت در URL جهت اشتراک‌گذاری
**مرجع در SPEC-11 (داستان US-EX-04، سناریوهای ۱ و ۲):**
> «امکان فیلتر بر اساس ترکیب چندبعدی (بازه زمانی، پیمانکار، کد WBS، وضعیت تایید، دیسیپلین و محل مصرف)... ذخیره فیلتر در URL جهت اشتراک‌گذاری: با کپی و باز کردن لینک در تبی دیگر، دقیقاً همان فیلترها بازیابی و نمایش داده شوند.»

**شواهد در کد جاری:**
1. در صفحه فهرست گزارش‌های روزانه [`apps/web/src/app/routes/daily-reports-list.tsx:87-90`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/daily-reports-list.tsx#L87-L90):
   ```tsx
   const [filters, setFilters] = useState<DailyReportListParams>({
     page: 1,
     per_page: 20,
   });
   ```
   فیلترها کاملاً در حافظه موضعی ری‌اکت قرار دارند. در صورت رفرش صفحه یا ارسال لینک به مدیر پروژه، فیلترها به حالت اولیه برمی‌گردند. همچنین فیلترهای مهم نظیر پیمانکار، دیسیپلین، و محل کاربری اصلاً در این صفحه وجود ندارند.
2. در صفحه لاگ جامع فعالیت‌ها [`apps/web/src/app/routes/project-activity-log.tsx:37-46`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/project-activity-log.tsx#L37-L46):
   ```tsx
   const [dateRange, setDateRange] = useState({
     from: monthStartIso(),
     to: todayIso(),
   });
   const [discipline, setDiscipline] = useState<string[]>([]);
   const [parcel, setParcel] = useState<string[]>([]);
   const [zone, setZone] = useState("");
   const [block, setBlock] = useState("");
   const [subcontractor, setSubcontractor] = useState("");
   const [page, setPage] = useState(1);
   ```
   تمام فیلترها با `useState` پیاده شده‌اند و هیچ ارتباطی با `useSearchParams` ندارند. همچنین این جدول که نمای نرم‌افزاری شیت **FILE 1 (ACTIVITY)** است، فاقد دکمه دانلود اکسل (خروجی دیتابیس تخت فعالیت‌ها) و فاقد ردیف جمع مقادیر و احجام اجرایی (سناریوی ۱ اسپک) است.

---

### G05 — P2 — نقص همگام‌سازی درخت تصمیم‌گیری (Decision Tree)
**مرجع:** دستورالعمل قوانین مخزن در `.agents/rules/decision-tree.md` و ساختار موجود در `docs/decision-tree/`.

**شواهد در مستندات جاری:**
1. در دایرکتوری `docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-daily-reports]/[view-report]/`:
   تنها نود `[export-report-pdf]` موجود است.
   - هیچ نودی برای `[export-report-excel]` (دانلود اکسل فرمت FILE 4) وجود ندارد.
   - نود `[export-report-pdf]` نیز فاقد اشاره به شرایط امضای دیجیتال و هش ممیزی است.
2. در دایرکتوری‌های ساب‌ریپورت دپارتمان‌ها:
   هیچ نودی برای دانلود اکسل ساب‌ریپورت‌های تفکیک‌شده ابنیه (FILE 5) و برق (FILE 6) ثبت نشده است.
3. در نود `filter-and-change-view`:
   توضیحات مربوط به ذخیره و همگام‌سازی پارامترهای فیلتر در URL (`useSearchParams`) و به اشتراک‌گذاری آدرس وجود ندارد.

---

### G06 — P2 — فقدان آزمون‌های خودکار یکپارچه (Integration & Unit Tests)
**شواهد در کد جاری:**
- تست‌های فعلی `field_reports/tests/test_daily_report_crud.py` صرفاً ایجاد و ویرایش فیلدهای اصلی گزارش را می‌سنجند.
- هیچ تستی برای توابع تولید اکسل روزانه، انطباق با ۳۴ عنوان ستادی و ۳۲ عنوان کارگری، فرمول‌های جمع اکسل، خروجی‌های ساب‌ریپورت‌های FILE 5 و FILE 6، واترمارک و امضاهای PDF نوشته نشده است.
- در فرانت‌اند هیچ تستی برای اعتبارسنجی سینک شدن پارامترهای جستجو با URL مرورگر وجود ندارد.

---

## ۳. ماتریس تفصیلی نیازمندی‌ها و سناریوهای بازسازی (Requirements & Remediation Matrix)

| کد شکاف | عنوان شکاف فنی | مؤلفه درگیر | اولویت | اقدام اصلاحی دقیق و راهکار فنی |
| :---: | :--- | :--- | :---: | :--- |
| **G01** | فقدان اکسل گزارش روزانه کل کارگاه (FILE 4) | بک‌اند (`field_reports`) | **P1** | ایجاد سرویس `shiraz_file4_excel.py` با استفاده از `openpyxl` شامل سکشن‌های هدر، پرسنل ستادی (۳۴ ردیف)، پرسنل کارگری (۳۲ ردیف)، مصالح، بتن، ماشین‌آلات و فعالیت‌ها همراه با فرمول‌های `=SUM(...)`، حالت RTL، و تعریف اندپوینت `GET .../daily-reports/{id}/excel/`. |
| **G02** | فقدان اکسل ساب‌ریپورت‌های ابنیه و برق (FILE 5/6) | بک‌اند (`sub_reports`) و فرانت‌اند | **P1** | ایجاد سرویس‌های تولید اکسل اختصاصی ابنیه (شامل درصد اجرا و قطعه با استایل `0.0%`) و برق (بدون درصد و قطعه)، تعریف اندپوینت `GET .../sub-reports/{id}/excel/` و افزودن دکمه‌های دانلود به `unit-daily-report-panel.tsx`. |
| **G03** | نقایص PDF رسمی (امضاها، هش ممیزی، واترمارک، نام) | بک‌اند (`field_reports/pdf.py`) | **P1** | افزودن بلوک ۳ کادر امضای رسمی در انتهای PDF با متادیتای تایید، محاسبه و درج کد هش امنیتی SHA-256، اعمال واترمارک مورب «پیش‌نویس» در گزارش‌های غیرمصوب، و اصلاح نام فایل به `daily-report-{report_date}-{shift}.pdf`. |
| **G04** | فیلترهای چندبعدی و سینک نبودن URL | فرانت‌اند (`daily-reports-list`, `project-activity-log`) | **P2** | جایگزینی `useState` با هوک `useSearchParams` در صفحات لیست گزارش‌ها و لاگ فعالیت‌ها، افزودن دکمه دانلود اکسل لاگ فعالیت‌ها (FILE 1)، و درج ردیف جمع کل مقادیر و متراژ در فرانت‌اند. |
| **G05** | به‌روزرسانی درخت تصمیم‌گیری | مستندات `docs/decision-tree/` | **P2** | افزودن نودهای `[export-report-excel]` و `[export-sub-report-excel]`، به‌روزرسانی نود `[export-report-pdf]` با مشخصات امضا و هش امنیتی، و مستندسازی اشتراک لینک‌های فیلترشده. |
| **G06** | پوشش تست‌های خودکار | تست‌های بک‌اند و فرانت‌اند | **P2** | نگارش تست‌های جامع pytest برای اعتبارسنجی ساختار ورک‌بوک اکسل، فرمول‌های جمع، محتوای متنی PDF، واترمارک، و صحت پارامترهای URL. |

---

## ۴. طرح معماری ماژول‌ها و تغییرات پیشنهادی (Architectural Design & File Changes)

### الف. معماری تولید اکسل FILE 4 شیراز (`field_reports/shiraz_file4_excel.py`)
سرویس تولید فایل باید یک ورک‌بوک با مشخصات زیر بسازد:
1. **جهت و استایل شیت:**
   `ws.sheet_view.rightToLeft = True`، قلم فارسی (Vazirmatn یا Arial)، بردرهای نازک استاندارد برای سلول‌ها و پس‌زمینه رنگی تمایزبخش برای هدرها.
2. **بلوک سربرگ (Rows 1–8):**
   - سلول ادغام‌شده نام پروژه و شماره قرارداد
   - تاریخ شمسی و روز هفته
   - شیفت‌های کاری (شیفت ۱، ۲، ۳)
   - وضعیت کارگاه (فعال/تعطیل با دلیل) و شرایط جوی (آفتابی، بارانی و ...) همراه با دمای کمینه و بیشینه
3. **سکشن A — نیروی انسانی ستادی (غیرمستقیم):**
   - ۳۴ ردیف استاندارد شیراز: از «مدیرشعبه» تا «مهمان».
   - درج مقادیر ثبت‌شده در دیتابیس برای شیفت‌های ۱ تا ۳ و ستون جمع ردیف با فرمول `=SUM(...)`.
   - سطر سرجمع پایانی: `جمع نیروی انسانی غیرمستقیم` با فرمول جمع ستونی.
4. **سکشن B — نیروی انسانی مستقیم (کارگری):**
   - ۳۲ ردیف استاندارد شیراز: از «کارگر ساده»، «بنا»، «آرماتوربند» تا «اپراتور تاور».
   - سطر سرجمع: `جمع نیروی انسانی مستقیم`.
   - سطر سرجمع کل: `جمع کل نیروی انسانی` با فرمول جمع دو زیرمجموعه ستادی و کارگری.
5. **سکشن C — مصالح وارده کارگاه:**
   - جدول شرح مصالح، واحد، مقدار ورودی، تأمین‌کننده و شماره بارنامه.
6. **سکشن D — حجم بتن‌ریزی:**
   - جدول شرح بتن (عیار)، حجم به مترمکعب، قطعه، بلوک، طبقه و قطعه بتن‌ریزی‌شده همراه با جمع حجم.
7. **سکشن E — ماشین‌آلات و تجهیزات:**
   - دستگاه، وضعیت (فعال، آماده‌به‌کار، خراب)، نوع مالکیت، ساعات کارکرد و تعمیرات.
8. **سکشن F — فعالیت‌های اجرایی روز:**
   - جدول ردیف، شرح فعالیت، شیفت، نام پیمانکار، تعداد نفر، زون/قطعه، بلوک، طبقه، واحد، مقدار انجام‌شده.

### ب. معماری امضای دیجیتال و واترمارک در PDF (`field_reports/pdf.py`)
1. **الگوریتم تولید هش امنیتی (Audit Hash):**
   ```python
   def generate_report_audit_hash(report) -> str:
       raw = f"{report.id}:{report.lineage_id}:{report.report_date}:{report.shift}:{report.status}:{report.approved_at}:{report.approved_by_id}"
       return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16].upper()
   ```
2. **بلوک ۳ امضای انتهای سند:**
   جدولی ۳ ستونه در انتهای سند شامل:
   - ستون ۱: **تنظیم‌کننده (سرپرست کارگاه):** نام کاربر `prepared_by` / `submitted_by`، نقش، تاریخ و ساعت ثبت (`submitted_at`).
   - ستون ۲: **بررسی‌کننده (دفتر فنی):** نام کاربر `reviewed_by`، تاریخ و ساعت بررسی (`reviewed_at`).
   - ستون ۳: **تأییدکننده (مدیر پروژه / ناظر مقیم):** نام کاربر `approved_by`، تاریخ و ساعت تایید نهایی (`approved_at`) و کد ممیزی یکتا (`Audit Hash: XXXXXXXX`).
3. **واترمارک پیش‌نویس:**
   در صورتی که `report.status != ReportStatus.APPROVED` باشد، با استفاده از متد `onFirstPage` و `onLaterPages` روی کنواس ReportLab، متن کم‌رنگ خاکستری با زاویه ۴۵ درجه در مرکز صفحه رسم شود:
   `«پیش‌نویس — غیرقابل استناد رسمی (DRAFT)»`.

### ج. همگام‌سازی فیلترها با URL در فرانت‌اند
1. در `daily-reports-list.tsx`:
   استفاده از `useSearchParams` برای مدیریت همزمان `date_from`, `date_to`, `status`, `discipline`, `contractor` به طوری که تمام تغییرات فیلترها مستقیماً به عنوان کوئری استرینگ در URL ست شده و در بارگذاری مجدد بازیابی گردند.
2. در `project-activity-log.tsx`:
   اتصال متغیرهای فیلتر بازه زمانی، دیسیپلین، قطعه، زون، بلوک و پیمانکار به `useSearchParams`.
   افزودن دکمه «خروجی اکسل (FILE 1)» جهت دریافت کل رکوردهای فیلترشده با فرمت اکسل.
   افزودن نوار خلاصه احجام و نفرات در بالای جدول.

---

## ۵. نقشه راه اجرا و اولویت‌بندی (Implementation Roadmap)

1. **فاز ۱ (بک‌اند - اکسل روزانه FILE 4 و اندپوینت آن):**
   - پیاده‌سازی `apps/api/core/field_reports/shiraz_file4_excel.py`.
   - اضافه کردن اکشن `excel` به `DailyReportViewSet` در `daily_report_views.py`.
   - تست‌های جامع برای تایید درستی فرمول‌ها و استایل‌ها.
2. **فاز ۲ (بک‌اند - ساب‌ریپورت‌های ابنیه FILE 5 و برق FILE 6):**
   - پیاده‌سازی اکسپورت اختصاصی ابنیه با ستون درصد اجرا و قطعه.
   - پیاده‌سازی اکسپورت برق با ستون‌های استاندارد شیراز.
   - ایجاد اکشن اکسپورت در `unit_report_views.py`.
3. **فاز ۳ (بک‌اند - استانداردسازی PDF، امضاهای سه‌گانه، هش امنیتی و واترمارک):**
   - بازنویسی انتهای `field_reports/pdf.py` و افزودن جدول امضاهای سه‌گانه.
   - الصاق شناسه امنیتی هش و واترمارک برای گزارش‌های تاییدنشده.
   - تصحیح نام فایل خروجی طبق استاندارد `daily-report-{report_date}-{shift}.pdf`.
4. **فاز ۴ (فرانت‌اند - دکمه‌های خروجی و فیلترهای ماندگار در URL):**
   - افزودن دکمه دانلود اکسل در `daily-report-view.tsx` و `unit-daily-report-panel.tsx`.
   - بازنویسی فیلترها در `daily-reports-list.tsx` و `project-activity-log.tsx` با `useSearchParams`.
   - تعبیه دکمه دانلود اکسل و خلاصه احجام در `project-activity-log.tsx`.
5. **فاز ۵ (مستندات و درخت تصمیم‌گیری):**
   - ایجاد و به‌روزرسانی نودهای مربوطه در `docs/decision-tree/`.
   - تست کامل رگرسیون با pytest.
