# گزارش بازرسی و برنامه زمان‌بندی واقع‌بینانه تحویل ولورا (Velora)

**وضعیت بازرس:** حسابرس مستقل فقط-خواندنی (Read-Only Auditor)  
**مرجع برنامه اولیه:** `/tmp/velora-original-schedule.txt` (استخراج‌شده از PDF اولیه پروژه)  
**وضعیت تست‌ها و CI:** بر اساس مستندات و کدهای موجود در مخزن (`.coverage`، فایل‌های تست pytest در مسیرهای `tests/` و فایل‌های `.github/workflows/ci.yml`) ارزیابی شده است. **مجموعه تست‌های سنگین در این نشست مجدداً اجرا نشده‌اند (Not Rerun)** و درصد پیشرفت‌ها از روی چک‌باکس‌های مستندات استنتاج نشده است.

---

## ۱. تفکیک لایه‌های پیشرفت: کد پیاده‌شده، تست‌های خودکار و پذیرش (UAT)

در ارزیابی مهندسی، وجود کد در مخزن به معنی اتمام کار نیست. تفکیک دقیق سه لایه به شرح زیر است:

| فاز | شرح فاز (WBS) | کد پیاده‌شده (Backend/Frontend) | وضعیت تست‌های خودکار (Automated Tests) | پذیرش کاربری (UAT) | وضعیت در برنامه اولیه |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A.2** | مدیریت پیمانکاران | پیاده‌سازی پایه در API و UI؛ فاقد جست‌وجو و خروجی | وجود تست در `subcontractors/tests` (اجرا نشده) | **۰٪** (عدم آزمون میدانی) | 0% Complete (۴ روز) |
| **A.3** | فهرست ذینفعان | پیاده‌سازی مدل، ماتریس و برنامه ارتباطی؛ فاقد کنترل تکرار و خروجی | تست در `projects/tests` موجود (اجرا نشده) | **۰٪** (عدم آزمون پذیرش) | 0% Complete (۳ روز) |
| **A.4** | مدیریت مکاتبات | مدل و اندپوینت پایه؛ عدم امکان آپلود UI و فقدان ارجاع داخلی | تست پایه در `documents/tests` (اجرا نشده) | **۰٪** (عدم آزمون پذیرش) | 0% Complete (۶ روز) |
| **A.5** | هزینه‌ها و جریان نقدی | مدل‌های CBS، بودجه، تعهدات و تراکنش نقدی؛ انقطاع تطبیق خودکار | تست‌های محاسباتی در `cost_control` و `cash_flow` (اجرا نشده) | **۰٪** (عدم تطبیق داده مالی واقعی) | 0% Complete (۷ روز) |
| **A.9** | اسناد و ترنسمیتال | نسخه اسناد موجود؛ **ترنسمیتال کاملاً غایب**؛ انفکاک از گردش کار | تست‌های بازبینی سند در `documents/tests` (اجرا نشده) | **۰٪** (فقدان کامل ماژول ترنسمیتال) | 0% Complete (۴ روز) |

---

## ۲. برنامه زمان‌بندی واقع‌بینانه بازبینی‌شده (تخمین نفر-روز کار باقی‌مانده)

برنامه اولیه مجموع این ۵ فاز را ۲۴ روز کاری در نظر گرفته بود، اما به دلیل غیبت ماژول ترنسمیتال، فقدان ارجاع مکاتبات، نبود خروجی‌ها و گسستگی میان هزینه‌ها و جریان نقد، زمان‌بندی واقع‌بینانه به تفکیک نفر-روز (Engineer-Days: خوش‌بینانه / محتمل / بدبینانه) به شرح زیر است:

