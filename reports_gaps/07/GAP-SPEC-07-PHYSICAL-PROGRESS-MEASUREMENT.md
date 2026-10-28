# سند نهایی ارزیابی شکاف‌ها و تحلیل انطباق: روش‌های اندازه‌گیری و پیشرفت فیزیکی ۴ گانه

**شناسه سند:** `GAP-SPEC-07-PHYSICAL-PROGRESS-MEASUREMENT`  
**سند مشخصات فنی هدف:** [`SPEC-07-PHYSICAL-PROGRESS-MEASUREMENT.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/atomic-specs/SPEC-07-PHYSICAL-PROGRESS-MEASUREMENT.md)  
**اسناد مرجع همبسته:**  
- [`docs/.../08-پیشرفت فیزیکی و گزارش‌های دوره‌ای.md`](file:///home/hossein/Desktop/projects/building-management/docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/08-پیشرفت%20فیزیکی%20و%20گزارش‌های%20دوره‌ای.md)  
- [`reports_documentation/04-.../schedule_and_progress_ENDPOINTS.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/04-periodic-weekly-monthly-reports/schedule_and_progress_ENDPOINTS.md)  
- [`specs/009-physical-progress-periodic-reports/spec.md`](file:///home/hossein/Desktop/projects/building-management/specs/009-physical-progress-periodic-reports/spec.md)  
- [`specs/009-physical-progress-periodic-reports/data-model.md`](file:///home/hossein/Desktop/projects/building-management/specs/009-physical-progress-periodic-reports/data-model.md)  
**تاریخ ارزیابی:** ۶ آبان ۱۴۰۵ (2026-10-28)  
**دامنه ارزیابی:**  
- بک‌اند:  
  - مدل‌ها و سرویس‌های اندازه‌گیری: [`apps/api/core/schedule/models.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/models.py)، [`apps/api/core/schedule/services/measurement_service.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/measurement_service.py)، [`apps/api/core/schedule/services/progress_service.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/progress_service.py)  
  - کنترلرها و اندپوینت‌ها: [`apps/api/core/schedule/measurement_views.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/measurement_views.py)، [`apps/api/core/schedule/progress_views.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/progress_views.py)  
  - جریان‌های گزارش روزانه و اعتبارسنجی: [`apps/api/core/sub_reports/services/section_validation.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/services/section_validation.py)، [`apps/api/core/field_reports/tasks.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/tasks.py)، [`apps/api/core/field_reports/services/__init__.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py)  
  - ماژول مالی و قراردادها: [`apps/api/core/contracts/services/ipc_service.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/contracts/services/ipc_service.py)  
- فرانت‌اند:  
  - کلاینت API و تایپ‌ها: [`apps/web/src/app/lib/api/progress.ts`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/api/progress.ts)  
  - ویرایشگر روش اندازه‌گیری و کشوی پیشرفت: [`apps/web/src/components/progress/MeasurementEditor.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/progress/MeasurementEditor.tsx)، [`apps/web/src/components/progress/ManualProgressDrawer.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/progress/ManualProgressDrawer.tsx)  
  - جدول پیشرفت ۴ گانه و داشبورد: [`apps/web/src/components/progress/ActivityProgressTable.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/progress/ActivityProgressTable.tsx)، [`apps/web/src/app/routes/project-progress.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/project-progress.tsx)  
  - فرم‌ها و کشوهای تعریف فعالیت در WBS: [`apps/web/src/components/activities/activity-drawer.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/activities/activity-drawer.tsx)  
**وضعیت کلی سند:** ⚠️ **دارای شکاف‌های انطباق بحرانی و نقض حاکمیت مالی (Fail - Action Required)**

---

## ۱. خلاصه‌ی اجرایی و تحلیل انطباق (Executive Summary)

سند مشخصات فنی اتمیک **`SPEC-07-PHYSICAL-PROGRESS-MEASUREMENT`** استانداردهای مهندسی سیستم Velora را برای تضمین دقت، صحت و اتکاپذیری پیشرفت فیزیکی پروژه‌ها تبیین می‌کند. این سند شامل ۳ داستان کاربری اتمیک کلیدی است:
1. **US-PR-01:** پیکربندی و اعتبارسنجی روش‌های سه‌گانه اندازه‌گیری فیزیکی فعالیت (`quantity_based`, `weighted_milestones`, `evidence_based`) و ممانعت قطعی از ثبت پیشرفت بدون تأیید روش.
2. **US-PR-02:** محاسبه و تفکیک پیشرفت ۴گانه (دوره‌ای، تجمعی ادعایی، برنامه‌ای، تأییدشده ناظر)، محاسبه انحراف (Variance)، و **الزام استناد مالی صورت‌وضعیت‌ها (IPC) صرفاً به پیشرفت تأییدشده**.
3. **US-PR-03:** ممانعت قاطع از عبور پیشرفت از سقف ۱۰۰٪ (رد با خطای ۴۰۰ بدون بستن خودکار/Clamping) و تفکیک شواهد تصویری از تأیید فنی مهندسی ناظر.

بررسی جامع کدبیس نشان می‌دهد اگرچه ساختار پایه مدل‌های نسخه روش اندازه‌گیری (`ActivityMeasurementDefinition`, `ActivityMeasurementVersion`) و فیلدهای چهارگانه در `ActivityProgress` در اسپرینت‌های قبلی ایجاد شده‌اند، اما **چندین شکاف عمیق، پرخطر و بحرانی** وجود دارد:

1. **نقض صریح حاکمیت مالی در صورت‌وضعیت‌ها (استفاده از پیشرفت ادعایی به جای تأییدشده):**  
   طبق سناریوی ۳ از US-PR-02، صورت‌وضعیت مالی (IPC) باید **صرفاً و منحصراً بر مبنای `approved_progress_pct`** محاسبه شود. در سرویس تولید ردیف‌های صورت‌وضعیت ([`contracts/services/ipc_service.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/contracts/services/ipc_service.py#L206-L214))، سیستم مستقیماً از فیلد `actual_progress` (پیشرفت تجمعی ادعاشده توسط پیمانکار) برای محاسبه احجام دوره و مبالغ پرداختی استفاده می‌کند! این یعنی اگر پیمانکار ادعای ۵۰٪ کند و ناظر تنها ۴۰٪ را تأیید کرده باشد، سیستم پول ۵۰٪ را آزاد می‌کند.
2. **عدم مسدودسازی ثبت پیشرفت روزانه برای فعالیت‌های فاقد روش اندازه‌گیری تأییدشده:**  
   طبق سناریوی ۳ از US-PR-01، سیستم باید تلاش برای ثبت پیشرفت روزانه روی فعالیت فاقد متدولوژی مصوب را با خطای `400 measurement_not_approved` متوقف کند. در حال حاضر، در اعتبارسنجی گزارش‌های روزانه ([`section_validation.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/services/section_validation.py#L271)) هیچ برداشتی از روش اندازه‌گیری وجود ندارد و در زمان تأیید گزارش روزانه ([`field_reports/tasks.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/tasks.py#L41-L47))، فعالیت فاقد روش تأییدشده صرفاً با یک لاگ نادیده گرفته می‌شود (Skipped)؛ گزارش تأیید می‌شود و کاربر با هیچ خطای ۴۰۰ مواجه نمی‌گردد!
3. **عدم اعتبارسنجی بلادرنگ پیشرفت بالای ۱۰۰٪ در گزارش‌های روزانه:**  
   برخلاف ثبت پیشرفت دستی که در لحظه بررسی می‌شود، در ثبت ردیف‌های فعالیت گزارش روزانه، اگر حجم تجمعی از حجم برآوردی کل فراتر رود، درخواست ثبت با `400 progress_exceeds_100` رد نمی‌شود. در عوض، گزارش ثبت و تأیید می‌شود و در تسک پس‌زمینه Celery محاسبه پیشرفت به دلیل خطا رد می‌شود بدون اینکه کاربر متوجه شود مقادیر روزانه نامعتبر هستند. همچنین پیام خطای سیستم با متن استاندارد مصوب تطابق ندارد.
4. **فقدان کامل اکشن تأیید فنی ناظر (`technicalApproveProgress`) در رابط کاربری:**  
   اندپوینت بک‌اند `POST /activities/{id}/technical-approve/` وجود دارد، اما در فرانت‌اند تابع `technicalApproveProgress` در فایل [`progress.ts`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/api/progress.ts#L372) به صورت یتیم رها شده و در هیچ کامپوننتی (جدول فعالیت‌ها، کارنامه یا کشوی ناظر) دکمه‌ای برای تأیید فنی صریح ناظر تعبیه نشده است!
5. **نقصان فاحش ویرایشگر روش اندازه‌گیری (`MeasurementEditor.tsx`):**  
   این کامپوننت فاقد هرگونه فیلد برای تعریف نقاط عطف وزنی (Milestones) و اوزان آن‌هاست (تضمین مجموع ۱۰۰٪)، فاقد فیلد ثبت قوانین مستندات (`evidence_rules`) است، و در روش مقداری نیز فاقد سلکتور واحد اندازه‌گیری (`unit_id`) است. علاوه بر این، این ویرایشگر در فرایند استاندارد تعریف فعالیت در WBS (`activity-drawer.tsx`) تعبیه نشده است.
6. **مغایرت در نام‌گذاری مقادیر Enum روش‌ها و عدم محاسبه حجم دوره (`period_quantity`):**  
   مقادیر اینام در بک‌اند `quantity` و `evidence_percent` هستند در حالی که استاندارد صریحاً `quantity_based` و `evidence_based` را معین کرده است. همچنین در محاسبه پیشرفت دوره، صرفاً درصد (`period_progress_pct`) بازمی‌گردد و حجم متناظر دوره (`period_quantity`) از قلم افتاده است.

---

### جدول ماتریس ارزیابی انطباق سناریوها

| شناسه داستان / سناریو | شرح در سند مشخصات (SPEC-07) | وضعیت انطباق | علت و خلاصه شواهد در کد جاری |
| :--- | :--- | :---: | :--- |
| **US-PR-01 (سناریو ۱)** | پیکربندی روش مقدارمحور (`quantity_based`) با حجم کل، واحد اندازه‌گیری و فرمول `(Qty_Act / Qty_Tot) * 100` | ⚠️ انطباق ناقص (P1) | فرمول محاسبه در تسک بک‌اند هست؛ اما اینام `quantity` است نه `quantity_based`. در فرانت‌اند `MeasurementEditor.tsx` سلکتور واحد اندازه‌گیری (`unit_id`) وجود ندارد و در کشوی تعریف فعالیت WBS نیز هیچ گزینه‌ای برای تعیین روش وجود ندارد. |
| **US-PR-01 (سناریو ۲)** | اعتبارسنجی نقاط عطف وزنی (`weighted_milestones`) و رد خطای `incomplete_measurement_basis` در صورت عدم تراز دقیق ۱۰۰٪ اوزان | ❌ شکاف UI و منطق (P1) | در بک‌اند شرط `abs(total - 1) > tolerance` چک می‌شود؛ اما در فرانت‌اند `MeasurementEditor.tsx` اصلاً فرمی برای افزودن مایلستون‌ها، نام و درصد آن‌ها وجود ندارد! مایلستون‌ها در جریان گزارش روزانه نیز پشتیبانی نمی‌شوند. |
| **US-PR-01 (سناریو ۳)** | ممانعت از ثبت پیشرفت دستی یا روزانه قبل از تصویب روش با خطای `400 measurement_not_approved` | ❌ شکاف بحرانی (P1) | برای پیشرفت دستی پیاده شده؛ اما برای ثبت ردیف‌های گزارش روزانه (`DailyReportActivity`) هیچ چک پیش‌فرضی وجود ندارد و در زمان تأیید گزارش روزانه، تسک Celery صرفاً آن را رد کرده و لاگ می‌زند، بدون بازگرداندن خطای ۴۰۰ به کاربر. |
| **US-PR-02 (سناریو ۱)** | محاسبه پیشرفت دوره (`period_progress_pct`) و حجم دوره (`period_quantity`) از گزارش‌های روزانه بازه | ⚠️ انطباق نسبی (P2) | درصد دوره (`period_progress_pct`) محاسبه می‌شود؛ اما فیلد حجم فیزیکی دوره (`period_quantity`) در خروجی اندپوینت و جدول فرانت‌اند محاسبه و ارائه نمی‌شود. |
| **US-PR-02 (سناریو ۲)** | مقایسه با خط‌مبنا و استخراج انحراف (`variance`) با رنگ‌آمیزی قرمز و برچسب تاخیر | ✅ منطبق | در `progress_service.py` محاسبه انحراف انجام می‌شود و در فرانت‌اند `ActivityProgressTable.tsx` با رنگ قرمز (`text-danger-600`) و بج «تأخیر» نمایش داده می‌شود. |
| **US-PR-02 (سناریو ۳)** | تفکیک پیشرفت ادعایی از تأییدشده ناظر، و **الزام استناد صورت‌وضعیت مالی به `approved_progress_pct`** | ❌ شکاف بحرانی و پرخطر (P1) | تفکیک در مدل و جدول UI وجود دارد؛ اما در [`ipc_service.py:211-214`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/contracts/services/ipc_service.py#L211-L214) محاسبه صورت‌وضعیت مالی پیمانکار مستقیماً روی `actual_progress` (پیشرفت ادعایی) انجام می‌شود و پیشرفت تأییدشده نادیده گرفته می‌شود! |
| **US-PR-03 (سناریو ۱)** | رد قطعی پیشرفت بالای ۱۰۰٪ (No Clamping) با خطای `400 progress_exceeds_100` و پیام خطای مصوب فارسی | ⚠️ انطباق ناقص (P1) | پیشرفت دستی رد می‌شود اما پیام خطا متفاوت است؛ در گزارش‌های روزانه هیچ مسدودسازی بلادرنگی با خطای ۴۰۰ رخ نمی‌دهد و خطا در تسک پس‌زمینه گم می‌شود. |
| **US-PR-03 (سناریو ۲)** | عدم کفایت عکس برای تأیید فنی (`photo_not_technical_approval`) و الزام امضای صریح کاربر ناظر | ❌ شکاف فرانت‌اند و تعاملی (P1) | اندپوینت بک‌اند خطای ۴۰۰ دارد، اما در فرانت‌اند متد `technicalApproveProgress` در هیچ کامپوننتی استفاده نشده و ناظر مقیم هیچ رابط کاربری برای اعمال تأییدیه فنی یا امضای پیشرفت ندارد. |

---

## ۲. یافته‌های تفصیلی و شواهد کد (Detailed Findings & Code Evidence)

### G01 — P1 — نقض صریح حاکمیت مالی در صورت‌وضعیت‌ها (`IPC`): محاسبه مبالغ بر پایه پیشرفت ادعایی به جای پیشرفت تأییدشده ناظر

**شرح نیازمندی در SPEC-07 (داستان US-PR-02، سناریو ۳):**  
> «با فرض اینکه پیمانکار پیشرفت تجمعی را ۵۰٪ ادعا کند اما ناظر تنها ۴۰٪ را تأیید فنی کرده باشد، آنگاه شاخص `cumulative_progress_pct = 50%` و شاخص `approved_progress_pct = 40%` ثبت شده و **مبنای صورت‌وضعیت مالی صرفاً عدد ۴۰٪ باشد**.»

**وضعیت در کد جاری:**  
در سرویس تولید خودکار اقلام صورت‌وضعیت در [`apps/api/core/contracts/services/ipc_service.py:206-214`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/contracts/services/ipc_service.py#L206-L214):
```python
            if progress_records.exists():
                latest = progress_records.order_by('-report_date').first()
                earliest_before = ActivityProgress.objects.filter(
                    activity_id=item.activity_id,
                    report_date__lt=ipc.period_start,
                ).order_by('-report_date').first()
                progress_start = float(earliest_before.actual_progress) if earliest_before else 0
                progress_end = float(latest.actual_progress)
                progress_delta = max(progress_end - progress_start, 0)
                qty_current = Decimal(str(progress_delta * float(item.activity.total_quantity or 0)))
```
**پیامدهای شکاف:**  
سیستم مستقیماً از `actual_progress` (پیشرفت گزارش‌شده توسط پیمانکار در کارگاه یا پیشرفت دستی) استفاده می‌کند و هیچ ارجاعی به `approved_progress` ندارد. اگر پیمانکار گزارش‌هایی ثبت کند که هنوز به تأیید ناظر نرسیده باشند (یا ناظر صریحاً آن‌ها را به دلیل ایراد فنی رد کرده باشد)، سیستم مالی پروژه این پیشرفت‌های تأییدنشده را مبنای پرداخت قرار داده و صورت‌وضعیت میلیاردی صادر می‌کند! این امر مغایر با اصول ابتدایی مدیریت ادعاها و کنترل قراردادها در پروژه‌های ساختمانی است.

---

### G02 — P1 — عدم اعتبارسنجی روش اندازه‌گیری هنگام ثبت پیشرفت روزانه و نادیده‌گرفتن خاموش در تسک Celery

**شرح نیازمندی در SPEC-07 (داستان US-PR-01، سناریو ۳):**  
> «با فرض اینکه برای فعالیتی روش اندازه‌گیری تعیین یا تأیید نشده باشد، هنگامی که کاربری تلاش کند پیشرفت دستی یا روزانه برای آن ثبت کند، آنگاه سرور با خطای `400 measurement_not_approved` عملیات را مسدود نماید.»

**وضعیت در کد جاری:**  
1. **در سطح ثبت ردیف‌های گزارش روزانه:**  
   در فایل [`apps/api/core/sub_reports/services/section_validation.py:271-275`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/services/section_validation.py#L271-L275):
   ```python
   if 'activity_ref' in validated:
       ref = validated['activity_ref']
       if ref is None or not _activity_active_and_within_project(ref, report.project_id):
           return [err('activity_ref', ACTIVITY_SCOPE_ERROR)]
   ```
   تنها چیزی که بررسی می‌شود، فعال بودن فعالیت در پروژه است. هیچ اعتبارسنجی‌ای در خصوص اینکه آیا این فعالیت روش اندازه‌گیری مصوب (`ActivityMeasurementVersion`) دارد یا خیر، انجام نمی‌شود.
2. **در سطح تسک بازسنجی پیشرفت پس از تأیید گزارش:**  
   در فایل [`apps/api/core/field_reports/tasks.py:39-47`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/tasks.py#L39-L47):
   ```python
   version = get_current_approved_version(activity)
   if version is None or version.method != MeasurementMethod.QUANTITY:
       reason = 'measurement_not_approved' if version is None else 'method_not_quantity'
       logger.info(
           'Skipping progress recalculation for activity %s (report %s): %s',
           activity.id, report_id, reason,
       )
       skipped.append({'activity_id': str(activity.id), 'code': reason})
       continue
   ```
**پیامدهای شکاف:**  
کاربر در ساب‌ریپورت و گزارش روزانه مقادیر اجراشده را وارد می‌کند، گزارش روزانه بدون کوچک‌ترین مانعی توسط سرپرستان تأیید می‌شود (`200 OK`)، اما در پس‌زمینه تسک Celery پیشرفت را ثبت نمی‌کند و آن را Skip می‌کند. کاربر هرگز خطای `400 measurement_not_approved` دریافت نمی‌کند و متوجه نمی‌شود که چرا پیشرفت فیزیکی فعالیت در داشبورد صفر مانده است.

---

### G03 — P1 — نشت پیشرفت بالای ۱۰۰٪ در گزارش‌های روزانه و عدم صدور خطای سنکرون `400 progress_exceeds_100` با پیام مصوب

**شرح نیازمندی در SPEC-07 (داستان US-PR-03، سناریو ۱):**  
> «با فرض اینکه پیشرفت تجمعی فعلی فعالیتی ۹۵٪ باشد، هنگامی که کاربری گزارشی با مقدار معادل ۱۰٪ پیشرفت جدید ثبت نماید (مجموع ۱۰۵٪)، آنگاه سیستم نباید مقدار را روی ۱۰۰٪ به طور خودکار ببندد (No Clamping)؛ بلکه باید با خطای `400 progress_exceeds_100` عملیات را به کلی رد کند و پیام دهد: «مجموع پیشرفت نمی‌تواند از ۱۰۰٪ بیشتر شود؛ لطفاً مقادیر اصلاح شوند».»

**وضعیت در کد جاری:**  
1. هنگام ارسال مقادیر اجرایی در ردیف‌های فعالیت گزارش‌های کارگاهی، هیچ بررسی تجمعی نسبت به سقف حجم کل برآوردی (`total_quantity`) صورت نمی‌گیرد.
2. اعتبارسنجی سقف ۱۰۰٪ به تسک ناهمگام Celery در [`tasks.py:61-70`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/tasks.py#L61-L70) موکول شده است:
   ```python
   try:
       progress_pct = compute_quantity_progress(activity, cumulative, version)
   except ProgressValidationError as exc:
       logger.warning(
           'Progress recalculation rejected for activity %s (report %s): %s',
           activity.id, report_id, exc.code,
       )
       skipped.append({'activity_id': str(activity.id), 'code': exc.code})
       continue
   ```
   در نتیجه، گزارش تأیید می‌شود و کاربر با خطای ۴۰۰ مسدود نمی‌شود؛ صرفاً در لاگ سرور ثبت شده و پیشرفت فعالیت آپدیت نمی‌شود.
3. در متد اعتبارسنجی پیشرفت دستی در [`measurement_service.py:374`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/measurement_service.py#L374):
   متن پیام خطای صادرشده عبارت است از:
   `'پیشرفت تجمعی بیش از ۱۰۰٪ است و تغییر مقدار تأییدشده‌ای آن را پوشش نمی‌دهد.'`
   که با متن الزامی استاندارد («مجموع پیشرفت نمی‌تواند از ۱۰۰٪ بیشتر شود؛ لطفاً مقادیر اصلاح شوند») مغایرت دارد.

---

### G04 — P1 — فقدان اکشن تعاملی تأیید فنی ناظر (`technicalApproveProgress`) در رابط کاربری کلاینت

**شرح نیازمندی در SPEC-07 (داستان US-PR-03، سناریو ۲):**  
> «عدم کفایت عکس برای تأیید فنی (Photo != Technical Approval): با فرض اینکه پیمانکار تصاویر متعدد از محل کارگاه بارگذاری کرده باشد، هنگامی که بخواهد بدون تأییدیه امضاشده ناظر مقیم، وضعیت را به approved تغییر دهد، آنگاه سرور با خطای `400 photo_not_technical_approval` مانع شود و اعلام کند که بارگذاری عکس صرفاً مستند پشتیبان است و تأییدیه صریح کاربر با نقش ناظر الزامی است.»

**وضعیت در کد جاری:**  
1. متد بک‌اند در [`apps/api/core/schedule/measurement_views.py:171-193`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/measurement_views.py#L171-L193) پیاده شده و شرط رد پایه تصویری (`basis == 'photo'`) را داراست.
2. تابع فراخوانی API در [`apps/web/src/app/lib/api/progress.ts:372`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/api/progress.ts#L372) وجود دارد:
   ```typescript
   export function technicalApproveProgress(projectId: string, activityId: string) {
     return apiJson(`${base(projectId)}/${activityId}/technical-approve/`, { method: "POST" });
   }
   ```
3. **شکاف کامل در UI:** این تابع در **هیچ نقطه‌ای از رابط کاربری فرانت‌اند** استفاده نشده است!
   - در جدول [`ActivityProgressTable.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/progress/ActivityProgressTable.tsx)، هیچ دکمه‌ای برای مهندس ناظر جهت کلیک روی «تأیید فنی» وجود ندارد.
   - در صفحه [`project-progress.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/project-progress.tsx)، هیچ فرمی یا دیالوگی برای بارگذاری تست/مستندات فنی و ثبت تأییدیه ناظر وجود ندارد.
   - ستون «تأییدشده٪» برای همیشه صفر یا مساوی پیشرفت اتوماتیک باقی می‌ماند، زیرا ناظر راهی برای تأیید فنی پیشرفت ثبت‌شده دستی ندارد.

---

### G05 — P1 — نقصان شدید ویرایشگر روش اندازه‌گیری (`MeasurementEditor.tsx`) در پشتیبانی از مایلستون‌ها و مستندات

**شرح نیازمندی در SPEC-07 (داستان US-PR-01، سناریوهای ۱ و ۲):**  
> «۱. روش مقدارمحور (`quantity_based`): فیلد حجم کل و واحد اندازه‌گیری فعال شده و پیشرفت از تقسیم مقادیر گزارشات بر حجم کل محاسبه شود.  
> ۲. روش نقاط عطف وزنی (`weighted_milestones`): فعالیت به گام‌های از پیش‌تعریف‌شده با وزن مشخص تقسیم شده و مجموع اوزان باید دقیقاً برابر ۱۰۰٪ باشد و در غیر این صورت خطای `incomplete_measurement_basis` صادر شود.»

**وضعیت در کد جاری:**  
در کامپوننت [`apps/web/src/components/progress/MeasurementEditor.tsx:127-156`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/progress/MeasurementEditor.tsx#L127-L156):
1. **عدم وجود گرید مایلستون‌ها:** زمانی که کاربر روش `weighted_milestones` را انتخاب می‌کند، هیچ فرم یا جدولی برای اضافه کردن گام‌ها (نام مایلستون و درصد وزنی آن) رندر نمی‌شود! در صورتی که کاربر دکمه تصویب را بزند، با خطای ۴۰۰ `incomplete_measurement_basis` مواجه می‌شود زیرا لیستی ارسال نشده است.
2. **عدم وجود فیلد قوانین مستندات:** زمانی که کاربر روش `evidence_percent` را انتخاب می‌کند، هیچ فیلد متنی برای ورود `evidence_rules` وجود ندارد.
3. **عدم وجود سلکتور واحد:** در روش مقداری، صرفاً فیلد عددی `totalQty` رندر می‌شود و سلکتور انتخاب واحد اندازه‌گیری (`unit_id`) وجود ندارد. اگر فعالیتی واحد نداشته باشد، تأیید آن در بک‌اند رد می‌شود.
4. **جداماندگی از کشوی WBS:** در کشوی اصلی ایجاد و ویرایش فعالیت‌های پروژه ([`activity-drawer.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/activities/activity-drawer.tsx))، بخش روش اندازه‌گیری پیشرفت اصلاً گنجانده نشده است.

---

### G06 — P2 — مغایرت در نام‌گذاری Enum روش‌ها و غیبت روش مایلستون در گزارش روزانه

**شرح نیازمندی در SPEC-07 (بخش ۲ و داستان US-PR-01):**  
نام‌گذاری کلیدهای روش اندازه‌گیری در استاندارد:
1. `quantity_based`
2. `weighted_milestones`
3. `evidence_based`

**وضعیت در کد جاری:**  
در مدل [`apps/api/core/schedule/models.py:265-269`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/models.py#L265-L269):
```python
class MeasurementMethod(models.TextChoices):
    QUANTITY = 'quantity', 'Quantity'
    WEIGHTED_MILESTONES = 'weighted_milestones', 'Weighted milestones'
    EVIDENCE_PERCENT = 'evidence_percent', 'Evidence percent'
```
- به جای `quantity_based` از `quantity` استفاده شده است.
- به جای `evidence_based` از `evidence_percent` استفاده شده است.
- علاوه بر این، در موتور گزارش روزانه ([`tasks.py:40`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/tasks.py#L40))، فقط روش `quantity` پشتیبانی می‌شود و در صورتی که فعالیتی دارای روش `weighted_milestones` باشد، گزارش‌های روزانه آن به کلی نادیده گرفته می‌شوند.

---

### G07 — P2 — عدم محاسبه و ارائه حجم فیزیکی دوره (`period_quantity`) در تفکیک ۴ گانه

**شرح نیازمندی در SPEC-07 (داستان US-PR-02، سناریو ۱):**  
> «با فرض اینکه در یک بازه هفتگی، ۳ گزارش روزانه تأییدشده با مقادیر ۲، ۳ و ۵ مترمکعب ثبت شده باشند، هنگامی که استعلام پیشرفت دوره گرفته می‌شود، آنگاه **مقدار پیشرفت دوره برابر با ۱۰ مترمکعب** و درصد متناظر آن در شاخص `period_progress_pct` درج شود.»

**وضعیت در کد جاری:**  
در متد [`get_activity_progress_breakdown`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/schedule/services/progress_service.py#L471-L509):
- درصد دوره (`period_progress_pct`) محاسبه می‌شود.
- حجم کل (`total_quantity`) و حجم تجمعی (`cumulative_quantity`) بازگردانده می‌شوند.
- اما **حجم فیزیکی انجام‌شده در دوره (`period_quantity`)** محاسبه نشده و در خروجی سریالایزر و ستون‌های جدول [`ActivityProgressTable.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/progress/ActivityProgressTable.tsx) غایب است.

---

## ۳. ریشه‌یابی معماری و سیستم‌های درگیر (Architectural Root Cause Analysis)

شکاف‌های شناسایی‌شده در سند پیشرفت فیزیکی از ۳ عامل ریشه‌ای ناشی می‌شوند:

1. **انزوای ماژول قراردادها و مالی (`contracts/ipc_service.py`) از سیستم حاکمیت پیشرفت (`schedule`):**  
   هنگام پیاده‌سازی سرویس صورت‌وضعیت‌ها (IPC)، توسعه‌دهندگان به سادگی به سراغ فیلد اولیه `actual_progress` رفتند، بدون توجه به اینکه در نظام مهندسی، پیشرفت اعلامی پیمانکار (Claimed Progress) تا پیش از امضا و تأیید مهندس ناظر (Approved Progress)، فاقد ارزش حقوقی و مالی برای پرداخت است.
2. **جدایی مسیر اعتبارسنجی گزارش‌های روزانه کارگاه از قوانین حاکمیت فعالیت‌های WBS:**  
   سرویس‌های ساب‌ریپورت و گزارش روزانه (`sub_reports` و `field_reports`) بدون در نظر گرفتن ملزومات روش‌های اندازه‌گیری فعالیت‌ها توسعه یافتند. در نتیجه، اعتبارسنجی‌ها به جای اینکه در مرز ورود داده (HTTP API) جلوی ثبت اطلاعات ناقص یا فراتر از سقف ۱۰۰٪ را بگیرند، به تسک‌های پس‌زمینه محول شدند که حاصل آن چشم‌پوشی خاموش از خطاها بود.
3. **پیاده‌سازی ناقص المان‌های رابط کاربری در اسپرینت‌های اولیه پیشرفت:**  
   ویرایشگر `MeasurementEditor` و اندپوینت `technical-approve` به صورت یک Mock اولیه بدون فرم‌های داینامیک برای مایلستون‌ها، مستندات و دکمه‌های اکشن تأییدیه رها شدند و تست‌های یکپارچگی کاربر نهایی برای بستن چرخه انجام نگرفت.

---

## ۴. برنامه اقدام و ماتریس اولویت‌بندی رفع شکاف‌ها (Action Plan)

| کد شکاف | عنوان اقدام اصلاحی | اولویت | لایه آسیب‌دیده | فایل‌های هدف |
| :---: | :--- | :---: | :---: | :--- |
| **G01** | اصلاح فوری سرویس صورت‌وضعیت برای استناد قطعی به `approved_progress` به جای `actual_progress` در محاسبه مقادیر و مبالغ پرداختی | **P1** | Backend Service (Contracts/IPC) | `apps/api/core/contracts/services/ipc_service.py` |
| **G02** | افزودن اعتبارسنجی داشتن روش اندازه‌گیری مصوب به `section_validation.py` و متوقف‌کردن ایجاد/ویرایش ردیف پیشرفت بدون متد مصوب با خطای `400 measurement_not_approved` | **P1** | Backend Service & Validation | `apps/api/core/sub_reports/services/section_validation.py`, `field_reports/tasks.py` |
| **G03** | بررسی سنکرون سقف حجم برآوردی (عدم عبور از ۱۰۰٪) در ثبت ردیف‌های گزارش روزانه با خطای `400 progress_exceeds_100` و یکپارچه‌سازی متن پیام فارسی خطا | **P1** | Backend Validation & Measurement Service | `apps/api/core/sub_reports/services/section_validation.py`, `schedule/services/measurement_service.py` |
| **G04** | ایجاد دیالوگ و دکمه «تأیید فنی ناظر» در جدول پیشرفت فعالیت‌ها و فعال‌سازی فراخوانی متد `technicalApproveProgress` با نقش مهندس ناظر | **P1** | Frontend UI & Components | `apps/web/src/components/progress/ActivityProgressTable.tsx`, `project-progress.tsx` |
| **G05** | بازطراحی `MeasurementEditor.tsx` شامل گرید پویا برای مایلستون‌های وزنی (تراز ۱۰۰٪)، فیلد مستندات فنی، سلکتور واحد، و تلفیق با کشوی تعریف فعالیت WBS | **P1** | Frontend UI & Components | `apps/web/src/components/progress/MeasurementEditor.tsx`, `components/activities/activity-drawer.tsx` |
| **G06** | همترازی مقادیر Enum روش‌ها (`quantity_based`, `weighted_milestones`, `evidence_based`) و پشتیبانی از مایلستون در گزارشات روزانه | **P2** | Backend Model & Serializers | `apps/api/core/schedule/models.py`, `schedule/services/measurement_service.py`, `progress.ts` |
| **G07** | محاسبه و ارسال شاخص حجم فیزیکی دوره (`period_quantity`) در خروجی اندپوینت breakdown و نمایش ستون آن در جدول پیشرفت | **P2** | Backend Service & Frontend Table | `apps/api/core/schedule/services/progress_service.py`, `ActivityProgressTable.tsx` |
