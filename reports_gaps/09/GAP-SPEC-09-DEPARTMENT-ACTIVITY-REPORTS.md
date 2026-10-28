# سند نهایی ارزیابی شکاف‌ها و تحلیل انطباق: رکوردهای فعالیت و گزارشات دپارتمان‌های ۵ گانه

**شناسه سند:** `GAP-SPEC-09-DEPARTMENT-ACTIVITY-REPORTS`  
**سند مشخصات فنی هدف:** [`SPEC-09-DEPARTMENT-ACTIVITY-REPORTS.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/atomic-specs/SPEC-09-DEPARTMENT-ACTIVITY-REPORTS.md)  
**اسناد مرجع همبسته:**  
- [`reports_documentation/05-.../department-activity-records.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/05-department-and-warehouse-reports/department-activity-records.md)  
- [`reports_documentation/07-.../department-activities-user-flow.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/07-decision-tree-and-user-flows/department-activities-user-flow.md)  
- [`reports_documentation/03-.../sub_reports_ENDPOINTS.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/03-daily-field-reports-and-apis/sub_reports_ENDPOINTS.md)  
- [`docs/decision-tree/.../[open-electrical-department]/README.md`](file:///home/hossein/Desktop/projects/building-management/docs/decision-tree/login/submit-valid-credentials/[open-legacy-project]/[open-electrical-department]/README.md)  
**تاریخ ارزیابی:** ۶ آبان ۱۴۰۵ (2026-10-28)  
**دامنه ارزیابی:**  
- **بک‌اند:**  
  - مدل‌ها و انام‌ها: [`apps/api/core/inventory/models.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/models.py)، [`apps/api/core/sub_reports/models.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/models.py)  
  - سریالایزرها و ولیدیشن‌ها: [`apps/api/core/inventory/serializers.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/serializers.py)  
  - کنترلرها و اندپوینت‌های ورود/خروج و گزارش: [`apps/api/core/inventory/department_activity_data_views.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_data_views.py)، [`apps/api/core/inventory/views.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/views.py)، [`apps/api/core/inventory/project_urls.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/project_urls.py)  
  - موتور تولید اکسل و PDF و ایمپورت: [`apps/api/core/inventory/department_activity_io.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_io.py)، [`apps/api/core/inventory/department_activity_services.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_services.py)  
  - تست‌های خودکار: [`apps/api/core/inventory/tests.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/tests.py)  
- **فرانت‌اند:**  
  - صفحه دپارتمان‌ها: [`apps/web/src/components/department/department-page.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/department/department-page.tsx)  
  - مودال ثبت رکورد فعالیت: [`apps/web/src/components/department/department-activity-record-modal.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/department/department-activity-record-modal.tsx)  
  - روت‌های ۵ دپارتمان: [`apps/web/src/app/routes/business-buildings.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/business-buildings.tsx)، [`business-electrical.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/business-electrical.tsx)، [`business-mechanical.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/business-mechanical.tsx)، [`business-machinery.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/business-machinery.tsx)، [`business-warehouse.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/business-warehouse.tsx)  
**وضعیت کلی سند:** ⚠️ **دارای شکاف‌های انطباق بحرانی و مغایرت بنیادی در قالب گزارشات (Fail - Action Required)**

---

## ۱. خلاصه‌ی اجرایی و تحلیل انطباق (Executive Summary)

سند مشخصات فنی اتمیک **`SPEC-09-DEPARTMENT-ACTIVITY-REPORTS`** الزامات فنی و کاربری ثبت رکوردهای روزانه، صدور گزارشات کاری روزانه و هفتگی در قالب فایل‌های چندشیتی اکسل (.xlsx) مجهز به فرمول‌های بومی محاسباتی، خروجی اکسل فیلترشده با استانداردهای زبان فارسی، و ورود دسته‌ای داده‌ها از طریق فایل شیت با تضمین یکپارچگی تراکنش (Atomic Rollback) و اعتبارسنجی سطر-محور را برای دپارتمان‌های ۵ گانه کارگاه تدوین می‌نماید:
1. **ابنیه و ساختمانی (`civil`)**
2. **تأسیسات الکتریکی (`electrical`)**
3. **تأسیسات مکانیکی (`mechanical`)**
4. **ماشین‌آلات و تجهیزات (`machinery`)**
5. **انبار و گردش مصالح (`warehouse`)**

بررسی و تحلیل عمیق کدهای موجود در بک‌اند (`apps/api/core/inventory/`) و فرانت‌اند (`apps/web/src/components/department/`) نشان می‌دهد که سیستم فعلی با یک **انحراف بنیادی از مشخصات فنی** مواجه است:

1. **انحراف کامل فرمت گزارشات روزانه و هفتگی (تولید PDF به جای اکسل):**  
   در حالی که SPEC-09 صراحتاً دریافت ورک‌بوک اکسل (`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`) را در اندپوینت‌های `.../reports/daily/` و `.../reports/weekly/` الزامی کرده است، کدهای جاری بک‌اند به کلی فایل PDF توسط کتابخانه ReportLab تولید می‌کنند (`Content-Type: application/pdf`) و در فرانت‌اند نیز فایل با پسوند `.pdf` دانلود می‌شود!
2. **فقدان فیلد حیاتی «مقدار اجرا» (`executed_quantity`) برای دپارتمان‌های غیرانباری:**  
   در مدل دیتابیس [`DepartmentActivityRecord`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/models.py#L79)، تنها برای انبار فیلدهای مقداری (`quantity_in` و `quantity_out`) وجود دارد؛ برای دپارتمان‌های ابنیه، برق، مکانیک و ماشین‌آلات، فیلد `unit` (واحد اندازه‌گیری) تعریف شده اما هیچ فیلدی برای مقدار عددی اجراشده وجود ندارد! در نتیجه در فرانت‌اند نیز فیلدی برای درج مقدار کار انجام‌شده وجود ندارد و امکان محاسبه جمع احجام در گزارش روزانه یا فرمول جمع هفتگی در اکسل منتفی است.
3. **فقدان کامل شیت‌های مجزای روزانه، شیت خلاصه (Summary) و فرمول‌های بومی اکسل (`=SUM(...)`):**  
   هیچ ماژولی برای ساخت ورک‌بوک چندشیتی هفتگی وجود ندارد؛ شیت‌های مجزا برای شنبه تا جمعه کارگاه و شیت جمع‌بندی تولید نمی‌شوند و فرمول‌نویسی بومی باز اکسل کاملاً غایب است.
4. **عدم پشتیبانی از فیلترهای تاریخی (`date` و `week_start`) در اندپوینت‌های گزارشات:**  
   اندپوینت گزارش روزانه پارامتر `date={YYYY-MM-DD}` را نادیده گرفته و صرفاً روز گذشته تقویمی (`yesterday`) را برمی‌گرداند؛ اندپوینت گزارش هفتگی نیز پارامتر `week_start` را قبول نکرده و یک بازه شناور ۷ روز اخیر (`rolling 7 days`) را محاسبه می‌کند.
5. **نقض اصل اتمیک بودن در ورود دسته‌ای اکسل (فقدان Rollback در صورت خطا در سطرها):**  
   متد `import_activities_from_xlsx` رکوردها را سطر به سطر ذخیره می‌کند. اگر در سطر ۴ خطایی رخ دهد، سطرهای ۲ و ۳ در دیتابیس باقی می‌مانند! هیچ تراکنش اتمیکی وجود ندارد و کل تراکنش متوقف نمی‌شود؛ فرانت‌اند نیز پیام وارد شدن بخشی از داده‌ها (`importPartial`) را نمایش می‌دهد که نقض صریح سناریوهای ۲ و ۳ از US-DP-03 است.
6. **مغایرت کدینگ اسلاگ دپارتمان ابنیه (`civil` در برابر `buildings`):**  
   سند SPEC-09 اسلاگ دپارتمان ابنیه را `civil` می‌داند، اما در انام بک‌اند تنها `buildings` مجاز است و در صورت ارسال `department=civil`، سرور با خطای HTTP 400 درخواست را رد می‌کند.
7. **آسیب‌پذیری امنیتی دسترسی به ورود داده‌ها (Import):**  
   اندپوینت آپلود اکسل و درج رکوردهای گروهی، به دلیل ارث‌بری نادرست از کلاس پایه، صرفاً با داشتن مجوز خواندن (`view_reports`) قابل فراخوانی است و نیازی به مجوز ویرایش (`edit_reports`) ندارد.

---

### جدول ماتریس ارزیابی انطباق سناریوها

| شناسه داستان / سناریو | شرح در سند مشخصات (SPEC-09) | وضعیت انطباق | علت و خلاصه شواهد در کد جاری |
| :--- | :--- | :---: | :--- |
| **US-DP-01 (سناریو ۱)** | ثبت موفق رکورد فعالیت با شناسه دپارتمان شامل شرح فعالیت، پیمانکار، جبهه کاری، مقدار اجرا و واحد در `POST .../department-activity-records/` | ❌ شکاف بحرانی (P1) | مدل `DepartmentActivityRecord` و فرم مودال فرانت‌اند فاقد فیلد «مقدار اجرا» (`executed_quantity`) برای دپارتمان‌های غیرانباری هستند. اسلاگ `civil` در بک‌اند نامعتبر است. |
| **US-DP-01 (سناریو ۲)** | دانلود فایل اکسل (.xlsx) گزارش روزانه واحد بر اساس تاریخ انتخابی با هدر رسمی، جدول ردیف‌ها و جمع احجام با وضعیت 200 OK | ❌ شکاف بحرانی (P1) | اندپوینت بک‌اند به جای فایل اکسل، فایل PDF تولید می‌کند (`Content-Type: application/pdf`). پارامتر `date` نادیده گرفته می‌شود و جمع احجام به دلیل نبود فیلد مقدار وجود ندارد. |
| **US-DP-02 (سناریو ۱)** | تولید گزارش هفتگی اکسل دپارتمان بر اساس `week_start` شامل شیت‌های مجزا برای هر روز هفته و یک شیت جمع‌بندی (Summary Sheet) | ❌ شکاف بحرانی (P1) | بک‌اند فایل PDF تولید می‌کند؛ ماژول تولید ورک‌بوک اکسل چندزبانه با شیت‌های روزانه و شیت خلاصه وجود ندارد؛ پارامتر `week_start` پذیرفته نمی‌شود. |
| **US-DP-02 (سناریو ۲)** | درج فرمول‌های بومی جمع اکسل (`=SUM(...)`) در ستون مجموع مقادیر هفتگی به منظور به‌روزرسانی خودکار با تغییر سلول‌ها | ❌ شکاف بحرانی (P1) | هیچ‌گونه فرمول‌نویسی اکسل در سامانه پیاده‌سازی نشده است؛ مقدار عددی برای فعالیت‌ها وجود ندارد که جمع زده شود. |
| **US-DP-03 (سناریو ۱)** | صدور خروجی اکسل فیلترشده از رکوردهای جدول با فرمت اکسل و فونت استاندارد فارسی بر اساس پیمانکار و بازه انتخابی | ⚠️ انطباق ناقص (P2) | خروجی فیلترشده وجود دارد اما بدون فونت فارسی، بدون راست‌چین (RTL)، با هدرهای انگلیسی خام و بدون مقدار اجرا صادر می‌شود. |
| **US-DP-03 (سناریو ۲)** | ورود اطلاعات دسته‌ای از تمپلیت اکسل با اعتبارسنجی ستون‌ها، کدهای پیمانکار و مقادیر عددی با تراکنش کامل و درج یکجا | ❌ شکاف بحرانی (P1) | متد ایمپورت فاقد `@transaction.atomic` است؛ رکوردها سطر به سطر درج می‌شوند؛ مقادیر عددی فعالیت‌های غیرانباری اعتبارسنجی نمی‌شوند. |
| **US-DP-03 (سناریو ۳)** | اعلام گزارش خطای سطر نامعتبر (مانند «خطا در سطر ۴: مقدار اجرا باید عددی باشد») و توقف کل تراکنش (Rollback) | ❌ شکاف بحرانی (P1) | در صورت بروز خطا در یک سطر، سطرهای قبلی در دیتابیس کامیت باقی می‌مانند (عدم Rollback)؛ پیام‌های خطا به صورت انگلیسی خام دیکشنری است. |

---

## ۲. یافته‌های تفصیلی و شواهد کد (Detailed Findings & Code Evidence)

### G01 — P1 — فقدان فیلد «مقدار اجرا» (`executed_quantity`) در مدل دیتابیس، سریالایزر و فرم فرانت‌اند برای دپارتمان‌های غیرانباری

**شرح نیازمندی در SPEC-09 (داستان US-DP-01، سناریو ۱):**  
> «هنگامی که فرم شامل شرح فعالیت، پیمانکار، جبهه کاری، مقدار اجرا و واحد را ذخیره کند،  
> آنگاه ردیف در اندپوینت `POST .../department-activity-records/` با فیلد `department="electrical"` ذخیره شود.»

**وضعیت در کد جاری:**  
در فایل [`apps/api/core/inventory/models.py:79-113`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/models.py#L79-L113):
```python
class DepartmentActivityRecord(TimeStampedModel):
    project = models.ForeignKey(...)
    department = models.CharField(max_length=32, choices=Department.choices, db_index=True)
    date = models.DateField()
    location = models.CharField(max_length=255, blank=True, default='')
    activity_description = models.CharField(max_length=500, blank=True, default='')
    contractor = models.CharField(max_length=255, blank=True, default='')
    contractor_ref = models.ForeignKey(...)
    unit = models.CharField(max_length=64, blank=True, default='')
    description = models.TextField(blank=True, default='')
    material_type = models.CharField(max_length=255, blank=True, default='')
    quantity_in = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    quantity_out = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    consumption_location = models.CharField(max_length=255, blank=True, default='')
    supplier = models.CharField(max_length=255, blank=True, default='')
```
در مدل بالا، برای دپارتمان‌های غیرانباری فیلد `unit` (مانند مترمکعب، کیلوگرم، شاخه) تعریف شده است، اما **هیچ فیلدی برای مقدار کار انجام‌شده (مانند `executed_quantity` یا `quantity`) وجود ندارد!**  
همچنین در فایل فرانت‌اند [`apps/web/src/components/department/department-activity-record-modal.tsx:134-148`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/department/department-activity-record-modal.tsx#L134-L148)، برای دپارتمان‌های غیرانباری هیچ فیلدی برای دریافت مقدار اجرا از کاربر طراحی نشده و مقادیر عددی به صفر اجبار می‌شوند:
```typescript
    return {
      department,
      date: form.date,
      location: form.location,
      activity_description: form.activity_description,
      contractor: "",
      contractor_ref: form.contractor_ref || null,
      unit: showsUnit ? form.unit : "",
      description: form.description,
      material_type: "",
      quantity_in: "0",
      quantity_out: "0",
      ...
    };
```
و در [`apps/api/core/inventory/serializers.py:277-280`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/serializers.py#L277-L280):
```python
        attrs['quantity_in'] = Decimal('0')
        attrs['quantity_out'] = Decimal('0')
```
**پیامدهای شکاف:**  
1. کارشناسان کارگاه نمی‌توانند حجم کار انجام‌شده (مثلاً ۲۰ متر بتن‌ریزی یا ۵۰ متر کابل‌کشی) را ثبت کنند.
2. سناریوی ۲ از US-DP-01 که محاسبه «جمع احجام» روزانه را الزامی دانسته، قابل تحقق نیست.
3. تجمیع هفتگی و درج فرمول‌های `=SUM(...)` در سناریوهای US-DP-02 کاملاً ناممکن شده است.

---

### G02 — P1 — انحراف کامل فرمت گزارش روزانه دپارتمان (تولید PDF به جای اکسل) و عدم پشتیبانی از فیلتر `date`

**شرح نیازمندی در SPEC-09 (داستان US-DP-01، سناریو ۲):**  
> «با فرض اینکه برای تاریخ `1405-07-25` رکوردهایی در دپارتمان ابنیه ثبت شده باشد،  
> هنگامی که کاربر دکمه «دانلود گزارش روزانه» را بزند،  
> آنگاه اندپوینت `GET .../reports/daily/?department=civil&date=2026-10-17` یک فایل ورک‌بوک اکسل با هدر رسمی پروژه، نام دپارتمان ابنیه، جدول ردیف‌های آن روز و جمع احجام با کد وضعیت `200 OK` بازگرداند.»

**وضعیت در کد جاری:**  
در فایل [`apps/api/core/inventory/department_activity_data_views.py:175-187`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_data_views.py#L175-L187):
```python
        pdf_bytes = generate_activity_report_pdf(...)
        filename = f'{department}_{self.period}_report_{date_from}_{date_to}.pdf'
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response["Content-Disposition"] = f"attachment; filename=\"{filename}\""
        return response
```
و در متد تعیین بازه تاریخی در [`apps/api/core/inventory/department_activity_services.py:121-128`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_services.py#L121-L128):
```python
def get_report_date_range(period: str) -> tuple[date, date]:
    today = timezone.localdate()
    if period == 'daily':
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday
```
و در فرانت‌اند [`apps/web/src/components/department/department-page.tsx:249-265`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/department/department-page.tsx#L249-L265):
```typescript
  const handleDownloadReport = async (period: "daily" | "weekly") => {
    ...
    const blob = await apiBlob(
      `/${PATHS.API_PROJECTS}/${businessId}/${DEPARTMENT_ACTIVITY_RECORDS_PATH}/reports/${period}/?department=${department}`,
    );
    downloadBlob(blob, `${department}_${period}_report.pdf`);
```
**پیامدهای شکاف:**  
1. خروجی درخواستی اکسل (.xlsx) با نوع رسانه‌ای `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` است، اما سرور PDF باینری بازمی‌گرداند.
2. هیچ پارامتر تاریخی (`date`) خوانده نمی‌شود و سیستم همیشه داده‌های روز قبل (`yesterday`) را به شکل هاردکد استخراج می‌کند! کاربر نمی‌تواند گزارش روزهای قبل‌تر (مثلاً `2026-10-17`) را دریافت کند.
3. در فرانت‌اند هیچ انتخاب‌گر تاریخی (DatePicker) برای دانلود گزارش روزانه وجود ندارد و با یک کلیک بلافاصله روز گذشته دانلود می‌شود.
4. جدول ردیف‌ها فاقد ستون احجام و فاقد سطر تجمیعی «جمع احجام» است.

---

### G03 — P1 — انحراف فرمت گزارش هفتگی دپارتمان (PDF به جای اکسل)، فقدان شیت‌های روزانه و شیت جمع‌بندی، و نبود فرمول‌های `=SUM(...)`

**شرح نیازمندی در SPEC-09 (داستان US-DP-02، سناریوهای ۱ و ۲):**  
> «سناریو ۱: اندپوینت `GET .../reports/weekly/?department=mechanical&week_start=2026-10-18` فایل اکسلی شامل شیت‌های مجزا برای هر روز هفته و یک شیت جمع‌بندی (Summary Sheet) تولید و دانلود نماید.  
> سناریو ۲: در ستون مجموع مقادیر هفتگی، فرمول‌های جمع استاندارد اکسل (`=SUM(...)`) درج شده باشند تا در صورت ویرایش محلی، جمع‌ها اتوماتیک به‌روز شوند.»

**وضعیت در کد جاری:**  
1. اندپوینت هفتگی [`DepartmentActivityWeeklyReportView`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_data_views.py#L207) از همان کلاس والد `_DepartmentActivityReportView` ارث‌بری کرده و خروجی تک‌صفحه‌ای PDF صادر می‌کند.
2. هیچ کدی برای ایجاد ورک‌بوک چندشیتی (Multi-Sheet Workbook) شامل زبانه‌های شنبه تا جمعه (Saturday to Friday) و زبانه خلاصه (`Summary`) در سامانه وجود ندارد.
3. هیچ فرمول اکسلی (`openpyxl.worksheet.worksheet.Worksheet.cell(value="=SUM(...)")`) در هیچ نقطه‌ای از کد نوشته نشده است.
4. متد `get_report_date_range` در [`department_activity_services.py:129-130`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_services.py#L129-L130) یک بازه متحرک ۷ روزه بر مبنای روز جاری می‌گیرد (`start = today - timedelta(days=6)`) و پارامتر `week_start` را کلاً نادیده می‌گیرد.
5. در فرانت‌اند [`department-page.tsx:737-747`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/department/department-page.tsx#L737-L747) دکمه دانلود گزارش هفتگی هیچ دیالوگی برای انتخاب هفته کاری باز نمی‌کند و مستقیماً درخواست دانلود فایل PDF ارسال می‌شود.

---

### G04 — P1 — عدم رعایت اصل تراکنش اتمیک (Atomic Transaction Rollback) در ورود دسته‌ای اکسل (Import)

**شرح نیازمندی در SPEC-09 (داستان US-DP-03، سناریوهای ۲ و ۳):**  
> «سناریو ۲: سرور صحت ستون‌ها، معتبر بودن کدهای پیمانکار و مقادیر عددی را سنجیده و در صورت عدم وجود خطا، تمامی ردیف‌ها را در پایگاه داده درج کرده و تعداد رکوردهای موفق را گزارش دهد.  
> سناریو ۳: خطا در سطر ۴... و کل تراکنش را متوقف (Rollback) کند تا داده ناقص درج نشود.»

**وضعیت در کد جاری:**  
در فایل [`apps/api/core/inventory/department_activity_io.py:254-411`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_io.py#L254-L411)، تابع `import_activities_from_xlsx`:
1. بدون دکوراتور یا بلاک `@transaction.atomic` اجرا می‌شود.
2. حلقه پردازش سطرها به ازای هر ردیف معتبر، بلافاصله `DepartmentActivityRecord.objects.create(...)` را اجرا کرده و مقدار `created += 1` می‌کند (سطرهای ۳۲۱-۳۳۶ و ۳۹۰-۴۰۶).
3. اگر در سطر ۴ یا ۱۰ خطایی رخ دهد (پیمانکار نامعتبر، فیلد خالی، خطای ولیدیشن)، ردیف خطا در آرایه `errors` اضافه می‌شود و حلقه ادامه می‌یابد (`continue`):
   ```python
   if row_errors:
       errors.append({'row': row_index, 'errors': row_errors})
       continue
   ```
4. در پایان، متد مقدار `return created, errors` را بازمی‌گرداند.
5. در فرانت‌اند [`apps/web/src/components/department/department-page.tsx:218-224`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/department/department-page.tsx#L218-L224):
   ```typescript
   if (result.errors.length > 0) {
     setActionMessage(
       t("businessDepartment.activityLog.importPartial", {
         created: result.created,
         errorCount: result.errors.length,
       }),
     );
   }
   ```
**پیامدهای شکاف:**  
سیستم رفتار مغایر "Partial Import" را پیاده‌سازی کرده است. کاربر نیمی از داده‌ها را ثبت‌شده می‌بیند و نیمی دیگر را با خطا مواجه؛ اگر فایل اصلاح و مجدداً آپلود شود، سطرهای قبلی دوباره تکرار (Duplicate) خواهند شد! طبق SPEC-09، سیاست قطعی سیستم **«همه یا هیچ» (All-or-Nothing Atomic Rollback)** است.

---

### G05 — P1 — فقدان اعتبارسنجی مقادیر عددی برای دپارتمان‌های غیرانباری و نبود پیام‌های خطای سطر-محور شفاف به زبان فارسی

**شرح نیازمندی در SPEC-09 (داستان US-DP-03، سناریو ۳):**  
> «با فرض اینکه در سطر ۴ فایل اکسل، مقدار عددی به جای عدد، متن وارد شده باشد،  
> هنگامی که فایل بررسی می‌شود،  
> آنگاه سیستم پیام مشخص بازگرداند: «خطا در سطر ۴: مقدار اجرا باید عددی باشد»»

**وضعیت در کد جاری:**  
1. در تابع `import_activities_from_xlsx` در خطوط ۳۴۱-۳۵۰ از [`department_activity_io.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_io.py#L341-L350):
   ```python
   required_value_fields = ('location', 'activity_description', 'contractor')
   if uses_unit:
       required_value_fields = (*required_value_fields, 'unit')
   ```
   فیلد «مقدار اجرا» اصلاً خوانده و ارزیابی نمی‌شود! اگر در اکسل ستون مقدار اجرا وجود داشته باشد یا متنی در آن درج شده باشد، سیستم آن را نادیده گرفته و به عنوان سطر صحیح ثبت می‌کند!
2. پیام‌های تولیدی در دیکشنری خطاها، انگلیسی هستند (`'Enter a valid number.'`، `'This field is required.'`) و فرمت اعلام پیام فارسی جامع طبق سناریو ۳ پیاده‌سازی نشده است.

---

### G06 — P2 — ناسازگاری اسلاگ دپارتمان ابنیه (`civil` در برابر `buildings`) و عدم پذیرش `civil` در اندپوینت‌ها

**شرح نیازمندی در SPEC-09 (بخش ۱، ۲، ۳):**  
> «دپارتمان‌های ۵ گانه: ۱. ابنیه و ساختمانی (`civil`)...  
> اندپوینت `GET .../reports/daily/?department=civil&date=2026-10-17`...»

**وضعیت در کد جاری:**  
در فایل [`apps/api/core/inventory/models.py:60-67`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/models.py#L60-L67):
```python
class Department(models.TextChoices):
    BUILDINGS = 'buildings', 'ابنیه'
    MECHANICAL = 'mechanical', 'مکانیک'
    SECURITY = 'security', 'حراست'
    MACHINERY = 'machinery', 'ماشین آلات'
    WAREHOUSE = 'warehouse', 'انباردار'
    ELECTRICAL = 'electrical', 'برق'
```
و در تابع اعتبارسنجی در [`apps/api/core/inventory/department_activity_services.py:114-118`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_services.py#L114-L118):
```python
def require_valid_department(department: str | None) -> str | None:
    if not department:
        return None
    valid = {choice[0] for choice in Department.choices}
    return department if department in valid else None
```
اگر کلاینت مقدار `department=civil` (مطابق قرارداد SPEC-09) را ارسال کند، این متد مقدار `None` برمی‌گرداند و اندپوینت با خطای `HTTP 400 Bad Request` متوقف می‌شود:
`Query parameter department is required and must be a valid department slug.`  
جالب اینکه در مدل‌های [`sub_reports/models.py:11-17`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/models.py#L11-L17) مقدار `Discipline.CIVIL = 'civil'` است. این ناهماهنگی نام‌گذاری باید از طریق تعریف آلیاس دوطرفه (`civil` ⇄ `buildings`) در لایه سرویس و مدل برطرف شود.

---

### G07 — P2 — نقص امنیتی در کنترل دسترسی اندپوینت ورود دسته‌ای اطلاعات (Import View)

**شرح نیازمندی در قرارداد و اصول دسترسی (SPEC-09 و Constitution):**  
عملیات بارگذاری فایل شیت و درج دسته‌ای رکوردها در پایگاه داده کارگاه، یک عملیات حساس تغییر داده (Mutation) است و حداقل نیازمند دسترسی `edit_reports` است.

**وضعیت در کد جاری:**  
در فایل [`apps/api/core/inventory/department_activity_data_views.py:33-42, 110`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_data_views.py#L33-L42):
```python
class _DepartmentActivityDataBase(APIView):
    permission_classes = [
        IsAuthenticated,
        IsProjectMember,
        HasProjectPermission,
        CanViewBusinessAssignments,
        IsVisitorReadOnly,
        IsHrOrAdminOrReadOnly,
    ]
    required_permission = 'view_reports'

class DepartmentActivityImportView(_DepartmentActivityDataBase):
    ...
```
کلاس `DepartmentActivityImportView` ویژگی `required_permission` را بازنویسی نکرده است. در نتیجه مجوزی که بررسی می‌شود فقط `view_reports` است! یعنی هر کاربری که در پروژه دسترسی صرفاً خواندن گزارشات را داشته باشد، می‌تواند فایل اکسل آپلود کرده و رکوردهای پایگاه داده را تغییر دهد.

---

### G08 — P2 — کاستی‌های ظاهری و فنی در خروجی اکسل فیلترشده (Export)

**شرح نیازمندی در SPEC-09 (داستان US-DP-03، سناریو ۱):**  
> «آنگاه خروجی دقیقاً شامل همان ردیف‌های فیلترشده با فرمت اکسل و فونت استاندارد فارسی صادر شود.»

**وضعیت در کد جاری:**  
در فایل [`apps/api/core/inventory/department_activity_io.py:112-154`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_io.py#L112-L154)، متد `export_activities_to_xlsx`:
1. ورک‌بوک را به صورت `Workbook(write_only=True)` می‌سازد و هیچ تنظیماتی برای جهت صفحه (RTL)، پهنای ستون‌ها، فونت استاندارد (وزیرمتن یا شبنم)، و هدرهای فارسی اعمال نمی‌کند.
2. هدرها به صورت کلمات انگلیسی خام (`date`, `location`, `activity_description`, `contractor`, `unit`, `description`) درج می‌شوند نه عناوین فارسی رسمی.
3. ستون «مقدار اجرا» در خروجی دپارتمان‌های غیرانباری وجود ندارد.
4. هدر رسمی پروژه (نام پروژه، کد کارگاه، بازه تاریخی فیلترشده، نام صادرکننده) در ابتدای شیت تعبیه نشده است.

---

## ۳. جدول جمع‌بندی اولویت‌بندی شکاف‌ها (Action Plan & Priority Matrix)

| کد شکاف | اولویت | عنوان شکاف | فایل‌های اصلی درگیر | نتیجه مورد انتظار و اقدام اصلاحی |
| :---: | :---: | :--- | :--- | :--- |
| **G01** | **P1** | فقدان فیلد «مقدار اجرا» (`executed_quantity`) در مدل و رابط کاربری | `inventory/models.py`, `serializers.py`, `department-activity-record-modal.tsx` | افزودن فیلد اعشاری `executed_quantity` به `DepartmentActivityRecord`، به‌روزرسانی سریالایزر و افزودن فیلد مقدار در فرم مودال غیرانباری |
| **G02** | **P1** | تولید PDF به جای اکسل در گزارش روزانه دپارتمان و عدم پشتیبانی از `date` | `department_activity_data_views.py`, `department_activity_io.py`, `department-page.tsx` | پیاده‌سازی متد `export_daily_department_report_xlsx` با هدر رسمی، ستون احجام و سطر جمع کل، خواندن پارامتر `date` و افزودن انتخاب‌گر تاریخ در UI |
| **G03** | **P1** | تولید PDF به جای اکسل هفتگی چندشیتی با فرمول‌های `=SUM(...)` | `department_activity_data_views.py`, `department_activity_io.py`, `department-page.tsx` | پیاده‌سازی `export_weekly_department_report_xlsx` با ۷ شیت روزانه + شیت خلاصه، تزریق فرمول‌های بومی اکسل، پذیرش `week_start` و افزودن انتخاب‌گر هفته در UI |
| **G04** | **P1** | فقدان تراکنش اتمیک و Rollback کامل در صورت بروز خطای سطری در Import | `department_activity_io.py`, `department-page.tsx` | پوشش کامل متد با `@transaction.atomic` و بازگرداندن وضعیت بدون درج رکورد در صورت وجود حتی ۱ سطر نامعتبر، و حذف منطق `importPartial` |
| **G05** | **P1** | فقدان ولیدیشن عددی مقدار اجرا در دپارتمان‌های غیرانباری و پیام خطای فارسی | `department_activity_io.py` | اعتبارسنجی مقادیر عددی اجرا در ایمپورت غیرانباری و صدور پیام ساختاریافته: «خطا در سطر X: مقدار اجرا باید عددی باشد» |
| **G06** | **P2** | مغایرت اسلاگ دپارتمان ابنیه (`civil` در برابر `buildings`) | `inventory/models.py`, `department_activity_services.py` | پذیرش اسلاگ `civil` به عنوان آلیاس رسمی `buildings` در پارامترها و پایگاه داده |
| **G07** | **P2** | نقص در دسترسی امنیتی اندپوینت ورود دسته‌ای (Import) | `department_activity_data_views.py` | تغییر `required_permission = 'edit_reports'` برای کلاس `DepartmentActivityImportView` |
| **G08** | **P2** | کاستی‌های خروجی اکسل فیلترشده (نبود RTL، فونت فارسی، هدر رسمی) | `department_activity_io.py` | افزودن استایل‌دهی RTL، فونت فارسی استاندارد، عناوین ستون فارسی و درج متادیتای پروژه در بالای فایل اکسل |
