# سند نهایی ارزیابی شکاف‌ها و تحلیل انطباق: موتور تجمیع خودکار ساب‌ریپورت‌ها در گزارش جامع روزانه

**شناسه سند:** `GAP-SPEC-06-AUTO-DAILY-ROLLUP`  
**سند مشخصات فنی هدف:** [`SPEC-06-AUTO-DAILY-ROLLUP.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md)  
**اسناد مرجع همبسته:**  
- [`01-.../مستندات فرم‌های اکسل شیراز (FILE 1 و FILE 5)`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/01-core-requirements-and-excel-blueprints/مستندات%20فرم‌های%20اکسل%20شیراز%20(Shiraz%20Excel%20Forms%20Documentation).md)  
- [`02-.../daily-report-summary-api.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/02-daily-summary-rollup-engine/daily-report-summary-api.md)  
- [`02-.../daily-report-summary-ui.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/02-daily-summary-rollup-engine/daily-report-summary-ui.md)  
- [`specs/028-auto-daily-summary-rollup/spec.md`](file:///home/hossein/Desktop/projects/building-management/specs/028-auto-daily-summary-rollup/spec.md)  
- [`specs/032-unit-report-source-truth/spec.md`](file:///home/hossein/Desktop/projects/building-management/specs/032-unit-report-source-truth/spec.md)  
- [`specs/033-daily-sections-grid/spec.md`](file:///home/hossein/Desktop/projects/building-management/specs/033-daily-sections-grid/spec.md)  
**تاریخ ارزیابی:** ۶ آبان ۱۴۰۵ (2026-10-28)  
**دامنه ارزیابی:**  
- بک‌اند: [`apps/api/core/field_reports/services/daily_report_aggregation.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/daily_report_aggregation.py)، [`apps/api/core/field_reports/daily_report_views.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py)، [`apps/api/core/field_reports/services/activity_log.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/activity_log.py)، [`apps/api/core/field_reports/report_views.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/report_views.py)، [`apps/api/core/field_reports/models.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/models.py)  
- فرانت‌اند: [`apps/web/src/components/daily_reports/summary/DailyReportSummaryView.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/summary/DailyReportSummaryView.tsx)، [`apps/web/src/components/daily_reports/summary/IncompletenessBanner.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/summary/IncompletenessBanner.tsx)، [`apps/web/src/components/daily_reports/DailyReportForm.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/DailyReportForm.tsx)، [`apps/web/src/app/routes/daily-reports-list.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/daily-reports-list.tsx)، [`apps/web/src/app/routes/daily-report-view.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/daily-report-view.tsx)، [`apps/web/src/app/routes/project-activity-log.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/project-activity-log.tsx)  
**وضعیت کلی سند:** ⚠️ **دارای شکاف‌های انطباق بحرانی و عملکردهای ناتمام (Fail - Action Required)**

---

## ۱. خلاصه‌ی اجرایی و تحلیل انطباق (Executive Summary)

سند مشخصات فنی اتمیک **`SPEC-06-AUTO-DAILY-ROLLUP`** قلب تپنده انتقال داده از ساب‌ریپورت‌های تخصصی واحدهای کارگاهی به شل جامع گزارش روزانه پروژه (`DailyReport`) است. این سند ایجاد گزارش‌های خام دستی را منسوخ کرده و تجمیع خودکار را جایگزین آن می‌کند.

