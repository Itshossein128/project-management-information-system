# پرامپت ماژولار ۱: اصلاح باگ کلونینگ، گردش کار انصراف از اصلاح و تاریخچه نسخه‌ها

**شناسه پرامپت:** `PROMPT-02-CORRECTION-LINEAGE-AND-CLONING`  
**هدف ابزار:** ورودی مستقیم برای دستور `/speckit-specify`  
**حوزه:** درخواست اصلاح و زنجیره نسخه‌بندی گزارش روزانه (Daily Report Correction & Lineage)  
**سند مرجع:** [`reports_gaps/03/GAP-SPEC-03-DAILY-LIFECYCLE-LOCK.md`](file:///home/hossein/Desktop/projects/building-management/reports_gaps/03/GAP-SPEC-03-DAILY-LIFECYCLE-LOCK.md)  
**داستان کاربری هدف:** `US-DR-13: فرآیند درخواست اصلاح گزارش قفل‌شده و نسخه‌بندی`  

---

### متن پرامپت جهت کپی در `/speckit-specify`:

```text
پیاده‌سازی نیازمندی‌های مصوب درخواست اصلاح گزارش قفل‌شده، رفع باگ کلونینگ ردیف‌ها، جریان انصراف و غنی‌سازی تاریخچه نسخه‌ها مطابق سناریوهای US-DR-13 سند SPEC-03 و گزارش GAP-SPEC-03:

۱. رفع نقص بحرانی در کپی ردیف‌های فرزند هنگام کلون گزارش (Data Loss on Clone):
- در فایل apps/api/core/field_reports/services/correction_service.py در نگاشت CHILD_CLONE_SPECS، فیلدهای جدید مدل DailyReportActivity به فهرست فیلدهای کپی افزوده شوند:
  - contractor_ref_id (شناسه پیمانکار طرف قرارداد)
  - crew_name (نام اکیپ کاری)
  - foreman_count (تعداد سرکارگران)
  - worker_count (تعداد کارگران)
  - parcel (محدوده/پلاک کارگاه)
- ردیف‌های مدل‌های زیر که در حال حاضر در فرآیند کلون جا افتاده‌اند، به CHILD_CLONE_SPECS اضافه شوند تا در گزارش جدید عینا کپی شوند:
  - DailyReportMachineryRow (جدول خلاصه ماشین‌آلات)
  - DailyReportGeneralActivity (فعالیت‌های عمومی کارگاه)
  - DailyReportVisit (بازدیدهای انجام‌شده)
  - فیلدهای severity و source_discipline در ردیف‌های DailyReportIncident.
- تست واحد جدیدی برای اطمینان از برابری دقیق مقادیر فیلدهای ۵ گانه فعالیت‌ها و ردیف‌های ماشین‌آلات قبل و بعد از کلون نوشته شود.

۲. اصلاح کد وضعیت HTTP در تصحیح همزمان:
- در متد open_correction در correction_service.py، در صورتی که درخواست اصلاح باز دیگری برای این گزارش وجود داشته باشد (open_exists)، به جای استفاده از ConflictError که کد ۴۰۹ برمی‌گرداند، یک استثنای ValidationError با کد ۴۰۰ و کد خطای صریح correction_already_open صادر شود:
  ValidationError({'detail': 'درخواست اصلاح باز برای این گزارش وجود دارد', 'code': 'correction_already_open'})

۳. تکمیل فرآیند لغو درخواست اصلاح در فرانت‌اند (Cancel Correction Request):
- در فایل apps/web/src/app/lib/api/daily-reports.ts:
  تابع cancelCorrectionRequest(projectId: string, correctionId: string) برای فراخوانی POST /api/v1/projects/{project_pk}/correction-requests/{correction_id}/cancel/ اضافه شود.
- در کامپوننت ApprovalStatusBar.tsx:
  هرگاه گزارش جاری یک پیش‌نویس ناشی از تصحیح باشد (status === 'draft' و version_number > 1):
  1) یک دکمه با عنوان «انصراف از اصلاح» با استایل هشدار ملایم نمایش داده شود.
  2) با کلیک روی آن، یک دیالوگ تأیید باز شود: «آیا از لغو درخواست اصلاح اطمینان دارید؟ تغییرات پیش‌نویس فعلی حذف شده و نسخه تأییدشده قبلی مجدداً جاری خواهد شد.»
  3) پس از تأیید، تابع cancelCorrectionRequest فراخوانی شده، پیام موفقیت نمایش داده شود و کاربر به صفحه مشاهده نسخه قبلی هدایت گردد.

۴. غنی‌سازی سریالایزر و رابط کاربری تاریخچه نسخه‌ها (Versions History):
- در بک‌اند در DailyReportVersionSerializer (apps/api/core/field_reports/serializers.py):
  1) فیلد modifier_name اضافه شود که نام کامل کاربری را که این نسخه را ثبت/اصلاح کرده بازگرداند.
  2) فیلد correction_reason اضافه شود که دلیل ثبت درخواست اصلاح این نسخه را از جدول DailyReportCorrectionRequest استخراج کند (برای نسخه اول خالی یا «ثبت اولیه» باشد).
  3) فیلد approved_at تاریخ و ساعت تأیید نسخه را برگرداند.
- در فرانت‌اند در کامپوننت ApprovalStatusBar.tsx در لیست «تاریخچه نسخه‌ها»:
  به ازای هر ردیف نسخه، اطلاعات زیر نمایش داده شود:
  - شماره نسخه و برچسب وضعیت (جاری، قفل، پیش‌نویس)
  - نام کاربر اصلاح‌کننده / ثبت‌کننده (modifier_name)
  - دلیل اصلاح ثبت‌شده (correction_reason)
  - تاریخ و ساعت تأیید (approved_at) با فرمت تقویم جلالی
  - دکمه هدایت به مشاهده/ویرایش نسخه مربوطه
```
