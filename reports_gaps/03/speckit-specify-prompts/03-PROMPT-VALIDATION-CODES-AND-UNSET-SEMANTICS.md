# پرامپت ماژولار ۲: استانداردسازی کدهای خطای گردش کار و تمایز بصری Unset در برابر صفر

**شناسه پرامپت:** `PROMPT-03-VALIDATION-CODES-AND-UNSET-SEMANTICS`  
**هدف ابزار:** ورودی مستقیم برای دستور `/speckit-specify`  
**حوزه:** گردش کار تأیید، اعتبارسنجی احجام و تمایز کارکرد صفر از ثبت‌نشده (Workflow Validation & Unset Semantics)  
**سند مرجع:** [`reports_gaps/03/GAP-SPEC-03-DAILY-LIFECYCLE-LOCK.md`](file:///home/hossein/Desktop/projects/building-management/reports_gaps/03/GAP-SPEC-03-DAILY-LIFECYCLE-LOCK.md)  
**داستان‌های کاربری هدف:** `US-DR-11 (گردش کار تأیید و رد)` و `US-DR-14 (تمایز صریح میان مقدار صفر و مقدار ثبت‌نشده)`  

---

### متن پرامپت جهت کپی در `/speckit-specify`:

```text
پیاده‌سازی نیازمندی‌های استانداردسازی کدهای خطای گردش کار گزارش روزانه و تمایز بصری کارکرد صفر در برابر وضعیت ثبت‌نشده (Unset) مطابق سناریوهای US-DR-11 و US-DR-14 سند SPEC-03 و گزارش GAP-SPEC-03:

۱. استانداردسازی کدهای خطای گردش کار در DailyReportViewSet (apps/api/core/field_reports/daily_report_views.py):
- در متد _submit:
  در صورتی که گزارش در وضعیت draft یا rejected نباشد، استثنای ValidationError با کد خطای صریح صادر شود:
  ValidationError({'detail': 'فقط گزارش‌های پیش‌نویس یا رد شده قابل ارسال هستند', 'code': 'report_not_in_submittable_state'})
- در متد _reject:
  اعتبارسنجی فیلد reason تفکیک و کدهای خطای مصوب اعمال گردند:
  1) اگر پارامتر reason خالی، فاقد کاراکتر یا ارسال نشده باشد:
     ValidationError({'reason': 'دلیل رد الزامی است', 'code': 'rejection_reason_required'})
  2) اگر طول متن کمتر از ۱۰ کاراکتر باشد:
     ValidationError({'reason': 'دلیل رد باید حداقل ۱۰ کاراکتر باشد', 'code': 'rejection_reason_min_length_10'})

۲. اعتبارسنجی و خطای کارکرد نامشخص در هنگام ارسال (Submit Quantity Validation):
- در متد _validate_report_ready_for_submit در daily_report_views.py:
  در بررسی ردیف‌های فعالیت کارگاه (activities):
  اگر برای ردیفی quantity_measured=True باشد اما مقدار quantity مقداردهی نشده باشد (None)، سیستم باید خطای اعتبارسنجی با کد quantity_unset_invalid صادر کند.
  متن خطای بازگردانده‌شده باید دقیقاً مطابق مشخصات فنی باشد:
  «مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود».
- این خطا نباید با مقادیر صفر صریح (0 یا 0.00) تحریک شود؛ عدد صفر به عنوان کارکرد واقعی معتبر تلقی شده و سابمیت گزارش را متوقف نمی‌کند.

۳. تمایز بصری وضعیت ثبت‌نشده (Unset) در فرانت‌اند:
- یک کامپوننت بازاستفاده‌پذیر بصری (مثلاً UnsetLabel یا UnsetQuantityBadge) برای نمایش مقادیر ثبت‌نشده در جداول طراحی شود:
  - متن: «ثبت‌نشده» (یا Unset در زبان انگلیسی)
  - استایل: پس‌زمینه خاکستری ملایم (muted/secondary)، فونت کوچک (text-xs) و کادر مرزی مشخص با تم هشدار ملایم (border border-muted-foreground/30 یا amber/warning).
- در جدول ردیف‌های فعالیت در کامپوننت‌های فرانت‌اند:
  1) در EditableGrid.tsx و ActivityTab.tsx: در ستون «مقدار» (Quantity)، در حالت فقط‌خواندنی (Read-only)، اگر مقدار کارکرد null باشد یا quantity_measured=false باشد، به جای خالی ماندن سلول یا نمایش عدد 0، برچسب «ثبت‌نشده» با کادر هشدار رندر شود.
  2) در DailyReportSummaryView.tsx (خط ۷۰۴): در ستون مقدار جدول فعالیت‌ها، به جای رندر ساده r.quantity ?? "—"، در صورت null بودن مقدار، برچسب «ثبت‌نشده» همراه با کادر هشدار نمایش یابد.
  3) در صورتی که کاربر عدد 0 را ثبت کرده باشد، مقدار صریح 0 نمایش داده شود تا کاربر تفاوت ماهوی میان عدم ثبت داده و کارکرد صفر را به وضوح ببیند.

۴. به‌روزرسانی فایل‌های زبان و ترجمه (fa.json / en.json):
- افزودن کلیدهای ترجمه خطاهای جدید:
  - report_not_in_submittable_state
  - rejection_reason_required
  - rejection_reason_min_length_10
  - quantity_unset_invalid
  - dailyReports.status.unsetQuantity ("ثبت‌نشده")

۵. آزمون‌های خودکار:
- اضافه کردن تست‌های pytest برای اطمینان از برگشت کدهای خطای فوق در درخواست‌های ارسالی به اندپوینت‌های submit و reject.
- تست پذیرش مقدار صفر (0.00) بدون خطا و مسدود شدن سابمیت در صورت مقدار unset با کد quantity_unset_invalid.
```