بررسی کدبیس نشان می‌دهد اگرچه شاکله و متد پایه [`rebuild_daily_report_summary`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/daily_report_aggregation.py#L537-L610) در فازهای ۰۲۸ و ۰۳۳ پیاده‌سازی شده است، اما میان نیازمندی‌های صریح ۶ گانه در سند **SPEC-06** و پیاده‌سازی فعلی شکاف‌ها و مغایرت‌های فنی جدی وجود دارد:

1. **انحراف قرارداد اندپوینت `by-date` (خطای ۴۰۴ در برابر الزام ایجاد خودکار):**  
   طبق سناریوی ۲ از داستان US-AG-01، فراخوانی `GET /api/v1/projects/{pk}/daily-reports/by-date/?date=YYYY-MM-DD` در صورتی که گزارشی وجود نداشته باشد، باید در لحظه یک شل معتبر با `is_auto_summary=True` ایجاد کرده و با کد `200 OK` تحویل دهد. در پیاده‌سازی فعلی، درخواست `GET` در صورت عدم وجود گزارش با خطای `404 Not Found` رد می‌شود و ایجاد شل صرفاً به درخواست `POST` با مجوز ویرایش موکول شده است. همچنین پارامتر `shift` در کوئری کاملاً نادیده گرفته می‌شود.
2. **اتلاف تفکیک پیمانکاران در تجمیع نیروی انسانی (Flattening Contractors):**  
   طبق سناریوی ۲ از داستان US-AG-02، تجمیع نیروی انسانی باید با کلید ترکیبی `(job_title, contractor)` صورت گیرد تا کارکرد پیمانکاران مختلف در یک عنوان شغلی مجزا بماند. در سرویس جاری، کلید تجمیع صرفاً عنوان شغلی است، پیمانکار در کلید باکت نادیده گرفته شده و مدل `DailyReportLabor` اصلاً فیلدی برای ارجاع به پیمانکار (`contractor_ref`) ندارد!
3. **نشت فرم‌های دستی ویرایش و عدم تطابق کدهای خطای ردیف‌های مشتق‌شده:**  
   در بک‌اند، هنگام تلاش برای افزودن ردیف مشتق‌شده، کد خطای `derived_readonly` با پیامی عمومی بازمی‌گردد در حالی که سند کد صریح `derived_collection_read_only` را الزام کرده است. در فرانت‌اند، کامپوننت `DailyReportForm.tsx` هیچ بررسی روی `is_auto_summary` انجام نداده و در مسیر `/edit` دکمه‌های افزودن و حذف ردیف را به کاربر نشان می‌دهد.
4. **نقصان داده‌ای و فیلترینگ بانک جامع فعالیت‌ها (`ACTIVITY` Master Log):**  
   مطابق شیت ACTIVITY اکسل شیراز و سناریوی ۱ از US-AG-06، لاگ جامع فعالیت‌ها باید دارای ستون‌های «دیسیپلین منبع» (`source_discipline`) و «قطعه» (`parcel`) و قابلیت فیلتر بر اساس آن‌ها باشد. در خروجی اندپوینت و صفحه فرانت‌اند `project-activity-log.tsx` این دو فیلد کاملاً غایب هستند. علاوه بر این، کش ۵ دقیقه‌ای اندپوینت پس از تأیید گزارش باطل نمی‌شود و به روزرسانی بلادرنگ محقق نمی‌گردد.
5. **فقدان بنر سبز تکمیل گزارشات:**  
   در سناریوی ۲ از US-AG-05 صراحتاً آمده است که با ثبت تمامی ساب‌ریپورت‌های مورد انتظار، بنر سبز رنگی مبنی بر «تمام گزارش‌های دیسیپلین دریافت و تجمیع شدند» نمایش داده شود؛ اما کامپوننت فرانت‌اند در زمان تکمیل، مقدار `null` بازمی‌گرداند و هیچ بازخورد مثبتی به کاربر نمی‌دهد.

---

### جدول ماتریس ارزیابی انطباق سناریوها

| شناسه داستان / سناریو | شرح در سند مشخصات (SPEC-06) | وضعیت انطباق | علت و خلاصه شواهد در کد جاری |
| :--- | :--- | :---: | :--- |
| **US-AG-01 (سناریو ۱)** | حذف دکمه «گزارش جدید» و پاسخ ۴۰۰ به درخواست دستی `POST .../daily-reports/` بدون بدنه ساب‌ریپورت | ✅ منطبق | در فرانت‌اند دکمه سنتی حذف شده؛ در بک‌اند [`DailyReportViewSet.create`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L191-L195) خطای ۴۰۰ با کد `auto_summary_only` صادر می‌کند. |
| **US-AG-01 (سناریو ۲)** | تضمین دسترسی به تاریخ با اندپوینت `GET .../by-date/` و ایجاد در لحظه شل معتبر با کد `200 OK` | ❌ شکاف بحرانی (P1) | در متد `GET`، اگر گزارش نباشد خطای `404 Not Found` صادر می‌شود؛ شل فقط با `POST` ساخته می‌شود؛ پارامتر `shift` نادیده گرفته می‌شود. |
| **US-AG-02 (سناریو ۱)** | تجمیع اجتماع فعالیت‌ها (Union of Activities) با قید دیسیپلین منبع | ✅ منطبق | در سرویس تجمیع، کلیه ردیف‌های فعالیت با `source_discipline` در جدول `DailyReportActivity` کپی و تجمیع می‌شوند. |
| **US-AG-02 (سناریو ۲)** | جمع کلیدمحور نیروی انسانی به ازای هر ترکیب `(job_title, contractor)` | ❌ شکاف داده و لاجیک (P1) | باکت تجمیع فقط روی عنوان شغلی است؛ پیمانکار نادیده گرفته شده و مدل `DailyReportLabor` فیلد `contractor_ref` ندارد. |
| **US-AG-02 (سناریو ۳)** | ثبت و بازگرداندن زمان تجمیع `aggregated_at` با تاریخ شمسی و UTC | ⚠️ انطباق نسبی (P2) | زمان UTC ثبت می‌شود، اما خروجی متادیتا فاقد نمایش تقویم شمسی (`aggregated_at_jalali`) است. |
| **US-AG-03 (سناریو ۱)** | ممانعت از افزودن ردیف مشتق‌شده با کد خطای `derived_collection_read_only` و پیام هدایتگر | ⚠️ انطباق نسبی (P1) | ممانعت انجام می‌شود، اما کد خطا `derived_readonly` است و متن پیام با متن مصوب تفاوت دارد. |
| **US-AG-03 (سناریو ۲)** | حذف یا غیرفعال شدن دکمه‌های «افزودن ردیف» و سطل زباله «حذف ردیف» در فرانت‌اند | ❌ شکاف تجربه کاربری (P1) | در مسیر `/edit` و فرم `DailyReportForm.tsx` فلگ `is_auto_summary` بررسی نشده و دکمه‌های گرید فعال نمایش داده می‌شوند. |
| **US-AG-04 (سناریو ۱)** | انتخاب شدیدترین شرایط جوی بر اساس اولویت `clear < cloudy < rainy < snowy < stormy` | ✅ منطبق | دیکشنری `WEATHER_SEVERITY` و تابع `_pick_weather` این سلسله‌مراتب ۵ گانه را به دقت پیاده‌سازی کرده‌اند. |
| **US-AG-04 (سناریو ۲)** | حفظ بازنویسی دستی شرایط جوی توسط مدیر با برچسب `overridden_by_manager` | ⚠️ انطباق نسبی (P2) | مقدار بازنویسی حفظ می‌شود، اما مقدار فیلد سورس `override` است و برچسب `overridden_by_manager` در مدل/خروجی ثبت نمی‌شود. |
| **US-AG-05 (سناریو ۱)** | تشخیص و اعلام دیسیپلین‌های غایب در API و نمایش بنر نارنجی نقص گزارش | ✅ منطبق | لیست `missing_units` و بنر هشدار در کامپوننت `IncompletenessBanner.tsx` نمایش داده می‌شود. |
| **US-AG-05 (سناریو ۲)** | نمایش پیام و بنر سبز «تمام گزارش‌های دیسیپلین دریافت و تجمیع شدند» پس از ارسال کامل | ❌ شکاف فرانت‌اند (P2) | در وضعیت کامل (`state === 'complete'`) بنر مقدار `null` بازمی‌گرداند و پیام تبریک و تأیید سبز نمایش داده نمی‌شود. |
| **US-AG-06 (سناریو ۱)** | انعکاس بلادرنگ فعالیت‌ها در بانک جامع فعالیت‌ها (`ACTIVITY` Master Log) با فیلتر دیسیپلین و قطعه | ❌ شکاف API و UI (P1) | فیلدهای `source_discipline` و `parcel` در سریالایزر، فیلترها و جدول فرانت‌اند غایب هستند؛ کش اندپوینت نیز بی‌درنگ ابطال نمی‌شود. |

---

## ۲. یافته‌های تفصیلی و شواهد کد (Detailed Findings & Code Evidence)

### G01 — P1 — بازگرداندن خطای ۴۰۴ در متد `GET /daily-reports/by-date/` و نادیده گرفتن پارامتر `shift`

**شرح نیازمندی در SPEC-06 (داستان US-AG-01، سناریو ۲):**  
> «با فرض اینکه کاربر یک تاریخ مشخص (مثلاً `2026-10-22`) را در تقویم انتخاب کند، هنگامی که فرانت‌اند درخواست `GET /api/v1/projects/{pk}/daily-reports/by-date/?date=2026-10-22` ارسال می‌کند، آنگاه اگر گزارشی از قبل برای آن تاریخ وجود داشته باشد بازگردانده شود؛ و اگر وجود نداشته باشد، سرور در لحظه یک شل معتبر با `is_auto_summary=True` ایجاد کرده و با کد `200 OK` بازگرداند.»  
> قرارداد: `GET /api/v1/projects/{project_pk}/daily-reports/by-date/?date={YYYY-MM-DD}&shift={1|2|3}`

**وضعیت در کد جاری:**  
در فایل [`apps/api/core/field_reports/daily_report_views.py:206-222`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L206-L222):
```python
        if request.method.upper() == 'GET':
            report = (
                DailyReport.objects.filter(
                    project_id=project_id,
                    report_date=report_date,
                    shift=ReportShift.FULL,
                    is_deleted=False,
                    is_current=True,
                )
                .order_by('-created_at')
                .first()
            )
            if report is not None:
                return Response(DailyReportDetailSerializer(report, context={'request': request}).data)
            from rest_framework.exceptions import NotFound
            raise NotFound({'detail': 'گزارشی برای این تاریخ یافت نشد', 'code': 'report_not_found'})
```
**پیامدهای شکاف:**
1. هنگامی که یک ناظر یا مهندس با دسترسی خواندن (`view_reports`) تقویم را باز می‌کند تا گزارش روزی را ببیند که هنوز شل آن ساخته نشده، به جای دریافت پیش‌نویس تجمیعی از ساب‌ریپورت‌های ثبت‌شده، با خطای ۴۰۴ مواجه می‌شود.
2. فرانت‌اند در فایل [`daily-reports-list.tsx:300-306`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/daily-reports-list.tsx#L300-L306) مجبور شده یک شرط انحرافی بگذارد: اگر کاربر مجوز ادیت دارد با `POST` شل بسازد، و اگر ندارد با `GET` بخواند که در صورت نبودن شل، خطای Toast قرمز به کاربر نمایش داده می‌شود.
3. متد `by_date` مقدار `shift=ReportShift.FULL` را هاردکد کرده و کوئری‌پارامتر `shift` مندرج در استاندارد را نادیده می‌گیرد.

---

### G02 — P1 — عدم تجمیع کلیدمحور نیروی انسانی بر مبنای `(job_title, contractor)` و فقدان فیلد پیمانکار در `DailyReportLabor`

**شرح نیازمندی در SPEC-06 (داستان US-AG-02، سناریو ۲):**  
> «با فرض اینکه ساب‌ریپورت ابنیه ۴ نفر آرماتوربند با پیمانکار A و ساب‌ریپورت برق ۲ نفر برق‌کار با پیمانکار B داشته باشد، هنگامی که تجمیع انجام می‌شود، آنگاه ردیف‌های مجزا به ازای هر ترکیب `(job_title, contractor)` ایجاد شده و در صورت یکسان بودن کلید، تعداد نفرات با هم جمع شوند.»

**وضعیت در کد جاری:**  
در سرویس [`daily_report_aggregation.py:816-834`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/daily_report_aggregation.py#L816-L834):
```python
            if resolved is not None:
                bucket_key = (row.labor_category, f"code:{resolved.title_code}")
                ...
            else:
                bucket_key = (row.labor_category, raw_title)

            bucket = labor_buckets[bucket_key]
            bucket['present'] += row.present_count or 0
```
کلید `bucket_key` صرفاً دسته و عنوان شغل است. ارجاع به پیمانکار (`row.contractor_ref_id`) به کلی از کلید تجمیع حذف شده است.  
علاوه بر این، در مدل [`DailyReportLabor`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/models.py#L335-L375)، هیچ فیلدی به نام `contractor_ref` یا `contractor_name` تعبیه نشده است!

**پیامدهای شکاف:**  
اگر پیمانکار «الف» ۳ نفر قالب‌بند داشته باشد و پیمانکار «ب» ۵ نفر قالب‌بند در دیسیپلین دیگر، در گزارش روزانه تجمیعی یک سطر واحد با ۸ نفر قالب‌بند ظاهر می‌شود و هیچ اطلاعی از سهم هر پیمانکار در جدول نیروی انسانی گزارش کل وجود نخواهد داشت. این امر صورت‌وضعیت‌ها و تفکیک نیروی انسانی کارگاه را مخدوش می‌کند.

---

### G03 — P1 — مغایرت کد خطای رد ردیف مشتق‌شده و نشت گرید ویرایش در `DailyReportForm.tsx`

**شرح نیازمندی در SPEC-06 (داستان US-AG-03، سناریوهای ۱ و ۲):**  
1. هنگام ارسال درخواست ایجاد ردیف در گزارش تجمیعی، سرور باید با کد خطای صریح `400 derived_collection_read_only` درخواست را رد کرده و پیام دهد: «این ردیف‌ها از ساب‌ریپورت‌های دیسیپلین مشتق شده‌اند؛ لطفاً از طریق ساب‌ریپورت مربوطه اقدام نمایید».
2. در نمای فرانت‌اند گزارش تجمیعی، در تب‌های فعالیت‌ها، مصالح و نیروی انسانی، دکمه‌های «افزودن ردیف» و سطل زباله «حذف ردیف» باید مخفی یا غیرفعال باشند.

**وضعیت در کد جاری:**  
1. **در سطح بک‌اند:**  
   در فایل [`daily_report_views.py:590`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L590):
   ```python
   def _assert_editable(self):
       report = self.get_report()
       if report.is_auto_summary:
           raise ValidationError({'detail': DERIVED_READONLY_MSG, 'code': 'derived_readonly'})
   ```
   کد خطای صادرشده `derived_readonly` است (نه `derived_collection_read_only`). همچنین پیام متنی صادرشده عبارت است از: `'ردیف‌های تجمیعی فقط از طریق گزارش واحد تخصصی قابل تغییر هستند'` که با مشخصات قرارداد اتمیک یکسان نیست.
2. **در سطح فرانت‌اند:**  
   در مسیر روت کلاینت [`/projects/:projectId/daily-reports/:reportId/edit`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/daily-report-form-edit.tsx#L8)， کامپوننت [`DailyReportForm.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/DailyReportForm.tsx#L354-L360) رندر می‌شود.  
   این کامپوننت متغیر `report.is_auto_summary` را اصلاً ارزیابی نمی‌کند! در نتیجه برای گزارش‌های پیش‌نویس تجمیعی، گرید قابل ویرایش [`EditableGrid.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/EditableGrid.tsx) را همراه با دکمه «افزودن ردیف» و دکمه‌های حذف ردیف به کاربر نمایش می‌دهد. کاربر ردیف را پر می‌کند و دکمه ذخیره را می‌زند، اما سیستم با خطای ناشناخته اعتبارسنجی را رد می‌کند.

---

### G04 — P1 — نقص بانک جامع فعالیت‌ها (`ACTIVITY` Master Log) مطابق با اکسل شیراز و عدم ابطال کش بلادرنگ

**شرح نیازمندی در SPEC-06 (داستان US-AG-06، سناریو ۱):**  
> «با تأیید هر گزارش روزانه، کلیه رکوردهای فعالیت آن به صورت خودکار در بانک جامع داده‌های پروژه (معادل شیت ACTIVITY در فرم شیراز) ذخیره شوند، تا تمامی فعالیت‌های مندرج در گزارش روزانه به صورت سطرهای مستقل با تاریخ، دیسیپلین، جبهه کاری و مقدار قابل فیلتر و جستجو باشند.»  
> اسناد مرجع اکسل شیراز: ستون‌های الزامی شیت ACTIVITY شامل: تاریخ، دیسیپلین، شرح فعالیت، شیفت، پیمانکار، نفرات، قطعه (Parcel)، بلوک، طبقه، موقعیت، مقدار، واحد.

**وضعیت در کد جاری:**  
1. **سریالایزر لاگ فعالیت‌ها:**  
   در فایل [`apps/api/core/field_reports/services/activity_log.py:38-60`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/activity_log.py#L38-L60):
   ```python
   def serialize_activity_log_row(row: DailyReportActivity) -> dict:
       return {
           'id': str(row.id),
           'report_id': str(report.id),
           'report_date': gregorian_to_jalali(report.report_date),
           'day_name': report.report_date.strftime('%A'),
           'activity_description': row.activity_description,
           'shift': row.shift,
           'subcontractor': row.subcontractor_name,
           'headcount': row.headcount,
           'zone': row.zone,
           'block': row.block,
           'floor': row.floor,
           'location': row.location_detail,
           'quantity': float(row.quantity) if row.quantity is not None else None,
           'unit': row.unit,
           ...
       }
   ```
   فیلد **`source_discipline`** (دیسیپلین منبع) و فیلد **`parcel`** (قطعه) که در مدل وجود دارند، در این دیکشنری سریالایز **حذف** شده‌اند!
2. **فیلترهای اندپوینت و کنترلر:**  
   در تابع `activity_log_queryset` و اندپوینت `ActivityLogFilterOptionsView` در [`report_views.py:114-120`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/report_views.py#L114-L120)، هیچ امکانی برای فیلتر بر اساس دیسیپلین (`discipline`) یا قطعه (`parcel`) وجود ندارد.
3. **جدول فرانت‌اند در صفحه `project-activity-log.tsx`:**  
   در فایل [`apps/web/src/app/routes/project-activity-log.tsx:173-187`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/project-activity-log.tsx#L173-L187)، ستون‌های جدول عبارتند از:  
   `["تاریخ", "فعالیت", "شرح", "زون", "بلوک", "طبقه", "پیمانکار", "نفر", "مقدار", "گزارش"]`  
   ستون‌های **دیسیپلین** و **قطعه** در جدول وجود ندارند و فیلتربار بالا نیز فاقد دراپ‌داون دیسیپلین است.
4. **تأخیر در به‌روزرسانی ناشی از کش (فقدان Invalidation):**  
   اندپوینت `ActivityLogView` خروجی را به مدت ۳۰۰ ثانیه کش می‌کند. در زمان فراخوانی متد [`approve_report`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py#L63-L70)، هیچ مکانیزمی برای حذف و ابطال کلیدهای کش `activity_log` اجرا نمی‌شود. در نتیجه پس از تأیید گزارش روزانه، فعالیت‌های آن تا ۵ دقیقه در بانک فعالیت‌ها منعکس نمی‌شوند.

---

### G05 — P2 — عدم نمایش بنر سبز «تکمیل و تجمیع موفق تمام دیسیپلین‌ها» در فرانت‌اند

**شرح نیازمندی در SPEC-06 (داستان US-AG-05، سناریو ۲):**  
> «با فرض اینکه آخرین واحد غایب نیز ساب‌ریپورت خود را ارسال کند، هنگامی که صفحه گزارش باز شود، آنگاه بنر نقص پنهان شده و پیام سبز «تمام گزارش‌های دیسیپلین دریافت و تجمیع شدند» نمایش داده شود.»

**وضعیت در کد جاری:**  
در فایل [`apps/web/src/components/daily_reports/summary/IncompletenessBanner.tsx:38-40`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/summary/IncompletenessBanner.tsx#L38-L40):
```tsx
    if (completeness.state === "complete") {
      return null;
    }
```
و در انتهای کامپوننت:
```tsx
    if (!aggregation.is_partial) return null;
```
هنگامی که وضعیت تجمیع کامل است، این کامپوننت صرفاً `null` بازمی‌گرداند. هیچ پیام سبز یا نشانگر موفقیتی برای اطمینان‌بخشی به مدیر پروژه از دریافت کامل گزارشات رندر نمی‌شود.

---

### G06 — P2 — مغایرت در ثبت برچسب بازنویسی شرایط جوی (`overridden_by_manager`)

**شرح نیازمندی در SPEC-06 (داستان US-AG-04، سناریو ۲):**  
> «با فرض اینکه مدیر پروژه فیلد weather_override را با مقدار خاص تنظیم کند، هنگام تجمیع مجدد سیستم مقدار انتخابی مدیر را با برچسب `overridden_by_manager` حفظ کند.»

**وضعیت در کد جاری:**  
در تابع [`build_aggregation_meta`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/daily_report_aggregation.py#L169):
```python
'weather_source': 'override' if report and report.weather_override else 'derived',
```
برچسب ثبت‌شده در خروجی متادیتا صرفاً `'override'` است نه مقدار یکتای قراردادی `'overridden_by_manager'`. این عدم یکنواختی برچسب در تست‌ها و یکپارچگی میان‌سیستمی ایجاد مغایرت می‌کند.

---

### G07 — P2 — عدم ارائه تاریخ شمسی تجمیع در متادیتا و فقدان خلاصه‌سازی مصالح به تفکیک جنس

**شرح نیازمندی در SPEC-06 (دیاگرام بخش ۲ و داستان US-AG-02 سناریو ۳):**  
1. ثبت و ارائه زمان تجمیع با زمان جاری سرور و تاریخ شمسی در متادیتا.
2. خلاصه‌سازی مصالح در تب ۳ به صورت جمع مقادیر ورودی و مصرفی به تفکیک جنس کالا (نه صرفاً تفکیک رسید انبار از سایر ردیف‌ها).

**وضعیت در کد جاری:**  
1. متد `build_aggregation_meta` فیلد `aggregated_at` را صرفاً به فرمت ایزو میلادی (`2026-10-28T...Z`) برمی‌گرداند و تاریخ شمسی معادل در این بخش ارسال نمی‌شود.
2. متد `get_materials_summary` در [`field_reports/serializers.py:1286`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/serializers.py#L1286) صرفاً ردیف‌ها را به دو دسته `receipt` و `details` فیلتر می‌کند، اما مقادیر وزنی/تعدادی مصالح هم‌نام را با هم جمع (Aggregate by Material) نمی‌کند.

---

## ۳. ریشه‌یابی معماری و سیستم‌های درگیر (Architectural Root Cause Analysis)

شکاف‌های شناسایی‌شده ناشی از ۳ عامل معماری زیر هستند:
1. **جداسازی ناقص فاز تجمیع (Read-Only Projection) از فرم‌های سنتی (Editable Forms):**  
   با پیاده‌سازی `is_auto_summary` در فاز ۰۲۸، کامپوننت `DailyReportSummaryView` برای نمایش ایجاد شد، اما کامپوننت مادر `DailyReportForm` و صفحات روت `/edit` با این متغیر تطبیق داده نشدند و کاربران همچنان به فرم‌های تغییرناپذیر دسترسی مستقیم پیدا می‌کنند.
2. **کاهش ابعاد کلیدهای تجمیع در مدل داده‌ای (Lossy Rollup):**  
   در طراحی تجمیع نیروی انسانی، جدول `DailyReportLabor` به گونه‌ای طراحی شد که کلید آن تنها `(category, job_title)` بود؛ فیلد `contractor_ref` از مدل حذف شد که منجر به ادغام ناخواسته کارکرد پیمانکاران رقیب و مجزا در کارگاه گردید.
3. **جداماندگی ماژول گزارشات تحلیلی (`report_views.py`) از استانداردهای تجمیعی:**  
   ماژول `activity-log` در ابتدای پروژه به صورت مستقل پیاده شد و با تکامل مدل‌های جدید ساب‌ریپورت (که فیلدهای `source_discipline` و `parcel` را اضافه کردند)، به‌روزرسانی و همگام نشد.

---

## ۴. برنامه اقدام و ماتریس اولویت‌بندی رفع شکاف‌ها (Action Plan)

| کد شکاف | عنوان اقدام اصلاحی | اولویت | لایه آسیب‌دیده | فایل‌های هدف |
| :---: | :--- | :---: | :---: | :--- |
| **G01** | تضمین عملکرد `GET .../by-date/` در ایجاد خودکار شل (`200 OK`) هنگام عدم وجود گزارش و پشتیبانی از پارامتر `shift` | **P1** | Backend View & Service | `apps/api/core/field_reports/daily_report_views.py`, `urls.py` |
| **G02** | اصلاح کلید تجمیع نیروی انسانی به `(job_title, contractor)` و افزودن فیلد `contractor_ref` به مدل و جدول `DailyReportLabor` | **P1** | Backend Model & Aggregation Engine | `apps/api/core/field_reports/models.py`, `services/daily_report_aggregation.py` |
| **G03** | استانداردسازی کد خطای `derived_collection_read_only` و قفل‌گذاری/ریدایرکت کامل کامپوننت `DailyReportForm.tsx` در صورت `is_auto_summary` | **P1** | Backend View & Frontend Forms | `daily_report_views.py`, `apps/web/src/components/daily_reports/DailyReportForm.tsx` |
| **G04** | تکمیل فیلدهای `source_discipline` و `parcel` در `activity-log`، فعال‌سازی فیلترها در فرانت‌اند و اعمال Invalidation کش هنگام تأیید گزارش | **P1** | Backend Reporting & Frontend UI | `apps/api/core/field_reports/services/activity_log.py`, `report_views.py`, `project-activity-log.tsx` |
| **G05** | اضافه کردن رندر بنر سبز رنگ «تمام گزارش‌های دیسیپلین دریافت و تجمیع شدند» در کامپوننت `IncompletenessBanner.tsx` در وضعیت تکمیل | **P2** | Frontend Component | `apps/web/src/components/daily_reports/summary/IncompletenessBanner.tsx` |
| **G06** | یکپارچه‌سازی برچسب `overridden_by_manager` در خروجی متادیتای شرایط جوی و نمایش رسمی آن در رابط کاربری | **P2** | Backend Serializer & Frontend UI | `field_reports/services/daily_report_aggregation.py`, `DailyReportSummaryView.tsx` |
| **G07** | افزودن تاریخ شمسی تجمیع `aggregated_at_jalali` و قابلیت جمع مقادیر مصالح هم‌نام در سطح خلاصه مصالح | **P2** | Backend Serializer | `field_reports/serializers.py`, `services/daily_report_aggregation.py` |
