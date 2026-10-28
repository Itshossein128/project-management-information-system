# سند نهایی ارزیابی شکاف‌ها و تحلیل انطباق: تولید خودکار گزارشات دوره‌ای و ردپای ارقام

**شناسه سند:** `GAP-SPEC-08-PERIODIC-REPORTS-ROLLUP`  
**سند مشخصات فنی هدف:** [`SPEC-08-PERIODIC-REPORTS-ROLLUP.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/atomic-specs/SPEC-08-PERIODIC-REPORTS-ROLLUP.md)  
**اسناد مرجع همبسته:**  
- [`docs/.../08-پیشرفت فیزیکی و گزارش‌های دوره‌ای.md`](file:///home/hossein/Desktop/projects/building-management/docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/08-پیشرفت%20فیزیکی%20و%20گزارش‌های%20دوره‌ای.md)  
- [`reports_documentation/04-.../schedule_and_progress_ENDPOINTS.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/04-periodic-weekly-monthly-reports/schedule_and_progress_ENDPOINTS.md)  
- [`specs/009-physical-progress-periodic-reports/spec.md`](file:///home/hossein/Desktop/projects/building-management/specs/009-physical-progress-periodic-reports/spec.md)  
- [`specs/009-physical-progress-periodic-reports/data-model.md`](file:///home/hossein/Desktop/projects/building-management/specs/009-physical-progress-periodic-reports/data-model.md)  
**تاریخ ارزیابی:** ۶ آبان ۱۴۰۵ (2026-10-28)  
**دامنه ارزیابی:**  
- بک‌اند:  
  - سرویس و مدل‌های گزارش دوره‌ای: [`apps/api/core/schedule/models.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/models.py)، [`apps/api/core/schedule/services/period_report_service.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/period_report_service.py)  
  - کنترلرها و اندپوینت‌ها: [`apps/api/core/schedule/period_report_views.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/period_report_views.py)، [`apps/api/core/schedule/urls.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/urls.py)  
  - مدل‌های گزارش روزانه کارگاه: [`apps/api/core/field_reports/models.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/models.py)  
  - تست‌های گزارش دوره‌ای: [`apps/api/core/schedule/tests/test_period_reports.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/tests/test_period_reports.py)  
- فرانت‌اند:  
  - پنل گزارشات دوره‌ای: [`apps/web/src/components/progress/PeriodReportsPanel.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/progress/PeriodReportsPanel.tsx)  
  - توابع ارتباطی API: [`apps/web/src/app/lib/api/progress.ts`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/api/progress.ts)  
  - صفحه پیشرفت پروژه: [`apps/web/src/app/routes/project-progress.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/project-progress.tsx)  
**وضعیت کلی سند:** ⚠️ **دارای شکاف‌های انطباق بحرانی و فقدان زنجیره تجمیع داده‌های روزانه (Fail - Action Required)**

---

## ۱. خلاصه‌ی اجرایی و تحلیل انطباق (Executive Summary)

سند مشخصات فنی اتمیک **`SPEC-08-PERIODIC-REPORTS-ROLLUP`** الزامات مهندسی سامانه Velora را برای تولید خودکار گزارشات دوره‌ای (هفتگی و ماهانه) پروژه، تضمین قابلیت ردیابی هر رقم مندرج در گزارش به رکوردهای منبع گزارش‌های روزانه کارگاه (Figure Provenance)، غیرقابل تغییر بودن ارقام نهایی (Immutability) و فرآیند تحت کنترل بازنویسی ارقام (Figure Override) با حفظ سوابق ممیزی تبیین می‌نماید. این سند شامل ۴ داستان کاربری اتمیک است:
1. **US-PR-04:** تولید خودکار گزارش هفتگی کارگاه از رکوردهای روزانه تأییدشده شامل سکشن‌های پنج‌گانه الزامی و استثنا کردن گزارش‌های روزانه پیش‌نویس (`draft`) همراه با اخطار در هدر گزارش.
2. **US-PR-05:** تولید خودکار گزارش ماهانه جامع وضعیت پروژه شامل فصول استاندارد (پیشرفت فیزیکی، مالی و جریان نقدینگی، ایمنی و کنترل کیفیت، تحلیل انحرافات SPI/CPI) و ثبت نسخه نهایی با کد سریال یکتا.
3. **US-PR-06:** ثبت و استعلام ردپای ارقام (Figure Provenance) به تفکیک رکوردهای روزانه تشکیل‌دهنده عدد و ممانعت از حذف فیزیکی رکوردهای مبنا در دیتابیس (Protected Foreign Key).
4. **US-PR-07:** فرآیند ممیزی و بازنویسی کنترل‌شده ارقام (Figure Override) با الزام ثبت دلیل حداقل ۱۰ کاراکتری، حفظ مقدار محاسبه‌شده اولیه (`calculated_value`) و درج علامت ستاره (*) و پانویس در خروجی.

بررسی جامع و عمیق کدهای پیاده‌سازی‌شده در بک‌اند و فرانت‌اند نشان می‌دهد که اگرچه اسکلت ابتدایی مدل‌های `ProjectPeriodReport`، `PeriodReportFigure` و `PeriodReportFigureOverride` در ماژول `schedule` پیاده‌سازی شده است، اما **شکاف‌های بنیادین و خلأهای کارکردی بزرگی** وجود دارد که امکان استقرار عملیاتی این سیستم را ناممکن می‌سازد:

1. **انفصال کامل سرویس گزارش دوره‌ای از گزارش‌های روزانه کارگاه (فقدان کامل تجمیع میدانی):**  
   سرویس جاری [`period_report_service.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/period_report_service.py) حتی یک خط کوئری یا ارتباط با مدل‌های گزارش روزانه کارگاه (`field_reports`) ندارد! نه جدول تجمیعی نفر-ساعت نیروی انسانی و ماشین‌آلات تولید می‌شود، نه احجام مصالح وارده و مصرفی تجمیع می‌گردد و نه فعالیت‌های تکمیل‌شده در طول هفته استخراج می‌شوند. گزارش هفتگی فعلی صرفاً داده‌های زمان‌بندی و ریسک را کپی می‌کند و فاقد آمار کارگاهی است.
2. **عدم اعتبارسنجی گزارش‌های پیش‌نویس روزانه و فقدان سازوکار درج هشدار در هدر:**  
   سیستم هیچ بررسی روی روزهای بازه انجام نمی‌دهد که آیا گزارش روزانه‌ای در وضعیت `draft` مانده است یا خیر. هیچ فیلد یا هدر هشداری (`warnings`) برای گزارش صادر نشده و هشدار «گزارش روز X تأیید نشده است» هرگز درج نمی‌شود.
3. **فقدان مدل ریز ردپای ارقام (Figure Provenance Breakdown) و کلید خارجی محافظت‌شده (Protected FK):**  
   مدل `PeriodReportFigure` دارای فیلد `source_id` به عنوان یک UUID آزاد و بدون کلید خارجی است. هیچ رابطه‌ای با رکوردهای تشکیل‌دهنده (چند منبع به ازای یک عدد تجمیعی) وجود ندارد؛ بنابراین اندپوینت جزئیات رقم (`GET .../figures/{figure_id}/`) نمی‌تواند سهم تفکیکی روزها و کاربران ثبت‌کننده/تأییدکننده را ارائه دهد. همچنین هیچ قید یکپارچگی ارجاعی (`on_delete=models.PROTECT`) وجود ندارد و کاربر می‌تواند رکوردهای گزارش روزانه مبنا را بدون خطا حذف کند.
4. **نقض قانون اعتبارسنجی طول دلیل بازنویسی (کمتر از ۱۰ کاراکتر):**  
   طبق سناریوی ۱ از US-PR-07، متن دلیل بازنویسی باید حداقل ۱۰ کاراکتر باشد. در بک‌اند و فرانت‌اند صرفاً شرط خالی نبودن چک می‌شود؛ در نتیجه دلایل بی‌معنی ۱ یا ۲ حرفی (مانند `'x'`) بدون خطا پذیرفته می‌شوند.
5. **تحریف مقدار محاسبه‌شده اولیه (`calculated_value`) در مدل رقم:**  
   در جدول `PeriodReportFigure` فیلد مجزایی برای `calculated_value` وجود ندارد و متد بازنویسی مستقیماً فیلد اصلی `value` را اوررایت می‌کند. همچنین در رابط کاربری هیچ ستاره (*) و پانویسی برای ارقام بازنویسی‌شده نمایش داده نمی‌شود.
6. **خلأ فصول HSE و QC، شاخص CPI و نبود فرآیند تصویب با شماره سریال یکتا در گزارش ماهانه:**  
   فصل حوادث کارگاهی و بازرسی‌های کنترل کیفیت در گزارش ماهانه غایب است؛ شاخص CPI در کنار SPI محاسبه نمی‌شود؛ و مدل گزارش فاقد وضعیت تصویب (`approved`/`final`) و شماره سریال رسمی است.
7. **محاسبه بازه‌های زمانی بر مبنای تقویم میلادی به جای تقویم هجری شمسی و نمایش خام JSON در فرانت‌اند:**  
   پنل کاربری فرانت‌اند بازه هفتگی را دوشنبه تا یکشنبه میلادی و ماهانه را اول تا آخر ماه میلادی می‌گیرد و ارقام پیچیده جیسون را به صورت خام در جدول رها می‌کند.

---

### جدول ماتریس ارزیابی انطباق سناریوها

| شناسه داستان / سناریو | شرح در سند مشخصات (SPEC-08) | وضعیت انطباق | علت و خلاصه شواهد در کد جاری |
| :--- | :--- | :---: | :--- |
| **US-PR-04 (سناریو ۱)** | تولید خودکار ۵ سکشن الزامی گزارش هفتگی (فعالیت‌های تکمیل‌شده، فعالیت‌های بحرانی دارای تأخیر، جدول نفر-ساعت و ماشین‌آلات، احجام مصالح وارده/مصرفی، برنامه هفته آینده) | ❌ شکاف بحرانی (P1) | در `period_report_service.py` هیچ کوئری یا تجمیعی از مدل‌های گزارش روزانه (`DailyReportLabor`, `DailyReportMachineryRow`, `DailyReportMaterial`) وجود ندارد. جداول نیروی انسانی، ماشین‌آلات و مصالح به کلی وجود ندارند. |
| **US-PR-04 (سناریو ۲)** | استثنا کردن روزهای پیش‌نویس (`draft`) و درج پیام اخطار «گزارش روز X تأیید نشده است» در هدر گزارش هفتگی | ❌ شکاف بحرانی (P1) | هیچ اعتبارسنجی وضعیتی روی گزارش‌های روزانه بازه انجام نمی‌شود و مدل `ProjectPeriodReport` هیچ فیلدی برای هشدارهای هدر ندارد. |
| **US-PR-05 (سناریو ۱)** | تولید فصول جامع گزارش ماهانه (پیشرفت برنامه‌ای در برابر واقعی، وضعیت مالی و جریان نقدینگی، حوادث HSE و بازرسی‌های QC، تحلیل انحرافات SPI و CPI) | ⚠️ انطباق ناقص (P2) | فصول پیشرفت، هزینه و IPC وجود دارند؛ اما حوادث HSE روزانه و بازرسی‌های QC ادغام نشده‌اند و شاخص CPI در کنار SPI غایب است. |
| **US-PR-05 (سناریو ۲)** | صدور نسخه نهایی ماهانه دارای شماره سریال رسمی یکتا و زمان دقیق استخراج بر روی تمام صفحات خروجی | ❌ شکاف اساسی (P2) | مدل `ProjectPeriodReport` فاقد فیلد `serial_number` و وضعیت `approved` است؛ هیچ خروجی رسمی چندصفحه‌ای دارای واترمارک و شماره سریال وجود ندارد. |
| **US-PR-06 (سناریو ۱)** | ردیابی عدد تجمیعی به رکوردهای روزانه منبع (`GET .../figures/{figure_id}/`) با نمایش روز، شماره رکورد، حجم روز، ثبت‌کننده و تأییدکننده | ❌ شکاف بحرانی (P1) | اندپوینت جزئیات رقم فقط یک رکورد تخت بازمی‌گرداند. هیچ مدل و داده‌ای برای ریز اقلام تشکیل‌دهنده عدد تجمیعی (Breakdown Items) طراحی نشده است. |
| **US-PR-06 (سناریو ۲)** | ممانعت از حذف فیزیکی رکوردهای گزارش روزانه مبنا توسط پایگاه داده با خطای Protected Foreign Key | ❌ شکاف معماری (P1) | فیلد `source_id` در جدول ارقام یک `UUIDField` آزاد است و هیچ قید کلید خارجی یا `PROTECT` به رکوردهای روزانه در پایگاه داده متصل نیست. |
| **US-PR-07 (سناریو ۱)** | الزام ثبت دلیل بازنویسی با حداقل ۱۰ کاراکتر و صدور خطای `override_reason_required` | ⚠️ انطباق ناقص (P1) | سرور و فرانت‌اند تنها شرط خالی نبودن را چک می‌کنند (`if not reason:`)؛ دلایل با طول کمتر از ۱۰ کاراکتر پذیرفته می‌شوند. |
| **US-PR-07 (سناریو ۲)** | حفظ رقم اولیه `calculated_value`، ثبت رکورد در `PeriodReportFigureOverride` و نمایش ستاره (*) با پانویس در خروجی چاپی و UI | ⚠️ انطباق ناقص (P1) | رکورد اورراید ثبت می‌شود، اما مقدار اولیه در جدول ارقام اوررایت می‌شود؛ در فرانت‌اند هیچ ستاره (*)، پانویس ارجاع یا نشانی از بازنویسی ارائه نمی‌شود. |

---

## ۲. یافته‌های تفصیلی و شواهد کد (Detailed Findings & Code Evidence)

### G01 — P1 — عدم تجمیع داده‌های میدانی گزارش‌های روزانه کارگاه در گزارش هفتگی (نیروی انسانی، ماشین‌آلات، احجام مصالح و فعالیت‌های تکمیل‌شده)

**شرح نیازمندی در SPEC-08 (داستان US-PR-04، سناریو ۱):**  
> «گزارش تولیدشده هفتگی باید شامل بخش‌های الزامی زیر باشد:  
> ۱. خلاصه فعالیت‌های تکمیل‌شده هفته  
> ۲. فعالیت‌های بحرانی دارای تأخیر و انحراف  
> ۳. جدول تجمیعی نفر-ساعت نیروی انسانی و کارکرد ماشین‌آلات  
> ۴. احجام مصالح وارده و مصرفی هفته  
> ۵. برنامه کاری و اولویت‌های هفته آینده»

**وضعیت در کد جاری:**  
در فایل [`apps/api/core/schedule/services/period_report_service.py:32-38`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/period_report_service.py#L32-L38):
```python
WEEKLY_SECTIONS = (
    'progress_summary',
    'critical_activities',
    'next_week_plan',
    'barriers',
    'decisions_required',
)
```
و در تابع ترکیب سکشن‌های هفتگی در سطرهای ۳۴۲-۳۵۰:
```python
    if kind == PeriodReportKind.WEEKLY:
        return [
            _progress_summary(pid, end),
            _critical_activities(pid, status_report),
            _window_plan(pid, end + timedelta(days=1), end + timedelta(days=7), 'next_week_plan'),
            _barriers(pid),
            _decisions_required(pid),
        ]
```
**پیامدهای شکاف:**  
1. سرویس تولید گزارش دوره‌ای اصلاً مدل‌های `DailyReportLabor`، `DailyReportMachineryRow` / `DailyReportEquipment` و `DailyReportMaterial` را ایمپورت یا کوئری نمی‌کند.
2. هیچ تجمیعی از نفر-ساعت عوامل انسانی کارگاه (تعداد نفر، ساعات کارکرد عادی و اضافه‌کار به تفکیک پیمانکار/تخصص) انجام نمی‌شود.
3. هیچ تجمیعی از ساعات کارکرد و توقفات ماشین‌آلات کارگاه در طول هفته ارائه نمی‌گردد.
4. آمار احجام مصالح وارده به کارگاه و مصالح مصرف‌شده در فعالیت‌ها در طول بازه هفته وجود ندارد.
5. بخش فعالیت‌های تکمیل‌شده در طول هفته استخراج نمی‌شود (سکشن `_critical_activities` صرفاً تأخیرات را لیست می‌کند، نه لیست کارهای تمام‌شده).

---

### G02 — P1 — عدم اعتبارسنجی گزارش‌های روزانه پیش‌نویس (`draft`) و فقدان اخطار در هدر گزارش هفتگی

**شرح نیازمندی در SPEC-08 (داستان US-PR-04، سناریو ۲):**  
> «با فرض اینکه یکی از گزارش‌های روزانه در وضعیت `draft` باقی مانده باشد،  
> هنگامی که تجمیع هفتگی اجرا شود،  
> آنگاه سیستم مقادیر آن روز را در گزارش هفتگی محاسبه نکرده و یک هشدار «گزارش روز X تأیید نشده است» به هدر گزارش هفتگی ضمیمه کند.»

**وضعیت در کد جاری:**  
در فایل [`apps/api/core/schedule/services/period_report_service.py:364-416`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/period_report_service.py#L364-L416)، متد `generate_period_report`:
1. هیچ بررسی یا شمارشی از گزارش‌های روزانه بازه (`DailyReport.objects.filter(project=project, report_date__range=(period_start, period_end))`) به عمل نمی‌آورد.
2. هیچ تفکیکی میان گزارش‌های تأییدشده (`approved`) و گزارش‌های پیش‌نویس (`draft`) انجام نمی‌دهد.
3. مدل `ProjectPeriodReport` در [`models.py:436-466`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/models.py#L436-L466) فاقد هرگونه فیلد هشدارهای متادیتای هدر (مانند `warnings = models.JSONField(default=list)`) است. در نتیجه کاربر نمی‌داند آمار ارائه شده ناقص است و کدام روزهای کارگاه در گزارش دخالت داده نشده‌اند.

---

### G03 — P1 — فقدان ریز ردپای ارقام (Figure Provenance Breakdown) و عدم ممانعت دیتابیس از حذف رکوردهای منبع (Protected FK)

**شرح نیازمندی در SPEC-08 (داستان US-PR-06، سناریوهای ۱ و ۲):**  
> «سناریو ۱: با فرض اینکه در گزارش هفتگی حجم بتن‌ریزی هفته ۱۸۰ مترمکعب ثبت شده باشد، هنگامی که کاربر اندپوینت جزئیات رقم (`GET .../figures/{figure_id}/`) را صدا بزند، آنگاه سیستم لیست دقیق شامل: «روز دوشنبه ۵۰ مترمکعب از رکورد گزارش روزانه شماره ۱۰۲»، «روز چهارشنبه ۱۳۰ مترمکعب از رکورد شماره ۱۰۴» را به همراه کاربر ثبت‌کننده و تأییدکننده نمایش دهد.  
> سناریو ۲: با فرض اینکه رکوردی منبع یک گزارش هفتگی رسمی باشد، هنگامی که کاربری بخواهد آن رکورد گزارش روزانه را حذف فیزیکی کند، آنگاه پایگاه داده با خطای یکپارچگی ارجاعی (Protected Foreign Key) جلوی حذف را بگیرد.»

**وضعیت در کد جاری:**  
1. **مدل تخت ارقام بدون ریز اقلام:** در [`apps/api/core/schedule/models.py:483-502`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/models.py#L483-L502):
   ```python
   class PeriodReportFigure(UUIDModel):
       report = models.ForeignKey(ProjectPeriodReport, on_delete=models.CASCADE, related_name='figures')
       section = models.CharField(max_length=60)
       label_key = models.CharField(max_length=120)
       value = models.JSONField(null=True, blank=True)
       source_type = models.CharField(max_length=40, blank=True, default='')
       source_id = models.UUIDField(null=True, blank=True)
       source_path = models.CharField(max_length=255, blank=True, default='')
       source_approved = models.BooleanField(default=False)
   ```
   فیلد `source_id` یک مقدار UUID منفرد است. در حالی که یک رقم تجمیعی هفتگی (مثلاً ۱۸۰ مترمکعب بتن یا ۲۵۰ نفر-ساعت کارکرد) حاصل جمع چندین رکورد در روزهای مختلف هفته است. هیچ موجودیتی مانند `PeriodReportFigureSourceItem` برای نگهداری سهم هر گزارش روزانه و کلیدهای اصلی آن وجود ندارد.
2. **فقدان قید کلید خارجی محافظت‌شده (Protected FK):**  
   فیلد `source_id` یک کلید خارجی رابطه‌ای نیست بلکه یک فیلد داده‌ای ساده است؛ بنابراین در سطح پایگاه داده هیچ قید `on_delete=models.PROTECT` وجود ندارد. اگر کاربری یک رکورد از `DailyReport` را حذف کند، دیتابیس هیچ خطایی پرتاب نمی‌کند و قابلیت ردیابی ارقام گزارش‌های رسمی از بین می‌رود.
3. **اندپوینت جزئیات رقم:** در فایل [`apps/api/core/schedule/period_report_views.py:114-116`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/period_report_views.py#L114-L116):
   اندپوینت `GET .../figures/{figure_id}/` صرفاً متادیتای کلی رکورد `PeriodReportFigure` را بازمی‌گرداند و فاقد لیست رکوردهای تشکیل‌دهنده، نام کاربران ثبت‌کننده و تأییدکننده رکوردهای روزانه است.

---

### G04 — P1 — عدم اعتبارسنجی حداقل طول دلیل بازنویسی (۱۰ کاراکتر) و از بین رفتن مقدار محاسبه‌شده اولیه (`calculated_value`) در مدل رقم

**شرح نیازمندی در SPEC-08 (داستان US-PR-07، سناریوهای ۱ و ۲):**  
> «سناریو ۱: با فرض اینکه کاربر بخواهد پیشرفت فیزیکی محاسبه‌شده را بازنویسی کند، هنگامی که فیلد `override_reason` را خالی بگذارد یا متنی کوتاهتر از ۱۰ کاراکتر وارد کند، آنگاه سرور با خطای `override_reason_required` مانع ذخیره‌سازی شود.  
> سناریو ۲: مقدار اولیه `calculated_value = 42%` بدون تغییر در جدول باقی بماند، مقدار جدید `overridden_value = 45%` در جدول `PeriodReportFigureOverride` همراه با کاربر بازنویسی‌کننده، زمان و دلیل ثبت شود و در خروجی چاپی در کنار عدد، یک علامت ستاره (*) با ارجاع به پانویس درج گردد.»

**وضعیت در کد جاری:**  
1. **عدم بررسی طول ۱۰ کاراکتر در بک‌اند:**  
   در فایل [`apps/api/core/schedule/services/period_report_service.py:428-432`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/period_report_service.py#L428-L432):
   ```python
   @transaction.atomic
   def apply_figure_override(figure: PeriodReportFigure, new_value, reason: str, user) -> PeriodReportFigureOverride:
       reason = (reason or '').strip()
       if not reason:
           raise ProgressValidationError('دلیل override الزامی است.', 'override_reason_required')
   ```
   تنها شرط خالی نبودن بررسی می‌شود! اگر کاربر دلیل ۱ یا ۲ حرفی (مثلاً `"تست"` یا `"ok"`) وارد کند، بدون خطا ثبت می‌شود و شرط الزامی حداقل ۱۰ کاراکتر نادیده گرفته می‌شود. حتی در تست‌های سیستم ([`test_period_reports.py:141`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/tests/test_period_reports.py#L141)) دلیل با مقدار `'x'` تست شده است!
2. **عدم بررسی طول در فرانت‌اند:**  
   در کامپوننت [`apps/web/src/components/progress/PeriodReportsPanel.tsx:226`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/progress/PeriodReportsPanel.tsx#L226):
   دکمه ذخیره با `disabled={!overrideReason.trim()}` کنترل شده است و متن‌های با طول کمتر از ۱۰ کاراکتر فعال هستند.
3. **اوررایت شدن مقدار خام در جدول ارقام:**  
   در خطوط ۴۴۱-۴۴۵ از `period_report_service.py`:
   ```python
   PeriodReportFigure.objects.filter(pk=figure.pk).update(
       value=new_value,
       value_status=FigureValueStatus.RECORDED,
       last_updated_at=timezone.now(),
   )
   ```
   فیلد `value` در جدول `PeriodReportFigure` مستقیماً با مقدار جدید رونویسی می‌شود؛ مدل دارای ستون مجزای `calculated_value` نیست و استعلام‌های مستقیم روی رقم، مقدار محاسبه‌شده اولیه را از دست می‌دهند.
4. **فقدان علامت ستاره (*) و پانویس در خروجی UI:**  
   در کامپوننت `PeriodReportsPanel.tsx` هیچ علامتی اعم از ستاره (*)، برچسب بازنویسی‌شده، یا پانویس ارجاع برای ارقامی که بازنویسی شده‌اند نمایش داده نمی‌شود.

---

### G05 — P2 — فقدان ارکان ماهانه: حوادث HSE، بازرسی‌های QC، شاخص CPI و فرآیند تصویب با شماره سریال رسمی یکتا

**شرح نیازمندی در SPEC-08 (داستان US-PR-05، سناریوهای ۱ و ۲):**  
> «گزارش ماهانه جامع پروژه شامل:  
> - درصد پیشرفت فیزیکی برنامه‌ای در برابر واقعی کل ماه  
> - وضعیت مالی و صورت‌وضعیت‌های کارکرد و پیش‌بینی جریان نقدینگی  
> - خلاصه وضعیت حوادث HSE، اقدامات اصلاحی و بازرسی‌های کنترل کیفیت  
> - نمودار انحرافات (Variance Analysis) و شاخص‌های SPI و CPI ماهانه  
> - ثبت نسخه نهایی ماهانه با شماره سریال یکتا و زمان دقیق استخراج بر روی تمام صفحات خروجی.»

**وضعیت در کد جاری:**  
1. **فقدان HSE و QC:** در `MONTHLY_SECTIONS` و متد `_compose_figures` در [`period_report_service.py:351-358`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/period_report_service.py#L351-L358)، تنها مدل `RiskEvent` برای موانع و ریسک‌ها کوئری می‌شود. حوادث کارگاهی ثبت‌شده در گزارش‌های روزانه (`DailyReportIncident`)، ممیزی‌های HSE و بازرسی‌های کنترل کیفیت (Quality / QC) به طور کلی غایب هستند.
2. **فقدان شاخص CPI:** در تابع `_baseline_variance` در سطرهای ۲۱۹-۲۲۴:
   ```python
   value={
       'planned_progress_pct': snapshot['planned_progress_pct'],
       'actual_progress_pct': snapshot['actual_progress_pct'],
       'schedule_variance_pct': snapshot['schedule_variance_pct'],
       'spi': snapshot['spi'],
   }
   ```
   شاخص عملکرد هزینه (Cost Performance Index - CPI) در محاسبات حضور ندارد.
3. **نبود شماره سریال یکتا و وضعیت تصویب:** مدل `ProjectPeriodReport` صرفاً دو وضعیت `GENERATED` و `SUPERSEDED` دارد و وضعیت `APPROVED` یا `FINAL` ندارد. هیچ فیلد شماره سریال یا کد یکتایی برای گزارش‌های مصوب وجود ندارد و قابلیت صدور خروجی رسمی (PDF/چاپ) همراه با درج شماره سریال و زمان استخراج در هدر/فوتر صفحات پیاده‌سازی نشده است.

---

### G06 — P2 — مغایرت مجوز امنیتی در اندپوینت بازنویسی رقم (Figure Override View)

**شرح نیازمندی در SPEC-08 (داستان US-PR-07، پیش‌شرط):**  
> «پیش‌شرط‌ها: کاربر دارای مجوز ارشد `edit_reports` یا `approve_reports` باشد.»

**وضعیت در کد جاری:**  
در فایل [`apps/api/core/schedule/period_report_views.py:126-142`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/period_report_views.py#L126-L142):
کلاس `ProgressReportFigureOverrideView` از `ProgressDomainView` مشتق شده است. در `ProgressDomainView`:
```python
write_permission = 'edit_activities'
```
و این ویو هیچ مقدار جدیدی برای `write_permission` یا `approve_permission` تعیین نکرده است. در نتیجه کاربری که صرفاً مجوز ویرایش فعالیت‌ها (`edit_activities`) را در پروژه داشته باشد، مجاز به تغییر ارقام نهایی گزارش هفتگی/ماهانه مدیریتی می‌شود، در حالی که این عمل ممیزی حساس نیازمند مجوزهای ارشد گزارشات (`edit_reports` یا `approve_reports`) است.

---

### G07 — P2 — نقایص رابط کاربری فرانت‌اند: محاسبه بازه‌ها با تقویم میلادی به جای شمسی و رها شدن آبجکت‌های JSON در جدول

**شرح نیازمندی در SPEC-08 (بخش ۳، US-PR-04 و US-PR-05):**  
> «تولید گزارش هفتگی برای بازه شنبه تا جمعه کارگاه و گزارش ماهانه برای یک ماه شمسی.»

**وضعیت در کد جاری:**  
1. **تولید بازه‌ها با تقویم میلادی:**  
   در فایل [`apps/web/src/components/progress/PeriodReportsPanel.tsx:16-37`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/progress/PeriodReportsPanel.tsx#L16-L37):
   توابع `mondayOf` و `sundayOf` هفته را از دوشنبه تا یکشنبه میلادی تنظیم می‌کنند و تابع `monthBounds` نیز ابتدا و انتهای ماه میلادی (Gregorian month) را استخراج می‌کند. تقویم کاری ایران (شنبه تا جمعه و ماه‌های شمسی فروردین تا اسفند) کاملاً نادیده گرفته شده است و هیچ پیکر تقویم شمسی برای انتخاب بازه توسط کاربر در پنل تعبیه نشده است.
2. **رندر خام JSON:**  
   در سطر ۱۶۷ از `PeriodReportsPanel.tsx`:
   ```tsx
   typeof f.value === "object"
     ? JSON.stringify(f.value)
     : String(f.value ?? "—")
   ```
   مقادیر ساختاریافته سکشن‌هایی چون برنامه هفته آینده، فعالیت‌های بحرانی، موانع، تعهدات و IPC به صورت یک رشته متنی خام و نامفهوم JSON در یک سلول جدول چاپ می‌شوند و هیچ جدول یا کارت تخصصی برای نمایش خوانا و شکیل آن‌ها وجود ندارد.

---

## ۳. جدول جمع‌بندی اولویت‌بندی شکاف‌ها (Action Plan & Priority Matrix)

| کد شکاف | اولویت | عنوان شکاف | فایل‌های اصلی درگیر | نتیجه مورد انتظار |
| :---: | :---: | :--- | :--- | :--- |
| **G01** | **P1** | عدم تجمیع داده‌های میدانی گزارش‌های روزانه کارگاه | `period_report_service.py`, `models.py` | افزودن متدهای تجمیع نفر-ساعت، ماشین‌آلات، احجام مصالح وارده/مصرفی و کارهای تکمیل‌شده از `field_reports` |
| **G02** | **P1** | عدم شناسایی گزارش‌های روزانه پیش‌نویس و فقدان هشدار در هدر | `period_report_service.py`, `models.py`, `serializers.py` | استثنا کردن روزهای `draft` و ذخیره لیست هشدارهای «گزارش روز X تأیید نشده است» در هدر گزارش |
| **G03** | **P1** | فقدان ردپای ساختاریافته ارقام (Breakdown) و کلید خارجی محافظت‌شده | `models.py`, `period_report_service.py`, `period_report_views.py` | ایجاد مدل `PeriodReportFigureSourceItem` با پیوند به روزهای مبنا و اعمال قید `PROTECT` در دیتابیس |
| **G04** | **P1** | عدم بررسی حداقل طول دلیل بازنویسی (۱۰ کاراکتر) و حفظ مقدار اولیه | `period_report_service.py`, `models.py`, `PeriodReportsPanel.tsx` | ولیدیشن `len(reason) >= 10`، نگهداری فیلد `calculated_value` و نمایش علامت ستاره (*) و پانویس در UI |
| **G05** | **P2** | فقدان حوادث HSE، بازرسی‌های QC، شاخص CPI و فرآیند تصویب رسمی | `period_report_service.py`, `models.py`, `period_report_views.py` | تجمیع آمار HSE و بازرسی‌های کیفی، محاسبه CPI، افزودن فیلد شماره سریال یکتا و متد تایید نهایی |
| **G06** | **P2** | نقص در دسترسی امنیتی بازنویسی ارقام | `period_report_views.py` | اصلاح مجوزهای `ProgressReportFigureOverrideView` به `edit_reports` یا `approve_reports` |
| **G07** | **P2** | نقایص رابط کاربری: تقویم میلادی و نمایش خام JSON | `PeriodReportsPanel.tsx`, `progress.ts` | استفاده از تقویم شمسی (شنبه-جمعه)، افزودن پیکر تاریخ شمسی، و طراحی کامپوننت‌های نمایش اختصاصی سکشن‌ها |