| شناسه WBS | فاز و خروجی‌های باقی‌مانده | نفر-روز (حداقل) | نفر-روز (محتمل) | نفر-روز (حداکثر) | وابستگی‌ها (Dependencies) | منطق و توجیه مهندسی (Rationale) |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **A.2** | **مدیریت پیمانکاران**<br>(جست‌وجو، خروجی اکسل/PDF، پرونده و UAT) | ۲.۰ | ۳.۵ | ۵.۰ | ماژول قراردادها (`contracts`)، سرویس خروجی مشترک | افزودن فیلتر جست‌وجو در بک‌اند و فرانت‌اند، طراحی خروجی اکسل/PDF، اجرای آزمون پذیرش ثبت پرونده پیمانکار |
| **A.3** | **فهرست ذینفعان**<br>(کنترل تکرار، خروجی، دسته‌بندی و UAT) | ۱.۵ | ۲.۵ | ۴.۰ | ماژول پروژه‌ها (`projects`) | قفل کردن تکرار بر اساس نام/تلفن در سطح دیتابیس و سریالایزر، توسعه دکمه خروجی اکسل، بسط نقش‌ها |
| **A.4** | **مدیریت مکاتبات**<br>(ارجاع داخلی، آپلود فایل در UI، جست‌وجو و پیگیری) | ۳.۰ | ۴.۵ | ۶.۵ | زیرساخت فایل و MinIO، سیستم اعلانات | مدل‌سازی موجودیت ارجاع (`referred_to`/تاریخچه گردش)، اصلاح فرم UI به Multipart جهت آپلود نامه، اتصال سرچ‌بار |
| **A.5** | **هزینه‌ها و جریان نقدی**<br>(تطبیق مانده، اتصال پرداخت به کش‌فلو، اتصال CR به گردش کار) | ۵.۰ | ۸.۰ | ۱۲.۰ | `cost_control`، `cash_flow`، `contracts`، `workflow` | تطبیق دوطرفه پرداخت‌ها با جریان نقد، اتصال فرم درخواست تغییر بودجه به موتور Workflow، آزمون محاسبات مغایرت |
| **A.9** | **اسناد و ترنسمیتال**<br>(طراحی کامل ترنسمیتال، اتصال اسناد به موتور گردش کار) | ۶.۰ | ۹.۰ | ۱۴.۰ | `documents`، `workflow`، موتور گزارش‌ساز | پیاده‌سازی کامل مدل، اندپوینت و UI ترنسمیتال از صفر، اتصال چرخه تأیید اسناد به `WorkflowInstance` |
| **جمع** | **مجموع کار خالص باقی‌مانده** | **۱۷.۵** | **۲۷.۵** | **۴۱.۵** | — | **نیاز به حدود ۵ الی ۸ هفته تقویمی با احتساب تست و تثبیت** |

---

## ۳. بررسی ۱۴ شکاف ملموس (Concrete Gaps): کد، یکپارچگی UI/API و دسترسی‌ها

