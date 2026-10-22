# راهنمای پرامپت‌های مهندسی‌شده برای ابزار `speckit-specify`
**شناسه مبدأ:** [`reports_gaps/01/GAP-SPEC-01-DAILY-HEADER-WEATHER.md`](file:///home/hossein/Desktop/projects/building-management/reports_gaps/01/GAP-SPEC-01-DAILY-HEADER-WEATHER.md)  
**دایرکتوری خروجی هدف:** `specs/<NNN-feature-name>/`  
**تاریخ تدوین:** ۲ آبان ۱۴۰۵ (2026-10-22)

---

## ۱. منطق معماری و تصمیم‌گیری در مورد تعداد پرامپت‌ها (Architecture Decision)

یکی از اصول بنیادین مهندسی پرامپت در سیستم‌های مبتنی بر Spec-Kit، **تعیین سطح اتمیسیته و مرزبندی فیچر (Feature Scoping)** است. در این خصوص دو رویکرد طراحی و پیاده‌سازی شده است:

### رویکرد اول: پرامپت جامع و یکپارچه (توصیه‌شده - Recommended)
📁 **فایل:** [`01-PROMPT-ALL-IN-ONE-DAILY-HEADER.md`](file:///home/hossein/Desktop/projects/building-management/reports_gaps/01/speckit-specify-prompts/01-PROMPT-ALL-IN-ONE-DAILY-HEADER.md)
- **چرا این رویکرد ترجیح دارد؟**
  1. تمامی فیلدهای مطرح در GAP-01 (`weather_condition`, `temp_max`, `temp_min`, `weather_impact_notes`, `site_status`, `inactivity_reason`) متعلق به **یک ردیف در جدول دیتابیس (`DailyReport`)** و **یک کامپوننت فرانت‌اند (`ReportHeader.tsx`)** هستند.
  2. تقسیم این اقلام به چند فیچر مستقل، منجر به تولید چند مایگریشن مجزا روی یک جدول، چرخه‌های متعدد ریویو و تعارض احتمالی کد (Merge Conflicts) می‌گردد.
  3. با اجرای این پرامپت، یک فیچر واحد (مثلاً `030-daily-report-header-weather-inactivity`) در سیستم ایجاد شده و تمام تغییرات در یک گام تمیز و هماهنگ پیاده‌سازی و تست می‌شوند.

### رویکرد دوم: تفکیک ماژولار دو مرحله‌ای (Modular 2-Phase Approach)
در صورتی که سیاست تیم توسعه، ایجاد PRهای فوق‌کوچک با ریسک رگرسیون تفکیک‌شده باشد، پرامپت‌ها به دو فاز مجزا خرد شده‌اند:
1. 📁 **فاز ۱ (داده‌های اقلیمی و جوی):** [`02-PROMPT-MODULAR-WEATHER-TEMPERATURE.md`](file:///home/hossein/Desktop/projects/building-management/reports_gaps/01/speckit-specify-prompts/02-PROMPT-MODULAR-WEATHER-TEMPERATURE.md)  
   تمرکز بر استانداردسازی ۵ وضعیت جوی، بازه و اعتبارسنجی دما، فیلد یادداشت‌های شرایط جوی و خروجی PDF.
2. 📁 **فاز ۲ (وضعیت عملیاتی، تعطیلی و امنیت):** [`03-PROMPT-MODULAR-INACTIVITY-SECURITY.md`](file:///home/hossein/Desktop/projects/building-management/reports_gaps/01/speckit-specify-prompts/03-PROMPT-MODULAR-INACTIVITY-SECURITY.md)  
   تمرکز بر فیلد علت تعطیلی کارگاه، اعتبارسنجی الزامی بودن، هشدار تداخل کارکرد اجرایی در روز غیرفعال، و ارتقای امنیت اکشن `by-date`.

---

## ۲. نحوه استفاده با ابزار `/speckit-specify`

کافی است متن داخل باکس کد در فایل پرامپت انتخابی را کپی کرده و در چت جاری به شکل زیر ارسال فرمایید:

```text
/speckit-specify <متن پرامپت کپی‌شده>
```

### گام‌های بعدی چرخه Spec-Kit پس از تولید مشخصات:
1. `/speckit-specify` سند رسمی `spec.md` و چک‌لیست کیفی نیازمندی‌ها را در دایرکتوری `specs/` تولید می‌کند.
2. با دستور `/speckit-plan`، طرح معماری، قراردادهای API و تغییرات شِمای دیتابیس طراحی می‌شوند.
3. با دستور `/speckit-tasks`، فهرست وظایف فنی و وابسته استخراج می‌گردد.
4. با دستور `/speckit-implement`، کدها پیاده‌سازی و تست‌های Pytest پاس خواهند شد.
