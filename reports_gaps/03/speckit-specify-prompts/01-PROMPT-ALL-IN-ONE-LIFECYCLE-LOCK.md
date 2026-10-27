# پرامپت جامع و یکپارچه (توصیه‌شده): تطبیق کامل چرخه حیات، قفل، بازنگری، اصلاح و تمایز صفر در برابر ثبت‌نشده

**شناسه پرامپت:** `PROMPT-01-ALL-IN-ONE-LIFECYCLE-LOCK`  
**هدف ابزار:** ورودی مستقیم برای دستور `/speckit-specify`  
**حوزه:** گزارشات روزانه کارگاه (Field Daily Reports)  
**سند مرجع:** [`reports_gaps/03/GAP-SPEC-03-DAILY-LIFECYCLE-LOCK.md`](file:///home/hossein/Desktop/projects/building-management/reports_gaps/03/GAP-SPEC-03-DAILY-LIFECYCLE-LOCK.md)  
**سند مشخصات هدف:** [`SPEC-03-DAILY-LIFECYCLE-LOCK.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/atomic-specs/SPEC-03-DAILY-LIFECYCLE-LOCK.md)  
**رویکرد پیاده‌سازی:** تک‌مرحله‌ای جامع (رفع کامل باگ‌های داده، تکمیل فرانت‌اند، استانداردسازی کدهای خطا و UI بصری)

---

### متن پرامپت جهت کپی در `/speckit-specify`:

```text
پیاده‌سازی نیازمندی‌های مصوب چرخه حیات گزارش روزانه، قفل‌گذاری، فرآیند اصلاح و نسخه‌بندی، استانداردسازی خطاهای گردش کار و تمایز بصری Unset در برابر صفر مطابق اسناد SPEC-03-DAILY-LIFECYCLE-LOCK و GAP-SPEC-03:

۱. رفع باگ تخریب داده در کلون گزارش اصلاحی (Child Row Clone Integrity - US-DR-13):
- در سرویس correction_service.py و نگاشت CHILD_CLONE_SPECS، فیلدهای جاافتاده ردیف‌های فعالیت کارگاه (DailyReportActivity) شامل:
  1) crew_name (نام اکیپ)
  2) foreman_count (تعداد سرکارگر)
  3) worker_count (تعداد کارگر)
  4) parcel (پلاک/محدوده اجرایی)
  5) contractor_ref_id (پیمانکار ارجاعی)
  به طور کامل به فهرست فیلدهای کپی اضافه شوند تا هنگام ایجاد نسخه اصلاحی، این اطلاعات مخدوش و خالی نشوند.
- اضافه کردن کپی سایر ردیف‌های گزارش شامل machinery_rows (DailyReportMachineryRow)، general_activities (DailyReportGeneralActivity)، visits (DailyReportVisit) و فیلدهای تکمیلی حوادث (severity، source_discipline) به CHILD_CLONE_SPECS.
- اصلاح کد وضعیت خطای درخواست اصلاح همزمان در open_correction از ConflictError (HTTP 409) به خطای ValidationError با کد وضعیت HTTP 400 و کد خطای صریح correction_already_open مطابق مشخصات فنی.

۲. تکمیل گردش کار لغو درخواست اصلاح در فرانت‌اند (Cancel Correction UI - US-DR-13):
- در فایل apps/web/src/app/lib/api/daily-reports.ts، تابع API کلاینت cancelCorrectionRequest(projectId, correctionId) برای فراخوانی اندپوینت POST /api/v1/projects/{project_pk}/correction-requests/{correction_id}/cancel/ اضافه شود.
- در کامپوننت نوار وضعیت تأیید (ApprovalStatusBar.tsx) و فرم گزارش (DailyReportForm.tsx)، هرگاه گزارش در وضعیت draft و دارای نسخه بزرگتر از ۱ باشد (نسخه در حال اصلاح باز)، دکمه و فرم تأیید «انصراف از اصلاح / لغو درخواست» تعبیه شود. با تایید کاربر، اندپوینت cancel فراخوانی شده، پیش‌نویس موقت حذف و کاربر به نسخه قبلی تأییدشده که مجدداً جاری (is_current=true) شده است هدایت شود.

