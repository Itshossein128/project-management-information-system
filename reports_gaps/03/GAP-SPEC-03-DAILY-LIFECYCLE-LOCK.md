# سند نهایی گزارش شکاف‌ها و برنامه اقدام فنی: چرخه حیات، قفل، بازنگری و اصلاح گزارش روزانه

**شناسه سند:** `GAP-SPEC-03-DAILY-LIFECYCLE-LOCK`  
**سند مشخصات فنی هدف:** [`SPEC-03-DAILY-LIFECYCLE-LOCK.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/atomic-specs/SPEC-03-DAILY-LIFECYCLE-LOCK.md)  
**اسناد مرجع همبسته:**  
- [`01-.../07-گزارش روزانه کارگاه.md`](file:///home/hossein/Desktop/projects/building-management/docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/07-گزارش%20روزانه%20کارگاه.md)  
- [`03-.../field_reports_ENDPOINTS.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/03-daily-field-reports-and-apis/field_reports_ENDPOINTS.md)  
- [`03-.../spec_007.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/03-daily-field-reports-and-apis/spec_007.md)  
- [`specs/007-daily-report-gaps/contracts/status-and-unset-semantics.md`](file:///home/hossein/Desktop/projects/building-management/specs/007-daily-report-gaps/contracts/status-and-unset-semantics.md)  
- [`specs/007-daily-report-gaps/contracts/correction-requests.md`](file:///home/hossein/Desktop/projects/building-management/specs/007-daily-report-gaps/contracts/correction-requests.md)  
**تاریخ ارزیابی:** ۳ آبان ۱۴۰۵ (2026-10-25)  
**دامنه ارزیابی:** مدل‌ها، سرویس‌ها، سریالایزرها، اندپوینت‌ها و تست‌های بک‌اند (`apps/api/core/field_reports`) و کامپوننت‌ها و API کلاینت‌های فرانت‌اند (`apps/web/src/components/daily_reports`, `apps/web/src/app/lib/api/daily-reports.ts`)  

---

## ۱. خلاصه‌ی اجرایی و ماتریس انطباق (Executive Summary)

این سند شکاف‌ها و مغایرت‌های فنی میان سند مشخصات فنی اتمیک **`SPEC-03-DAILY-LIFECYCLE-LOCK`** و وضعیت جاری پیاده‌سازی در مخزن کد را با دقت بررسی و ثبت می‌کند. 

ماشین وضعیت، قفل‌گذاری هدر و ردیف‌های فرزند پس از تأیید نهایی، و فراخوانی تسک پس‌زمینه محاسبه پیشرفت فیزیکی از نظر معماری کلی با موفقیت پیاده شده‌اند؛ اما **چندین شکاف بحرانی** شامل:
1. **باگ تخریب داده در کپی نسخه اصلاحی (Data Loss on Clone):** عدم انتقال فیلدهای ضروری فعالیت‌ها مانند اکیپ، تعداد سرکارگر/کارگر، پیمانکار و پلاک در متد کلون ردیف‌های فرزند.
2. **فقدان فرآیند لغو درخواست اصلاح در فرانت‌اند (Missing Cancel UI):** نبود هرگونه متد API کلاینت یا دکمه رابط کاربری برای لغو درخواست اصلاح.
3. **نقص متادیتای نسخه‌ها (Missing Lineage Metadata):** عدم ارسال و عدم نمایش نام اصلاح‌کننده، دلیل اصلاح و تاریخ تأیید در تاریخچه نسخه‌ها.
4. **عدم انطباق کدهای خطای API و وضعیت HTTP:** ارسال `409 Conflict` به جای `400 Bad Request` در تصحیح تکراری و عدم استفاده از کدهای خطای مصوب (`quantity_unset_invalid`، `rejection_reason_min_length_10`، `report_not_in_submittable_state`).
5. **فقدان برچسب بصری «ثبت‌نشده» (Unset) با کادر هشدار در فرانت‌اند.**

### جدول ماتریس ارزیابی انطباق

| شاخص / داستان کاربری | عنوان سناریو در مشخصات فنی | وضعیت انطباق | شرح خلاصه وضعیت پیاده‌سازی و مغایرت‌ها |
| :--- | :--- | :---: | :--- |
| **US-DR-11 (سناریو ۱)** | ارسال گزارش پیش‌نویس (Submit) | ⚠️ انطباق نسبی | گردش کار انجام می‌شود؛ اما کد خطای رسمی `report_not_in_submittable_state` ارسال نمی‌گردد. |
| **US-DR-11 (سناریو ۲)** | شروع بررسی گزارش (Review) | ✅ منطبق | وضعیت به `under_review` تبدیل شده و کاربر و زمان بررسی ثبت می‌گردد. |
| **US-DR-11 (سناریو ۳)** | رد گزارش با دلیل الزامی (Reject) | ⚠️ شکاف خطا | شرط ۱۰ کاراکتر اعمال شده اما کدهای خطای `rejection_reason_min_length_10` و `rejection_reason_required` غایب هستند. |
| **US-DR-12 (سناریو ۱)** | تأیید نهایی و فعال‌سازی قفل (Approve) | ✅ منطبق | وضعیت `approved`، فیلد `is_locked=True` و تسک صف محاسبه پیشرفت فیزیکی به درستی فعال می‌شوند. |
| **US-DR-12 (سناریو ۲)** | قفل ویرایش مستقیم هدر (Header Lock) | ✅ منطبق | متد `PATCH` در وضعیت قفل با خطای `400 report_locked` به درستی مسدود می‌شود. |
| **US-DR-12 (سناریو ۳)** | قفل افزودن/ویرایش/حذف ردیف‌های فرزند | ✅ منطبق | هرگونه ایجاد، ویرایش یا حذف در ردیف‌های فرزند در گزارش قفل با خطای `400 report_locked` مسدود است. |
| **US-DR-13 (سناریو ۱)** | ثبت درخواست اصلاح و کلون گزارش | ❌ باگ تخریب داده | کپی هدر انجام می‌شود اما فیلدهای کلیدی فعالیت‌ها (`crew_name`, `foreman_count`, `worker_count`, `parcel`, `contractor_ref_id`) در کلون کپی نشده و حذف می‌شوند. |
| **US-DR-13 (سناریو ۲)** | لغو درخواست اصلاح (Cancel) | ❌ شکاف فرانت‌اند | اندپوینت در بک‌اند وجود دارد؛ اما در فرانت‌اند هیچ تابع API و هیچ دکمه/المان رابط کاربری برای لغو وجود ندارد. |
| **US-DR-13 (سناریو ۳)** | مشاهده تاریخچه نسخه‌ها (Versions List) | ❌ نقص شدید داده | نام اصلاح‌کننده و دلیل اصلاح نه در سریالایزر بک‌اند و نه در فرانت‌اند وجود ندارد. تاریخ تأیید نیز در UI رندر نمی‌شود. |
| **US-DR-13 (خطاهای API)** | کدهای خطای تصحیح | ⚠️ عدم تطابق HTTP | برای درخواست باز تکراری، به جای `400 correction_already_open`، کد `409 Conflict` بازگردانده می‌شود. |
| **US-DR-14 (سناریو ۱)** | ممانعت از ارسال با کارکرد نامشخص | ⚠️ عدم تطابق خطا | ولیدیشن در سابمیت کد خطای `quantity_unset_invalid` و متن مصوب سند را صادر نمی‌کند. |
| **US-DR-14 (سناریو ۲)** | پذیرش مقدار صفر (`0.00`) به عنوان کارکرد | ✅ منطبق | تمایز صفر عددی و مقدار `null` در لایه مدل و سریالایزر رعایت شده است. |
| **US-DR-14 (سناریو ۳)** | تمایز بصری Unset در فرانت‌اند | ❌ شکاف کامل UI | برچسب خاکستری «ثبت‌نشده» (Unset) با کادر هشدار در جدول ردیف‌ها پیاده نشده است. |

---

## ۲. ارزیابی دقیق بندهای سند مشخصات فنی (Detailed Story Review)

---

### بخش ۲.۱: داستان کاربری US-DR-11 (گردش کار چندمرحله‌ای تأیید و رد)

#### سناریو ۱: ارسال گزارش پیش‌نویس (Submit)
- **الزام سند:**  
  با فرض وضعیت `draft` یا `rejected`، کاربر با مجوز `edit_reports` گزارش را ارسال کند؛ وضعیت به `submitted` تغییر یافته و کاربر/تاریخ ثبت شود. در صورت عدم انطباق وضعیت، کد خطای `400 report_not_in_submittable_state` بازگردد.
- **موقعیت در کد:**  
  [`apps/api/core/field_reports/daily_report_views.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L261-L274) در متد `_submit` و سرویس [`submit_report`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py#L28-L46).
- **شکاف و مغایرت:**  
  در `_submit` خطا به شکل زیر صادر می‌شود:
  ```python
  if instance.status not in EDITABLE_STATUSES:
      raise ValidationError('فقط گزارش‌های پیش‌نویس یا رد شده قابل ارسال هستند')
  ```
  استثنای فوق فاقد کد استاندارد `code='report_not_in_submittable_state'` است و کلاینت خطای متنی عمومی دریافت می‌کند.

#### سناریو ۲: شروع بررسی گزارش (Review)
- **الزام سند:**  
  با فرض وضعیت `submitted`، ناظر دارای `approve_reports` وضعیت را به `under_review` تغییر داده و متادیتا ثبت شود.
- **موقعیت در کد:**  
  [`apps/api/core/field_reports/daily_report_views.py:277-286`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L277-L286) و [`services.review_report`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py#L48-L61).
- **وضعیت:**  
  کاملاً منطبق بر مشخصات فنی است. وضعیت به `under_review` تغییر یافته، `reviewed_by` و `reviewed_at` ثبت شده و یادداشت ناظر به متادیتای گزارش اضافه می‌گردد. در فرانت‌اند نیز دکمه «شروع بررسی» در [`ApprovalStatusBar.tsx:89-100`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/ApprovalStatusBar.tsx#L89-L100) تنها برای کاربران مجاز در وضعیت `submitted` نمایش داده می‌شود.

#### سناریو ۳: رد گزارش با ثبت دلیل الزامی (Reject)
- **الزام سند:**  
  با فرض وضعیت `submitted` یا `under_review`، ثبت متن دلیل کمتر از ۱۰ کاراکتر با خطای `rejection_reason_min_length_10` و فیلد خالی با `400 rejection_reason_required` رد شود. در صورت ورود دلیل معتبر (حداقل ۱۰ کاراکتر)، وضعیت به `rejected` تبدیل شود.
- **موقعیت در کد:**  
  [`apps/api/core/field_reports/daily_report_views.py:298-305`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L298-L305) و سرویس [`reject_report`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py#L84-L97).
- **شکاف و مغایرت:**  
  پیاده‌سازی بک‌اند به این صورت است:
  ```python
  reason = (request.data.get('reason') or '').strip()
  if len(reason) < 10:
      raise ValidationError({'reason': 'دلیل رد باید حداقل ۱۰ کاراکتر باشد'})
  ```
  1. هیچ تفکیکی میان ارسال نشدن دلیل (`rejection_reason_required`) و ارسال متن کوتاه (`rejection_reason_min_length_10`) وجود ندارد.
  2. استثنا فاقد پارامتر `code` است و کدهای استاندارد تصریح‌شده در سند صادر نمی‌شوند.

---

### بخش ۲.۲: داستان کاربری US-DR-12 (قفل شدن خودکار گزارش - Immutability & Lock)

#### سناریو ۱: تأیید نهایی و فعال شدن قفل
- **الزام سند:**  
  اندپوینت `POST .../daily-reports/{pk}/approve/` گزارش در وضعیت `under_review` یا `submitted` را به `approved` تبدیل کرده، فیلد `is_locked=True` را تنظیم نموده و روال محاسبه مجدد پیشرفت فیزیکی دوره‌ای را فراخوانی کند.
- **موقعیت در کد:**  
  [`DailyReportViewSet._approve`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L288-L296)، مدل [`DailyReport.is_locked`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/models.py#L259-L260)، سرویس [`approve_report`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py#L63-L82) و تسک [`_enqueue_progress_recalc`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/__init__.py#L477-L484).
- **وضعیت:**  
  کاملاً منطبق بر سند است. تسک Celery به شناسه `recalculate_activity_progress.delay` به صف ارسال می‌شود و وضعیت گزارش قفل می‌گردد.

#### سناریو ۲ و ۳: ممانعت از ویرایش هدر و ردیف‌های فرزند
- **الزام سند:**  
  ارسال هرگونه درخواست `PATCH` به هدر گزارش قفل یا تلاش برای ایجاد، ویرایش یا حذف ردیف‌ها در فعالیت‌ها، نیروی انسانی، مصالح و ماشین‌آلات، با خطای `400 report_locked` متوقف شود و هیچ تغییری در پایگاه داده اعمال نگردد.
- **موقعیت در کد:**  
  [`daily_report_views.py:partial_update`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L226-L230) و [`DailyReportChildViewSet._assert_editable`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L479-L487).
- **وضعیت:**  
  کاملاً منطبق است:
  ```python
  if report.status == ReportStatus.APPROVED:
      raise ValidationError({'detail': 'گزارش قفل‌شده است', 'code': 'report_locked'})
  ```
  همچنین در فرانت‌اند در کامپوننت [`DailyReportForm.tsx:170`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/DailyReportForm.tsx#L170)، فیلدها و گریدها در حالت `readOnly` قرار می‌گیرند.

---

### بخش ۲.۳: داستان کاربری US-DR-13 (درخواست اصلاح گزارش قفل‌شده و نسخه‌بندی)

#### سناریو ۱: ثبت درخواست اصلاح و کلون گزارش
- **الزام سند:**  
  با فرض گزارش تأییدشده و جاری (`approved` و `is_current=True`) و نبود درخواست باز دیگر، ثبت درخواست با ذکر دلیل (حداقل ۱۰ کاراکتر) صورت گیرد. یک گزارش کلون‌شده جدید با `version_number = version_number + 1` در وضعیت `draft` با همان `lineage_id` ایجاد شده و نسخه قبلی موقتاً `is_current=False` شود.
- **موقعیت در کد:**  
  [`correction_service.py:open_correction`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/correction_service.py#L73-L132) و [`daily_report_views.py:correction_requests`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L346-L365).
- **شکاف‌های شناسایی‌شده:**
  1. **باگ بحرانی تخریب داده در کلون ردیف‌های فعالیت کارگاه:**  
     در نگاشت کپی ردیف‌های فرزند [`CHILD_CLONE_SPECS`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/correction_service.py#L28-L62)، فیلدهای کلیدی مدل [`DailyReportActivity`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/models.py#L282-L300) که در تحولات معماری سامانه افزوده شده‌اند از قلم افتاده‌اند:
     - `contractor_ref_id` (پیمانکار ارجاعی سامانه پیمانکاران)
     - `crew_name` (نام اکیپ اجرایی)
     - `foreman_count` (تعداد سرکارگر)
     - `worker_count` (تعداد کارگر)
     - `parcel` (پلاک/محدوده اجرایی)
     در نتیجه با ایجاد درخواست اصلاح، این فیلدها در نسخه جدید `null` شده و داده‌های ارزشمند کارگاه به صورت خاموش از بین می‌روند.
  2. **عدم پوشش سایر سکشن‌های داده:**  
     مدل‌های `DailyReportMachineryRow`، `DailyReportGeneralActivity` و `DailyReportVisit` اصلاً در تاپل `CHILD_CLONE_SPECS` لحاظ نشده‌اند و ردیف‌های آن‌ها کلون نمی‌شوند.

#### سناریو ۲: رد یا انصراف از درخواست اصلاح (Cancel)
- **الزام سند:**  
  با ارسال درخواست به `POST .../correction-requests/{id}/cancel/`، پیش‌نویس نسخه ویرایش حذف شده و نسخه تأییدشده قبلی مجدداً به عنوان نسخه جاری (`is_current=True`) بازیابی شود.
- **موقعیت در کد:**  
  بک‌اند: [`DailyReportCorrectionCancelView`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L419-L436) در آدرس `/api/v1/projects/{project_pk}/correction-requests/{correction_id}/cancel/`.  
  فرانت‌اند: [`ApprovalStatusBar.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/ApprovalStatusBar.tsx) و [`daily-reports.ts`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/api/daily-reports.ts).
- **شکاف‌های شناسایی‌شده:**  
  1. در فایل فرانت‌اند `daily-reports.ts` متد API برای فراخوانی اندپوینت Cancel تعبیه نشده است.
  2. در رابط کاربری فرم گزارش و نوار وضعیت، هیچ دکمه یا دیالوگی برای «انصراف از درخواست اصلاح» وجود ندارد. اگر کاربری درخواست اصلاح ثبت کند، تا زمانی که آن را تأیید نهایی یا دیتابیس را دستی دستکاری نکند، راهی برای لغو و بازگرداندن نسخه قبلی در UI ندارد.

#### سناریو ۳: مشاهده تاریخچه نسخه‌ها (Versions List)
- **الزام سند:**  
  فراخوانی `GET .../daily-reports/{pk}/versions/` باید تمامی نسخه‌های زنجیره (`lineage_id`) را همراه با **شماره نسخه، نام اصلاح‌کننده، دلیل اصلاح و تاریخ تأیید** لیست کند.
- **موقعیت در کد:**  
  بک‌اند: [`DailyReportVersionSerializer`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/serializers.py#L1420-L1437).  
  فرانت‌اند: [`ApprovalStatusBar.tsx:244-280`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/ApprovalStatusBar.tsx#L244-L280).
- **شکاف‌های شناسایی‌شده:**  
  1. **نقص متادیتا در بک‌اند:** سریالایزر `DailyReportVersionSerializer` صرفاً فیلدهای مدل `DailyReport` را برمی‌گرداند. فیلدهای **نام اصلاح‌کننده (modifier name)** و **دلیل اصلاح (correction reason)** در آن وجود ندارند. دلیل اصلاح اساساً در مدل `DailyReportCorrectionRequest` ذخیره شده و به این خروجی متصل (Join) نشده است.
  2. **نقص نمایش در فرانت‌اند:** در پنل بازشونده نسخه‌ها در UI، صرفاً شماره نسخه، فلگ جاری و برچسب وضعیت رندر می‌شود:
     ```tsx
     <span>
       نسخه {v.version_number}
       {v.is_current ? " (جاری)" : ""}
       {" · "}
       {STATUS_LABELS[v.status]}
       {v.is_locked ? " · قفل" : ""}
     </span>
     ```
     نه نام اصلاح‌کننده، نه دلیل اصلاح و حتی نه تاریخ تأیید نسخه در UI رندر نمی‌شوند.

#### کدهای خطای درخواست اصلاح
- **الزام سند:**  
  - `400 report_not_locked`
  - `400 correction_already_open`
- **موقعیت در کد:**  
  [`correction_service.py:90`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/correction_service.py#L90) و [`config/exceptions.py:19-20`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/config/exceptions.py#L19-L20).
- **شکاف و مغایرت:**  
  سرویس تصحیح در هنگام وجود درخواست باز، استثنای `ConflictError` بالا می‌آورد:
  ```python
  if open_exists:
      raise ConflictError(detail='درخواست اصلاح باز برای این گزارش وجود دارد', code='correction_already_open')
  ```
  از آنجا که `ConflictError` دارای `status_code = status.HTTP_409_CONFLICT` است، خطای شبکه با کد وضعیت **`409 Conflict`** ارسال می‌شود؛ در حالی که سند مشخصات فنی به صراحت کد وضعیت **`400`** را مقرر کرده است (`400 correction_already_open`).

---

### بخش ۲.۴: داستان کاربری US-DR-14 (تمایز صریح میان مقدار صفر و ثبت‌نشده)

#### سناریو ۱: ممانعت از ارسال گزارش با فیلدهای احجام نامشخص
- **الزام سند:**  
  در صورتی که ردیف فعالیتی افزوده شده ولی فیلد کارکرد مقداردهی نشده باشد (`null`)، هنگام Submit سیستم باید با خطای **`quantity_unset_invalid`** مانع شده و پیام دهد:
  **«مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود»**.
- **موقعیت در کد:**  
  [`daily_report_views.py:_validate_report_ready_for_submit`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L73-L97).
- **شکاف و مغایرت:**  
  1. کد خطای استاندارد `quantity_unset_invalid` صادر نمی‌شود؛ بلکه آرایه‌ای متنی درون کلید `submit_validation` بازگردانده می‌شود (`{'submit_validation': [...]}`).
  2. متن خطای تولیدشده با متن تصریح‌شده در سند مغایرت دارد:
     - متن فعلی کد: `ردیف فعالیت {idx}: در حالت اندازه‌گیری شده، مقدار باید ثبت شود`
     - متن مصوب سند: `«مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود»`

#### سناریو ۲: پذیرش عدد صفر به عنوان مقدار معتبر
- **الزام سند:**  
  مقدار صریح `0.00` باید به عنوان کارکرد واقعی و معتبر پذیرفته شود و گزارش بدون خطا ثبت و سابمیت شود.
- **موقعیت در کد:**  
  [`test_core_principles_unset_vs_zero.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/tests/test_core_principles_unset_vs_zero.py#L18-L51) و [`common/unset.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/common/unset.py).
- **وضعیت:**  
  کاملاً منطبق بر مشخصات است.

#### سناریو ۳: نمایش بصری متمایز در فرانت‌اند
- **الزام سند:**  
  در صورت مقداردهی نشدن فیلد مقدار یک ردیف، هنگام رندر جدول ردیف‌ها، **به جای نمایش `0`، برچسب خاکستری‌رنگ «ثبت‌نشده» (Unset) با کادر هشدار نمایش داده شود**.
- **موقعیت در کد:**  
  [`EditableGrid.tsx:433-453`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/EditableGrid.tsx#L433-L453) و [`DailyReportSummaryView.tsx:704`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/summary/DailyReportSummaryView.tsx#L704).
- **شکاف و مغایرت:**  
  در گرید ویرایشی مقدار صرفاً خالی رها می‌شود (`""`) و در صفحه خلاصه گزارش روزانه مقدار `null` به صورت خط تیره معمولی (`r.quantity ?? "—"`) نمایش داده می‌شود. هیچ برچسب خاکستری با عنوان «ثبت‌نشده» (Unset) و کادر هشدار در رابط کاربری پیاده نشده است.

---

## ۳. جدول تفصیلی ارجاعات کدبیس و شکاف‌ها

| ردیف | رده شکاف | فایل و موقعیت کد | الزام در SPEC-03 | رفتار فعلی در کد |
| :---: | :--- | :--- | :--- | :--- |
| **۱** | بک‌اند / دیتابیس | [`correction_service.py:28-62`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/correction_service.py#L28-L62) | کلون کامل فعالیت‌ها در تصحیح (US-DR-13 سناریو ۱) | حذف فیلدهای `crew_name`, `foreman_count`, `worker_count`, `parcel`, `contractor_ref_id` |
| **۲** | فرانت‌اند / API | [`daily-reports.ts:630-647`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/api/daily-reports.ts#L630-L647) | متد لغو تصحیح (US-DR-13 سناریو ۲) | تابع `cancelCorrectionRequest` وجود ندارد |
| **۳** | فرانت‌اند / UI | [`ApprovalStatusBar.tsx:125-145`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/ApprovalStatusBar.tsx#L125-L145) | دکمه و جریان لغو درخواست اصلاح (US-DR-13 سناریو ۲) | هیچ دکمه‌ای برای Cancel تعبیه نشده است |
| **۴** | بک‌اند / داده | [`serializers.py:1420-1437`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/serializers.py#L1420-L1437) | متادیتای نسخه‌ها (US-DR-13 سناریو ۳) | فیلدهای `modifier_name` و `correction_reason` وجود ندارند |
| **۵** | فرانت‌اند / UI | [`ApprovalStatusBar.tsx:251-278`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/ApprovalStatusBar.tsx#L251-L278) | نمایش کامل مشخصات نسخه (US-DR-13 سناریو ۳) | نام اصلاح‌کننده، دلیل و تاریخ تأیید نمایش داده نمی‌شوند |
| **۶** | بک‌اند / HTTP | [`correction_service.py:90`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/services/correction_service.py#L90) | خطای `400 correction_already_open` | پرتاب استثنای `ConflictError` با کد وضعیت `409` |
| **۷** | بک‌اند / اعتبارسنجی | [`daily_report_views.py:62-97`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L62-L97) | خطای `quantity_unset_invalid` و متن مصوب (US-DR-14) | ارسال `submit_validation` با متن مغایر و بدون کد |
| **۸** | بک‌اند / اعتبارسنجی | [`daily_report_views.py:261-267`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L261-L267) | خطای `400 report_not_in_submittable_state` (US-DR-11) | عدم ارسال فیلد `code` در استثنای ولیدیشن سابمیت |
| **۹** | بک‌اند / اعتبارسنجی | [`daily_report_views.py:298-305`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/daily_report_views.py#L298-L305) | خطاهای `rejection_reason_*` (US-DR-11 سناریو ۳) | عدم ارسال کدهای استاندارد در رد گزارش |
| **۱۰** | فرانت‌اند / UI | [`DailyReportSummaryView.tsx:704`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/summary/DailyReportSummaryView.tsx#L704) | برچسب خاکستری Unset با کادر هشدار (US-DR-14) | نمایش خط تیره ساده `"—"` به جای برچسب Unset |

---

## ۴. برنامه اقدام و نقشه راه اصلاحات (Action Plan)

برای رفع کامل شکاف‌های فوق و انطباق ۱۰۰ درصدی با `SPEC-03-DAILY-LIFECYCLE-LOCK`، اقدامات فنی زیر به ترتیب اولویت توصیه می‌شود:

### فاز ۱: اصلاحات بحرانی یکپارچگی داده (Data Integrity & Lineage)
1. **اصلاح تاپل `CHILD_CLONE_SPECS` در `correction_service.py`:**
   افزودن فیلدهای `'crew_name'`, `'foreman_count'`, `'worker_count'`, `'parcel'`, `'contractor_ref_id'` به مشخصات کلون `DailyReportActivity` و اضافه کردن مدل‌های `DailyReportMachineryRow`، `DailyReportGeneralActivity` و `DailyReportVisit` به روال کلون.
2. **اصلاح خروجی اندپوینت نسخه‌ها (`DailyReportVersionSerializer`):**
   اضافه کردن متد فیلدهای `modifier_name` (برگرفته از کاربر اصلاح‌کننده یا سازنده نسخه) و `correction_reason` (از طریق کوئری متناظر در `DailyReportCorrectionRequest`) به سریالایزر نسخه‌ها.
3. **تغییر کد وضعیت HTTP تصحیح باز:**
   تغییر استثنای `open_correction` برای `correction_already_open` از `ConflictError` (409) به `ValidationError(..., code='correction_already_open')` (400) جهت انطباق با قرارداد API مشخصات فنی.

### فاز ۲: تکمیل قابلیت‌های گردش کار در فرانت‌اند (Workflow UI)
1. **پیاده‌سازی لغو درخواست اصلاح:**
   - افزودن متد `cancelCorrectionRequest(projectId, correctionId)` در `apps/web/src/app/lib/api/daily-reports.ts`.
   - افزودن دکمه «انصراف از درخواست اصلاح» در نوار وضعیت تأیید (`ApprovalStatusBar.tsx`) زمانی که نسخه جاری یک پیش‌نویس ناشی از تصحیح است (`report.version_number > 1` و `status === 'draft'`).
2. **غنی‌سازی پنل تاریخچه نسخه‌ها:**
   رندر کامل متادیتا شامل نام اصلاح‌کننده، متن دلیل اصلاح و تاریخ تأیید رسمی نسخه در لیست کشویی نسخه‌ها.

### فاز ۳: استانداردسازی اعتبارسنجی و رابط کاربری Unset
1. **اصلاح ساختار خطای Submit در بک‌اند:**
   ارسال ساختاریافته خطای `quantity_unset_invalid` به همراه پیام فارسی استاندارد: `«مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود»`.
2. **افزودن کدهای خطای `report_not_in_submittable_state` و `rejection_reason_min_length_10` و `rejection_reason_required`:**
   تزریق پارامتر `code` به استثناهای ولیدیشن در اکشن‌های `_submit` و `_reject`.
3. **طراحی و پیاده‌سازی کامپوننت `UnsetQuantityBadge` در فرانت‌اند:**
   نمایش برچسب خاکستری هشداردهنده «ثبت‌نشده» در ستون مقدار جداول فعالیت‌ها در زمان `quantity == null` یا `quantity_measured === false`.