### حوزه A.2: مدیریت پیمانکاران (Contractors)
1. **فقدان جست‌وجوی متنی در API پیمانکاران:**
   در [views.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/subcontractors/views.py#L59-L66)، متد `_filter_queryset` تنها فیلترهای `status` و `discipline` را پشتیبانی می‌کند. هیچ پارامتر جست‌وجو (`search`) برای نام شرکت (`company_name`) یا شخص رابط وجود ندارد.
2. **فقدان ورودی جست‌وجو و خروجی در رابط کاربری:**
   در [project-subcontractors.tsx](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/project-subcontractors.tsx#L138-L160)، فقط دراپ‌داون وضعیت و چک‌باکس ریسک تعبیه شده و ورودی متنی برای سرچ یا دکمه خروجی اکسل/PDF (الزام بند A.2.2 جدول زمان‌بندی) وجود ندارد.
3. **انقطاع مجوزهای پیمانکاران از نقش‌های کارگاهی:**
   در [constants.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/permissions/constants.py#L20-L21) و [views.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/subcontractors/views.py#L30-L33)، دسترسی به پیمانکاران فرعی کاملاً به `view_contracts` و `edit_contracts` وابسته است؛ سرپرستان کارگاه بدون داشتن مجوز مالی قراردادها، امکان مشاهده پرونده فنی پیمانکاران را ندارند.

### حوزه A.3: فهرست ذینفعان (Stakeholders)
4. **فقدان کنترل تکرار (Duplicate Control) در سطح داده و اعتبارسنجی:**
   در مدل [models.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/projects/models.py#L542-L578) و سریالایزر [stakeholder_views.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/projects/stakeholder_views.py#L20-L67)، هیچ قید یکتایی (`unique_together`) یا متد `validate` برای جلوگیری از ثبت تکراری ذینفع در پروژه وجود ندارد (نقض صریح بند A.3.2).
5. **عدم تعبیه خروجی اکسل/PDF برای ذینفعان:**
   نه در اندپوینت‌های [stakeholder_views.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/projects/stakeholder_views.py#L69-L94) و نه در فرانت‌اند [project-stakeholders.tsx](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/project-stakeholders.tsx#L180-L250)، هیچ سازوکاری برای استخراج خروجی لیست ذینفعان پیاده‌سازی نشده است.
6. **محدودیت دسته‌بندی نقش‌ها در UI:**
   در [project-stakeholders.tsx](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/project-stakeholders.tsx#L28-L41)، نقش‌ها به ۳ مورد ثابت (پیمانکار، کارفرما، مشاور) محدود شده‌اند و نهادهای نظارتی، آزمایشگاه‌ها، همسایگان و ارگان‌های دولتی پوشش داده نشده‌اند.

### حوزه A.4: مدیریت مکاتبات (Correspondence)
7. **فقدان سازوکار ارجاع داخلی (Referral / Assignment):**
   در مدل [models.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/documents/models.py#L104-L135)، طرفین نامه صرفاً دو فیلد متنی ساده (`from_party` و `to_party`) هستند. هیچ فیلد کاربری یا تاریخچه ارجاع برای گردش نامه میان اعضای تیم پروژه وجود ندارد (نقض بند A.4.1).
8. **عدم امکان آپلود پیوست نامه از طریق رابط کاربری:**
   با وجود پشتیبانی بک‌اند از `MultiPartParser` در [views.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/documents/views.py#L115)، تابع کلاینت در [documents.ts](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/api/documents.ts#L109-L112) داده را به‌صورت JSON خام می‌فرستد و در دراور ثبت مکاتبه [project-documents.tsx](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/project-documents.tsx#L77-L91)، فیلد انتخاب فایل تعبیه نشده است.
9. **قطع ارتباط نوار جست‌وجوی اسناد با تب مکاتبات:**
   در [project-documents.tsx](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/project-documents.tsx#L60-L61)، استیت جست‌وجو فقط روی تب اسناد اعمال می‌شود و کوئری ارسالی تب مکاتبات [project-documents.tsx](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/project-documents.tsx#L130-L134) مقدار `search` را ارسال نمی‌کند.
10. **وابستگی پیگیری خودکار (Tracking) به ورکر Celery غیرفعال:**
    وظیفه پایش مهلت پاسخ مکاتبات در [tasks.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/documents/tasks.py#L11-L24) با Celery زمان‌بندی شده که در محیط محلی/ابری فعال نبوده و در UI سازوکار پیگیری دیگری جز چک‌باکس ساده تاخیر وجود ندارد.

### حوزه A.5: هزینه‌ها و جریان نقدی (Budgets/Cost/Payment/Cashflow)
11. **عدم تطبیق سیستمی پرداخت‌های هزینه با تراکنش‌های نقدی (Reconciliation Gap):**
    موجودیت‌های پرداخت در [models.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/cost_control/models.py#L192-L227) هیچ پیوند خودکاری با `CashTransaction` در [models.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/cash_flow/models.py#L38-L65) ندارند؛ ثبتیات دفتر کل هزینه‌ها با صورت گردش نقدینگی دچار انحراف مغایرت (Drift) می‌شوند.
12. **انفکاک تایید تغییرات بودجه از موتور گردش کار:**
    با وجود تعریف `WorkflowType.BUDGET_CHANGE` در [models.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/workflow/models.py#L18)، مدل `BudgetChangeRequest` در [models.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/cost_control/models.py#L409-L452) از فیلدهای سنتی `reviewed_by` استفاده کرده و نمونه‌ای در موتور جامع گردش کار ایجاد نمی‌کند.

### حوزه A.9: اسناد و ترنسمیتال (Documents/Workflows)
13. **فقدان کامل ماژول ترنسمیتال (Missing Transmittal System):**
    عنوان صریح فاز A.9 در برنامه اولیه «اسناد و ترنسمیتال» است. در سراسر کدهای [models.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/documents/models.py) و [routes.ts](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes.ts)، هیچ مدل داده‌ای، شماره‌گذاری، بسته مدارک و تاییدیه‌ای برای Transmittal وجود ندارد.
14. **انفکاک چرخه تأیید اسناد مهندسی از موتور گردش کار:**
    وضعیت مدرک در [models.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/documents/models.py#L55-L66) به یک اینام ساده (`DocumentStatus`) و فیلد تک‌کاربره `approver` محدود شده است. مراحل چندگانه بررسی، برگشت (Return/Reject)، تایید مشاور و تاریخچه لاگ در هماهنگی با [models.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/workflow/models.py#L116-L146) پیاده‌سازی نشده است.

---

## ۴. تفکیک دامنه ذینفعان: دامنه پایه اولیه (Baseline) در برابر ماژول ارتباطات توسعه‌یافته

برای جلوگیری از سردرگمی در برنامه‌ریزی، مرز این دو بخش تفکیک می‌شود:

```
┌─────────────────────────────────────────────────────────────┐
│ A.3 دامنه پایه برنامه اولیه (Schedule Baseline Scope)       │
│ • ثبت ذینفع، دسته‌بندی و اطلاعات تماس                        │
│ • کنترل عدم تکرار ذینفع در پروژه (Duplicate Check) [غایب]     │
│ • خروجی اکسل/PDF ذینفعان [غایب]                            │
│ • تأییدیه استقرار و ثبت پایه (UAT) [انجام‌نشده]             │
└──────────────────────────────┬──────────────────────────────┘
                               │ الحاق‌شده در مستندات بعدی
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ ماژول ارتباطات توسعه‌یافته (Expanded Communication Module)  │
│ • مدل برنامه ارتباطات: CommunicationPlan (کانال، فرکانس)    │
│ • ماتریس نفوذ / تمایل: StakeholderMatrixView                │
│ • فیلتر و محرمانگی تماس‌ها: view_sensitive_contacts          │
│ • تخصیص مالک ارتباط سازمانی: relationship_owner              │
└─────────────────────────────────────────────────────────────┘
```

- **کدهای موجود ماژول توسعه‌یافته:** در [models.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/projects/models.py#L586-L618) و [stakeholder_views.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/projects/stakeholder_views.py#L96-L144) پیاده شده است.
- **توصیه تحویل:** الزامات دامنه پایه (کنترل تکرار و خروجی اکسل) بدون نیاز به توسعه بیشتر ماژول ارتباطات باید در ۲.۵ روز کاری بسته شوند تا فاز A.3 تکمیل گردد.

---

## ۵. آزمون‌های پیشنهادی برای برنامه‌ریزی (Tests to be Scheduled)

برای نهایی‌سازی این فازها، نوشتن و اجرای این تست‌ها باید در اسپرینت قرار گیرد:
1. **آزمون اعتبارسنجی تکرار ذینفع:** تست اعتبارسنجی ثبت هم‌زمان دو ذینفع با نام یکسان در یک پروژه (`projects/tests/test_stakeholder_duplicate_guard.py`).
2. **آزمون یکپارچگی ارجاع مکاتبات:** تست انتساب مکاتبه به کاربر و فیلتر نامه‌های ارجاع‌شده به من (`documents/tests/test_correspondence_assignment.py`).
3. **آزمون آپلود پیوست مکاتبه:** تست ارسال فرم چندبخشی (Multipart) شامل فایل اسکن نامه به همراه متادیتا.
4. **آزمون تطبیق مانده نقد و هزینه:** آزمون اعتبارسنجی که پس از ثبت پرداخت قطعی در `cost_control`، تراکنش متناظر خروج نقد را در `cash_flow` تایید یا مغایرت را پرچم کند.
5. **آزمون چرخه رد و برگشت ترنسمیتال:** تست ایجاد ترنسمیتال جدید با ۳ سند، رد یک سند توسط مشاور و تغییر وضعیت ترنسمیتال به `Rejected/Revise`.

---

## ۶. ماتریس ریسک‌ها و شواهد مستند

| شناسه ریسک | شرح ریسک | شواهد مستند در کد / مخزن | شدت اثر | وضعیت قطعیت |
| :--- | :--- | :--- | :---: | :---: |
| **R-01** | رد پذیرش ترنسمیتال توسط کارفرما | عدم وجود هرگونه فایل یا مدل ترنسمیتال در `apps/api/core/documents/` | بحرانی | مستند با کد (قطعی) |
| **R-02** | مغایرت حسابداری میان هزینه و نقدینگی | انفکاک کامل مدل‌های `cost_control.Payment` و `cash_flow.CashTransaction` | بالا | مستند با کد (قطعی) |
| **R-03** | نقض محرمانگی قراردادها توسط ناظران کارگاه | وابستگی دسترسی پیمانکار به `view_contracts` در [subcontractors/views.py:31](file:///home/hossein/Desktop/projects/building-management/apps/api/core/subcontractors/views.py#L31) | متوسط | مستند با کد (قطعی) |
| **R-04** | شکست آپلود فایل در محیط فاقد MinIO | الزام ذخیره‌سازی ابری در [storage/s3.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/storage/s3.py) در صورت عدم اجرای داکر | متوسط | مستند با راهنما (قطعی) |
| **R-05** | آمادگی نهایی عملکردی بدون اجرای آزمون رگرسیون | عدم اجرای مجدد سوئیت تست‌های pytest در نشست‌های اخیر | متوسط | **نامشخص (Unknown)** تا زمان اجرای تست‌ها |