۳. غنی‌سازی متادیتای نسخه‌ها و شفافیت تاریخچه (Version History Lineage - US-DR-13):
- در بک‌اند در DailyReportVersionSerializer (apps/api/core/field_reports/serializers.py)، فیلدهای زیر به خروجی اندپوینت /versions/ اضافه شوند:
  1) modifier_name: نام و نام خانوادگی کاربر ایجادکننده یا اصلاح‌کننده نسخه.
  2) correction_reason: متن دلیل ثبت درخواست اصلاح که در DailyReportCorrectionRequest ذخیره شده است.
  3) approved_at: تاریخ و زمان رسمی تأیید نسخه.
- در فرانت‌اند در ApprovalStatusBar.tsx در بخش بازشونده «تاریخچه نسخه‌ها»، به ازای هر نسخه در لیست، علاوه بر شماره نسخه و وضعیت قفل، نام اصلاح‌کننده، متن دلیل اصلاح و تاریخ تأیید آن با فرمت تاریخ جلالی خوانا نمایش داده شود.

۴. استانداردسازی کدهای خطای گردش کار تأیید و رد (Workflow Error Codes - US-DR-11):
- در DailyReportViewSet._submit در daily_report_views.py، در صورتی که گزارش در وضعیتی غیر از draft یا rejected باشد، خطای اعتبارسنجی صریح با کد report_not_in_submittable_state صادر شود.
- در DailyReportViewSet._reject، اعتبارسنجی فیلد reason تفکیک و استاندارد شود:
  1) در صورت خالی بودن یا ارسال نشدن دلیل، خطای 400 با کد rejection_reason_required صادر شود.
  2) در صورت ارسال متنی با کمتر از ۱۰ کاراکتر، خطای 400 با کد rejection_reason_min_length_10 صادر شود.
  3) پیام‌های متنی فارسی متناظر در دیکشنری ترجمه و خطاها قرار گیرند.

۵. اعتبارسنجی احجام نامشخص در ارسال گزارش (Submit Unset Validation - US-DR-14):
- در متد _validate_report_ready_for_submit در daily_report_views.py، اعتبارسنجی احجام فعالیت‌ها به صورت ساختاریافته اصلاح شود:
  هرگاه ردیفی دارای quantity_measured=True ولی quantity=None باشد، خطای اعتبارسنجی با کد quantity_unset_invalid و دقیقاً با پیام مصوب سند صادر گردد:
  «مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود».

۶. تمایز بصری Unset در برابر مقدار صفر در فرانت‌اند (Unset vs Zero UI Badge - US-DR-14):
- یک کامپوننت بصری (مثلاً UnsetQuantityBadge) طراحی و پیاده‌سازی شود:
  در صورتی که مقدار کارکرد فعالیتی مقداردهی نشده باشد (quantity == null یا quantity_measured === false)، به جای نمایش عدد 0 یا خط تیره ساده ("—")، یک برچسب خاکستری‌رنگ متمایز با متن «ثبت‌نشده» (Unset) و دارای کادر هشدار ملایم نمایش داده شود.
- این تمایز بصری در گرید EditableGrid / ActivityTab (حالت‌های نمایشی و فقط‌خواندنی) و در جدول ردیف‌های فعالیت صفحه خلاصه گزارش روزانه (DailyReportSummaryView.tsx) اعمال گردد.
- در صورتی که کاربر صراحتاً عدد 0.00 را وارد کرده باشد، مقدار عددی 0 نمایش داده شود تا تفاوت کارکرد صفر با وضعیت ثبت‌نشده کاملاً برای ناظر و مدیر پروژه مشهود باشد.

۷. تست‌پذیری و آزمون‌های رفتاری:
- به‌روزرسانی یا ایجاد تست‌های pytest در بک‌اند برای اطمینان از کلون کامل فیلدهای ۵ گانه فعالیت در تصحیح، بازگرداندن خطای 400 برای تصحیح باز، کدهای خطای رسمی سابمیت و ریجکت، و صحت اعتبارسنجی quantity_unset_invalid.
- تست E2E یا کامپوننت برای اطمینان از عملکرد دکمه لغو اصلاح و نمایش برچسب بصری ثبت‌نشده در جدول.
```
