# راهنمای پرامپت‌های مهندسی‌شده برای ابزار `speckit-specify`

**شناسه مبدأ:** [`reports_gaps/03/GAP-SPEC-03-DAILY-LIFECYCLE-LOCK.md`](file:///home/hossein/Desktop/projects/building-management/reports_gaps/03/GAP-SPEC-03-DAILY-LIFECYCLE-LOCK.md)  
**سند مشخصات هدف:** [`reports_documentation/atomic-specs/SPEC-03-DAILY-LIFECYCLE-LOCK.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/atomic-specs/SPEC-03-DAILY-LIFECYCLE-LOCK.md)  
**دایرکتوری خروجی هدف:** `specs/<NNN-feature-name>/`  
**تاریخ تدوین:** ۳ آبان ۱۴۰۵ (2026-10-25)

---

## ۱. منطق معماری و راهنمای انتخاب پرامپت (Architecture Decision)

برای پوشش شکاف‌ها و عدم انطباق‌های شناسایی‌شده در گزارش `GAP-SPEC-03`، دو رویکرد مهندسی پرامپت در این دایرکتوری در دسترس قرار گرفته است:

### رویکرد اول: پرامپت جامع و یکپارچه (توصیه‌شده - Recommended)
📁 **فایل:** [`01-PROMPT-ALL-IN-ONE-LIFECYCLE-LOCK.md`](file:///home/hossein/Desktop/projects/building-management/reports_gaps/03/speckit-specify-prompts/01-PROMPT-ALL-IN-ONE-LIFECYCLE-LOCK.md)
- **مزایای انتخاب این رویکرد:**
  1. چرخه حیات گزارش روزانه، قفل‌گذاری و اصلاح، یک جریان متصل و وابسته به یکدیگر است.
  2. رفع باگ کلونینگ، تکمیل UI لغو اصلاح، غنی‌سازی تاریخچه نسخه‌ها و استانداردسازی خطاهای سابمیت/ریجکت همگی در ماژول‌های مشترک (`daily_report_views.py`, `correction_service.py`, `ApprovalStatusBar.tsx`) قرار دارند.
  3. با اجرای این پرامپت، یک فیچر منسجم (مانند `034-daily-report-lifecycle-lock-parity`) تولید شده و کلیه شکاف‌های SPEC-03 در یک فرآیند یکپارچه و هماهنگ، بدون دوباره‌کاری در چرخه‌های تست، رفع خواهند شد.

### رویکرد دوم: تفکیک ماژولار دو مرحله‌ای (Modular 2-Phase Approach)
در صورتی که سیاست تیم فنی، تفکیک تغییرات اساسی دیتابیس/سرویس تصحیح از استانداردسازی اعتبارسنجی‌ها و UI باشد، پرامپت‌ها به دو ماژول مستقل تقسیم شده‌اند:

1. 📁 **ماژول ۱ (اصلاح باگ کلونینگ، گردش کار انصراف و تاریخچه نسخه‌ها):**  
   [`02-PROMPT-CORRECTION-LINEAGE-AND-CLONING.md`](file:///home/hossein/Desktop/projects/building-management/reports_gaps/03/speckit-specify-prompts/02-PROMPT-CORRECTION-LINEAGE-AND-CLONING.md)  
   - **تمرکز:** رفع باگ بحرانی حذف فیلدهای ۵ گانه فعالیت در کلون تصحیح، اضافه کردن متد و دکمه Cancel Correction در فرانت‌اند، تغییر کد وضعیت خطای تصحیح همزمان از 409 به 400 و غنی‌سازی سریالایزر و نمایش تاریخچه نسخه‌ها.
   - **پوشش داستانی:** سناریوهای داستان کاربری `US-DR-13`.

2. 📁 **ماژول ۲ (استانداردسازی کدهای خطا و تمایز بصری Unset در برابر صفر):**  
   [`03-PROMPT-VALIDATION-CODES-AND-UNSET-SEMANTICS.md`](file:///home/hossein/Desktop/projects/building-management/reports_gaps/03/speckit-specify-prompts/03-PROMPT-VALIDATION-CODES-AND-UNSET-SEMANTICS.md)  
   - **تمرکز:** اصلاح کدهای خطای `report_not_in_submittable_state`، `rejection_reason_required`، `rejection_reason_min_length_10`، اعتبارسنجی کارکرد نامشخص با خطای `quantity_unset_invalid` و پیام مصوب، و طراحی کامپوننت برچسب خاکستری هشداردهنده «ثبت‌نشده» در جداول فرانت‌اند.
   - **پوشش داستانی:** سناریوهای داستان‌های کاربری `US-DR-11` و `US-DR-14`.

---

## ۲. نحوه استفاده با ابزار `/speckit-specify`

متن پرامپت داخل کادر مربوطه در فایل انتخابی را کپی کرده و به شکل زیر به دستور ارسال نمایید:

```text
/speckit-specify <متن پرامپت انتخابی>
```

### گام‌های چرخه توسعه مبتنی بر مشخصات (Spec-Driven Development):
1. دستور `/speckit-specify` ساختار نیازمندی‌ها، سناریوهای آزمون‌پذیر و متادیتای فیچر را در مسیر `specs/` تولید می‌کند.
2. با دستور `/speckit-plan`، طرح معماری، دیاگرام‌های توالی و قراردادهای داده طراحی می‌شوند.
3. با دستور `/speckit-tasks`، فهرست تسک‌های مهندسی به ترتیب وابستگی ایجاد می‌گردد.
4. با دستور `/speckit-implement`، تغییرات در کدبیس اعمال شده و تست‌های یکپارچگی اجرا خواهند شد.
