# گزارش ارزیابی کیفیت و آزمون کاربر نهایی: نیازمندی A.1.03 (فاز A.1)

## ۱. شناسنامه نیازمندی
- **شناسه نیازمندی:** `A.1.03` (مرتبط با بسته `B03` در مشخصات مرجع)
- **عنوان:** رفع اختلاف‌های اثبات‌شده خروجی
- **معیار پذیرش:** ساعت نامعلوم ماشین‌آلات صفر قطعی جلوه نکند و تست دقیق اضافه شود.
- **فاز تحویل:** فاز فعال `A.1` (بر اساس `/delivery-plan`)
- **وضعیت آزمون (QA Status):** `qa_passed`
- **تاریخ ارزیابی:** ۲۲ نوامبر ۲۰۲۶
- **محیط‌های آزمون:**
  - فرانت‌اند: `http://localhost:5173`
  - بک‌اند: `http://localhost:8000`

---

## ۲. بررسی معیارهای پذیرش و آزمون کاربری (UAT)

### ۲.۱. تفکیک ساعت نامعلوم از صفر قطعی در ماشین‌آلات
- **خروجی اکسل (FILE 4):**
  - در متد `_write_machinery` فایل [shiraz_file4_excel.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/shiraz_file4_excel.py#L481-L527)، در صورتی که مقدار ساعات کارکرد (`productive_hours` یا `operating_hours`) ثبت نشده باشد (`None`)، مقدار سلول دقیقاً `None` باقی می‌ماند و سلول خالی نمایش داده می‌شود.
  - در صورتی که ساعت کارکرد به صورت صریح صفر ثبت شده باشد (`0`)، مقدار سلول عدد `0` ذخیره می‌شود. بنابراین ساعت نامعلوم هیچ‌گاه به اشتباه «صفر قطعی» جلوه نمی‌کند.
- **خروجی PDF دو زبانه:**
  - در متد ساخت بخش ماشین‌آلات فایل [pdf.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/pdf.py#L233-L247):
    ```python
    r.productive_hours if r.productive_hours is not None else '—'
    ```
    و
    ```python
    r.operating_hours if r.operating_hours is not None else '—'
    ```
  - در حالت `None`، علامت خط تیره ام‌دش (`—`) درج شده و در حالت عدد `0`، کاراکتر عددی `0` چاپ می‌گردد.

### ۲.۲. تست‌های دقیق افزوده شده (Automated Test Suite)
تست‌های رگرسیونی اختصاصی برای این نیازمندی پیاده‌سازی شده و معتبر می‌باشند:
1. **تست هم‌ارزی خروجی ماشین‌آلات (`test_b03_legacy_equipment_zero_and_unknown_across_exports`):**
   - در فایل [test_pdf_summary_parity.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/tests/test_pdf_summary_parity.py#L279-L304).
   - اعتبارسنجی می‌کند که برای دو دستگاه یکی با ساعت `None` و دیگری با ساعت `0`، در اکسل دقیقاً `{'Unknown machine': None, 'Measured machine': 0}` و در جدول PDF دقیقاً `{'Unknown machine': '—', 'Measured machine': 0}` تولید شود.
2. **تست حفظ ردیف‌های منبع در تعارض یا ساعات بیش از حد مجاز (`test_b03_conflicting_status_and_excess_hours_preserve_source_rows`):**
   - در فایل [test_machinery_derivation.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/tests/test_machinery_derivation.py#L111-L128).
   - در صورت تعارض وضعیت یا ساعات متناقض، مقدار ساعت تجمیعی را `None` قرار می‌دهد و رکوردهای منبع را حفظ می‌کند.
3. **اعتبارسنجی حد ۲۴ ساعت در شبانه‌روز (`hours_exceed_day_limit`):**
   - در فایل [section_validation.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/services/section_validation.py) و تست‌های `test_machinery_contract.py`.

---

## ۳. بررسی رگرسیون نواقص تاریخی بسته B03
تمام ۸ نقص ثبت‌شده پیشین در این نیازمندی بررسی شدند:
- **DEF-B03-01:** ساعات کارکرد شیفت در ردیف ۴ خروجی اکسل به درستی با روز مرجع هماهنگ است.
- **DEF-B03-02:** جدول‌های نیروی انسانی مستقیم و غیرمستقیم در پروفایل شیراز مجاور هم هستند.
- **DEF-B03-03:** تنظیمات چاپ A4، شکست صفحات و تکرار هدرها رعایت شده است.
- **DEF-B03-04:** سمت سازمانی، نام و زمان محلی کنشگران واقعی درج شده و کنشگر جعلی وجود ندارد.
- **DEF-B03-05:** تجهیزات قدیمی با ساعت نامعلوم از صفر قطعی کاملاً متمایز هستند.
- **DEF-B03-06:** اقلام بتن‌ریزی، بچینگ، تراک‌میکسر و نتایج ۲۸ روزه به درستی لینک شده‌اند.
- **DEF-B03-07:** برچسب‌های حوادث HSE به صورت فارسی بومی نمایش داده می‌شوند.
- **DEF-B03-08:** پشتیبانی از پروفایل‌های پروژه‌ای بدون تحمیل تعداد ثابت انجام شده است.

---

## ۴. نتیجه‌گیری ارزیابی
نیازمندی **A.1.03** با موفقیت پیاده‌سازی شده و تمام معیارهای پذیرش آن از منظر کاربر نهایی و کنترل کیفیت (QA) احراز شده است (`qaStatus: qa_passed`). مستندات ساختاریافته در پوشه `output/phase-a1/` ذخیره شد.
