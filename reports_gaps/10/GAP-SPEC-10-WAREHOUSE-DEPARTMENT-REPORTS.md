# سند نهایی ارزیابی شکاف‌ها و تحلیل انطباق: گزارشات و گردش مصالح دپارتمان انبار

**شناسه سند:** `GAP-SPEC-10-WAREHOUSE-DEPARTMENT-REPORTS`  
**سند مشخصات فنی هدف:** [`SPEC-10-WAREHOUSE-DEPARTMENT-REPORTS.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/atomic-specs/SPEC-10-WAREHOUSE-DEPARTMENT-REPORTS.md)  
**اسناد مرجع همبسته:**  
- [`reports_documentation/05-department-and-warehouse-reports/spec_001_warehouse.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/05-department-and-warehouse-reports/spec_001_warehouse.md)  
- [`reports_documentation/05-department-and-warehouse-reports/department-activity-records.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/05-department-and-warehouse-reports/department-activity-records.md)  
- [`apps/api/core/inventory/models.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/models.py)  
- [`apps/api/core/inventory/serializers.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/serializers.py)  
- [`apps/api/core/inventory/department_activity_io.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_io.py)  
- [`apps/api/core/inventory/department_activity_data_views.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_data_views.py)  
- [`apps/web/src/components/department/department-activity-record-modal.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/department/department-activity-record-modal.tsx)  
- [`apps/web/src/components/department/department-page.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/department/department-page.tsx)  
- [`docs/decision-tree/login/submit-valid-credentials/[open-legacy-project]/[open-warehouse-department]/`](file:///home/hossein/Desktop/projects/building-management/docs/decision-tree/login/submit-valid-credentials/[open-legacy-project]/[open-warehouse-department]/)  
**تاریخ ارزیابی:** ۶ آبان ۱۴۰۵ (2026-10-28)  
**وضعیت کلی انطباق:** ⚠️ **دارای شکاف‌های معماری و نیازمند بهبود در بالانس مصالح و اعتبارسنجی (Fail - Action Required)**

---

## ۱. خلاصه‌ی اجرایی و تحلیل انطباق (Executive Summary)

سند مشخصات فنی اتمیک **`SPEC-10-WAREHOUSE-DEPARTMENT-REPORTS`** ناظر بر مدیریت تخصصی دپارتمان انبار و تدارکات کارگاه، گردش ورود و خروج مصالح، بالانس تجمعی موجودی، اعتبارسنجی مقادیر مثبت با کد خطای استاندارد و تولید خروجی‌های رسمی اکسل منطبق بر استانداردهای گزارش‌نویسی کارگاه‌های عمرانی (فرمت شیراز) می‌باشد.

بررسی فنی عمیق کدهای جاری بک‌اند (`apps/api/core/inventory/`) و فرانت‌اند (`apps/web/src/components/department/`) نشان می‌دهد که اگرچه پس از اجرای SPEC-09، فیلدهای ۸ گانه انبار در دیتابیس و فرم ثبت ذخیره شده و خروجی اکسل جایگزین خروجی‌های قبلی PDF شده است، اما **۴ شکاف معماری اساسی و ۳ کمبود زیرساختی** در حوزه انبارداری و حسابداری مصالح وجود دارد:

1. **انحراف بنیادی شیت هشتم گزارش هفتگی از بالانس تجمعی مصالح (Cumulative Material Balance):**  
   در متد `generate_weekly_activity_report_xlsx`، شیت هشتم به عنوان «خلاصه هفتگی» تولید می‌شود، اما برای دپارتمان انبار:
   - صرفاً مقادیر ورودی (`quantity_in`) جمع زده می‌شود و کلیه مقادیر خروجی (`quantity_out`) کاملاً نادیده گرفته می‌شوند!
   - ردیف‌ها به جای `(material_type, unit)` بر اساس `(material_type, supplier, unit)` گروه‌بندی می‌شوند که عملاً گزارش عملکرد تأمین‌کنندگان است نه شیت بالانس موجودی انبار.
   - ستون «موجودی اول دوره» (`Opening Balance`) وجود ندارد و سوابق قبل از `week_start` اصلاً واکشی نمی‌شوند.
   - فرمول بومی اکسل برای «مانده پای کار / موجودی پایان دوره» (`=Opening + In - Out`) پیاده‌سازی نشده است.
2. **فقدان کد خطای استاندارد سرور `at_least_one_quantity_must_be_positive` و پیام خطای فارسی:**  
   در `serializers.py` و متد ورود اکسل `import_activities_from_xlsx`، هنگامی که هر دو مقدار `quantity_in` و `quantity_out` صفر یا منفی باشند، خطای پیش‌فرض با کد عمومی `invalid` یا `validation_error` برگردانده می‌شود. کد اختصاصی الزامی‌شده در سناریوی ۳ اسپک (`at_least_one_quantity_must_be_positive`) تنظیم نشده و شرح پیام به جای عبارت فارسی مصوب «حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد»، انگلیسی ترجمه‌شده است.
3. **نقص فرمول‌های گزارش روزانه انبار (فرمت کارگاه شیراز):**  
   شیت گزارش روزانه اکسل فاقد سطر/ستون محاسبه «تراز خالص گردش روزانه» (`Daily Net Balance = Total_In - Total_Out`) است و تنها سرجمع ورودی و سرجمع خروجی را به صورت مجزا درج می‌کند.
4. **فقدان اندپوینت اختصاصی وب‌سرویس بالانس مصالح انبار (`warehouse-balance`):**  
   سامانه هیچ اندپوینتی برای استعلام مانده جاری موجودی مصالح پروژه (`GET .../warehouse-balance/`) بر اساس گردش رکوردهای انبار ندارد و کلاینت‌ها بدون دانلود اکسل یا پردازش کلاینت‌ساید به موجودی پای کار دسترسی ندارند.
5. **نقایص تجربه کاربری فرانت‌اند (UX):**  
   ستون‌های مقادیر ورودی و خروجی فاقد قالب‌بندی عددی (جداکننده هزارگان و اعشار) هستند و دکمه‌های دانلود گزارش روزانه و هفتگی بدون اشاره به شیت بالانس مصالح یا فرمت شیراز با برچسب‌های عمومی نمایش داده می‌شوند.
6. **فقدان پوشش آزمون‌های گزارش اکسل انبار و سناریوی کد خطا:**  
   هیچ آزمون خودکاری برای توابع `generate_daily_activity_report_xlsx` و `generate_weekly_activity_report_xlsx` در انبار وجود ندارد و تست موجود در `tests.py` کد خطای `at_least_one_quantity_must_be_positive` را اعتبارسنجی نمی‌کند.
7. **نواقص درخت تصمیم‌گیری (Decision Tree):**  
   مستندات `docs/decision-tree/.../[open-warehouse-department]/` نیازمند به‌روزرسانی برای تبیین شیت بالانس تجمعی مصالح، فرمت شیراز و کد خطای مذکور هستند.

---

### جدول ماتریس ارزیابی انطباق سناریوها

| شناسه سناریو | شرح در سند مشخصات فنی (SPEC-10) | وضعیت انطباق | علت و شواهد در کد موجود |
| :--- | :--- | :---: | :--- |
| **US-WH-01 (سناریو ۱)** | ثبت موفق رسید ورود کالا با فیلدهای ۸گانه (نوع مصالح، مقدار ورودی، واحد، تأمین‌کننده، بارنامه) و افزایش موجودی | ⚠️ انطباق نسبی (P1) | فیلدها در مدل و فرم ذخیره می‌شوند؛ اما مفهوم موجودی و بالانس تجمعی در هیچ اندپوینتی محاسبه و نگهداری نمی‌شود. |
| **US-WH-01 (سناریو ۲)** | ثبت موفق حواله خروج مصالح با مقدار خروجی، محل مصرف و تحویل‌گیرنده و کاهش موجودی | ⚠️ انطباق نسبی (P1) | فیلد خروج و محل مصرف ذخیره می‌شود؛ اما اثر کاهنده آن در بالانس تجمعی هفتگی اکسل نادیده گرفته شده است. |
| **US-WH-01 (سناریو ۳)** | اعتبارسنجی ثبت همزمان صفر برای ورودی و خروجی با توقف تراکنش و صدور خطای سرور با کد دقیق `at_least_one_quantity_must_be_positive` | ❌ شکاف بحرانی (P1) | سرور کد عمومی `validation_error` صادر می‌کند نه `at_least_one_quantity_must_be_positive`؛ پیام فارسی مصوب در بک‌اند تنظیم نشده است. |
| **US-WH-02 (سناریو ۱)** | تولید گزارش روزانه انبار با هدر استاندارد، ستون‌های ۸گانه و فرمت شیت بالانس مصالح کارگاه شیراز | ⚠️ انطباق ناقص (P2) | هدر و ستون‌ها وجود دارند، اما فرمول تراز خالص روزانه (`=In - Out`) و استانداردهای فرمت شیراز غایب است. |
| **US-WH-02 (سناریو ۲)** | شیت بالانس تجمعی مصالح در گزارش هفتگی شامل موجودی اول دوره، کل ورودی، کل خروجی، مانده پای کار با فرمول اکسل | ❌ شکاف بحرانی (P1) | شیت ۸ فقط ورودی‌ها را با تفکیک تأمین‌کننده جمع می‌زند؛ خروجی‌ها حذف شده‌اند، موجودی اول دوره محاسبه نمی‌شود و فرمول مانده وجود ندارد. |

---

## ۲. یافته‌های تفصیلی و شواهد کد (Detailed Findings & Code Evidence)

### G01 — P1 — انحراف شیت هشتم گزارش هفتگی از بالانس تجمعی مصالح و حذف خروجی‌ها
**مرجع در SPEC-10 (داستان US-WH-02، سناریو ۲):**
> «یک شیت بالانس تجمعی حاوی ستون‌های: «موجودی اول دوره»، «کل ورودی دوره»، «کل خروجی دوره» و «مانده پای کار» به همراه فرمول‌های حسابداری انبار در فایل اکسل تعبیه شده باشد.»

**شواهد در کد جاری ([`apps/api/core/inventory/department_activity_io.py:691-736`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_io.py#L691-L736)):**
```python
    # Group records by (item_desc, entity_name, unit)
    grouped: dict[tuple[str, str, str], dict[int, float]] = {}
    for rec in records:
        if warehouse:
            key = (rec.material_type, rec.supplier, rec.unit)
            qty = float(rec.quantity_in or 0)
        else:
            key = (rec.activity_description, rec.contractor, rec.unit)
            qty = float(rec.executed_quantity or 0)
...
    # Row Data
    row_data = [
        idx,
        key[0], # material_type
        key[1], # supplier
        key[2], # unit
        days_dict[0], ... days_dict[6],
        f'=SUM(E{s_row}:K{s_row})',
    ]
```
همچنین در کنترلر [`DepartmentActivityWeeklyReportView`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_data_views.py#L298-L309):
```python
    qs = DepartmentActivityRecord.objects.filter(
        project_id=project_pk,
        department__in=dept_filter,
        date__gte=week_start,
        date__lte=week_end,
    ).order_by('date', '-created_at')
```
**تحلیل نقص فنی:**
1. متغیر `qty` صرفاً از `quantity_in` مقداردهی می‌شود و کل مصارف و حواله‌های خروج (`quantity_out`) نادیده گرفته می‌شوند.
2. تفکیک ردیف‌ها بر مبنای `supplier` انجام شده است؛ در صورتی که سیمان تیپ ۲ از دو تأمین‌کننده وارد شده باشد، در دو ردیف مجزا قرار می‌گیرد و بالانس موجودی کل کارگاه برای آن مصالح شکل نمی‌گیرد.
3. موجودی اول دوره (`Opening Balance`) صفر فرض شده یا وجود ندارد، زیرا کوئری‌ست `qs` تنها رکوردهای بین `week_start` و `week_end` را فیلتر کرده و هیچ اطلاعی از موجودی انتقالی پیش از هفته جاری ندارد. مصالحی هم که در طول هفته ورودی جدید نداشته‌اند اما در کارگاه موجودند، اصلاً در شیت ظاهر نمی‌شوند.
4. هیچ فرمولی برای مانده پایان دوره (`=موجودی اول دوره + کل ورودی - کل خروجی`) وجود ندارد.

---

### G02 — P1 — عدم صدور کد خطای صریح `at_least_one_quantity_must_be_positive` و فقدان پیام فارسی
**مرجع در SPEC-10 (داستان US-WH-01، سناریو ۳):**
> «با فرض اینکه کاربر در هر دو فیلد quantity_in و quantity_out مقدار ۰ وارد کند، هنگامی که فرم ذخیره شود، آنگاه سرور با خطای `at_least_one_quantity_must_be_positive` تراکنش را متوقف سازد.»  
> همراه با پیام: «حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد».

**شواهد در کد جاری ([`apps/api/core/inventory/serializers.py:188-201`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/serializers.py#L188-L201)):**
```python
    if (
        'quantity_in' not in errors
        and 'quantity_out' not in errors
        and quantity_in <= 0
        and quantity_out <= 0
    ):
        msg = _(
            'At least one of quantity_in or quantity_out must be greater than zero.'
        )
        errors['quantity_in'] = msg
        errors['quantity_out'] = msg

    if errors:
        raise serializers.ValidationError(errors)
```
و در متد ورود دسته‌ای ([`apps/api/core/inventory/department_activity_io.py:935-948`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_io.py#L935-L948)):
```python
    if (
        'quantity_in' not in row_errors
        and 'quantity_out' not in row_errors
        and quantity_in <= 0
        and quantity_out <= 0
    ):
        msg = str(
            _(
                'At least one of quantity_in or quantity_out must be greater than zero.'
            )
        )
        row_errors['quantity_in'] = msg
        row_errors['quantity_out'] = msg
```
**تحلیل نقص فنی:**
- سریالایزر از کلاس استاندارد `serializers.ValidationError(errors)` استفاده می‌کند و هیچ پارامتر `code='at_least_one_quantity_must_be_positive'` یا آبجکت `ErrorDetail` با این کد تنظیم نمی‌کند.
- سیستم مدیریت خطای سفارشی پروژه در [`apps/api/core/config/exceptions.py:107`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/config/exceptions.py#L107)، در صورت نبود کد ساختاریافته، مقدار پیش‌فرض `validation_error` را به عنوان کد خطا بازمی‌گرداند.
- پیام خطا انگلیسی است و پیام خطای مصوب فارسی در پاسخ لایه کنترلر یا سریالایزر درج نمی‌شود.

---

### G03 — P2 — فقدان فرمول تراز خالص روزانه در گزارش روزانه (فرمت کارگاه شیراز)
**مرجع در SPEC-10 (داستان US-WH-02، سناریو ۱):**
> «فایل اکسلی حاوی ستون‌های ۸گانه فارسی با فرمت شیت بالانس مصالح کارگاه شیراز تولید و تحویل کاربر گردد.»

**شواهد در کد جاری ([`apps/api/core/inventory/department_activity_io.py:431-454`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/department_activity_io.py#L431-L454)):**
```python
    if warehouse:
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
        lbl_in = ws.cell(row=current_row, column=1, value='مجموع ورودی:')
        sum_in = ws.cell(row=current_row, column=4)
        sum_in.value = f'=SUM(D5:D{current_row - 1})' if records else 0

        lbl_out = ws.cell(row=current_row, column=5, value='مجموع خروجی:')
        sum_out = ws.cell(row=current_row, column=6)
        sum_out.value = f'=SUM(F5:F{current_row - 1})' if records else 0
```
**تحلیل نقص فنی:**
- در انبارداری کارگاه شیراز، علاوه بر مجموع ورودی و مجموع خروجی، ردیف/بخش «تراز خالص گردش مصالح روزانه» (`Daily Net Balance = Total In - Total Out`) الزامی است تا مشخص شود در آن روز کارگاه جذب‌کننده مصالح بوده یا مصرف‌کننده، و موجودی پای کار چه تغییری کرده است.
- عنوان شیت و عنوان سربرگ فاقد عبارت استاندارد سازمانی است:
  «گزارش روزانه گردش مصالح و بالانس انبار کارگاه — پروژه {proj_name}».

---

### G04 — P2 — فقدان اندپوینت اختصاصی وب‌سرویس بالانس مصالح انبار (`warehouse-balance`)
**مرجع در نیازمندی‌های معماری سیستم:**
> دسترسی بلادرنگ به موجودی پای کار مصالح تفکیک‌شده به `(material_type, unit)` از طریق API:
> `GET /api/v1/projects/{project_id}/department-activity-records/warehouse-balance/`

**وضعیت در کد جاری:**
- هیچ روت یا ویویی برای محاسبه موجودی خالص مصالح انبار در روت‌های `inventory.project_urls` یا `sub_reports` وجود ندارد.
- در حال حاضر تنها روش مطلع شدن از موجودی مصالح، دانلود اکسل یا خواندن کل رکوردهای انبار و جمع‌زدن دستی در فرانت‌اند است.

---

### G05 — P2 — نقایص رابط کاربری دپارتمان انبار (عدم قالب‌بندی اعداد و برچسب‌های عمومی)
**شواهد در کد جاری ([`apps/web/src/components/department/department-page.tsx:348-376`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/department/department-page.tsx#L348-L376)):**
```tsx
    {
      id: "quantity_in",
      header: t("businessDepartment.activityLog.columns.quantityIn"),
      accessorKey: "quantity_in",
      cell: ({ row }) => (
        <span id={`text-departmentActivityQuantityIn-${row.index}`}>
          {row.original.quantity_in ?? "—"}
        </span>
      ),
    },
```
**تحلیل نقص فنی:**
1. مقادیر عددی `quantity_in` و `quantity_out` به صورت رشته خام رندر می‌شوند و هیچ تابعی برای درج کاما (جداکننده سه‌رقمی) یا نمایش ارقام فارسی وجود ندارد.
2. دکمه‌های دانلود گزارش روزانه و هفتگی (خطوط ۷۷۲ و ۷۸۴) از کلید‌های ترجمه عمومی استفاده می‌کنند («خروجی لاگ فعالیت» و «گزارش هفتگی»)؛ در حالی که برای انبار باید مشخصاً عنوان «گزارش روزانه انبار (شیراز)» و «گزارش هفتگی و بالانس مصالح» را منعکس نمایند.
3. کارت یا خلاصه‌ای از موجودی‌های بحرانی انبار در بالای جدول وجود ندارد.

---

### G06 — P3 — فقدان تست‌های اختصاصی گزارش اکسل انبار و اعتبارسنجی کد خطا
**شواهد در کد جاری ([`apps/api/core/inventory/tests.py:795-807`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/inventory/tests.py#L795-L807)):**
```python
    def test_warehouse_create_rejects_both_quantities_zero(self):
        response = self.client.post(
            self.url,
            self._warehouse_payload(quantity_in='0', quantity_out='0'),
        )
        self.assertEqual(response.status_code, 400)
        details = response.data.get('error', {}).get('details', {})
        self.assertTrue(
            'quantity_in' in details
            or 'quantity_out' in details
            or 'non_field_errors' in details
        )
```
**تحلیل نقص فنی:**
- تست موجود صرفاً کد وضعیت ۴۰۰ را چک می‌کند و صراحتاً بررسی نمی‌کند که `response.data['error']['code'] == 'at_least_one_quantity_must_be_positive'` باشد.
- هیچ تستی برای توابع `generate_daily_activity_report_xlsx` و `generate_weekly_activity_report_xlsx` و صحت فرمول‌های بومی محاسباتی اکسل برای دپارتمان انبار نوشته نشده است.

---

### G07 — P3 — لزوم به‌روزرسانی نودهای درخت تصمیم‌گیری (Decision Tree)
**شواهد در مستندات جاری:**
در پوشه [`docs/decision-tree/login/submit-valid-credentials/[open-legacy-project]/[open-warehouse-department]/`](file:///home/hossein/Desktop/projects/building-management/docs/decision-tree/login/submit-valid-credentials/[open-legacy-project]/[open-warehouse-department]/):
- فایل `download-weekly-activity-report/README.md` صرفاً به «دانلود هشت ورک‌شیت با فرمول جمع» اشاره کرده و ساختار شیت بالانس تجمعی مصالح، ستون‌های موجودی اول دوره و فرمول موجودی پای کار را مستند نکرده است.
- فایل `download-daily-activity-report/README.md` تراز خالص روزانه کارگاه شیراز را منعکس نکرده است.
- فایل `[create-activity-record]/README.md` کد خطای `at_least_one_quantity_must_be_positive` را به عنوان گارد اعتبارسنجی قید ننموده است.
- تصمیم جدید برای استعلام موجودی انبار (`[query-warehouse-balance]`) ثبت نشده است.

---

## ۳. طرح معماری و راهکار فنی (Target Architecture & Remediation)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SPEC-10 TARGET STATE                            │
└────────────────────────────────────────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼──────────────────────────────┐
    ▼                               ▼                              ▼
[ 1. Validation & Error Codes ]  [ 2. Excel Reporting Engine ]   [ 3. Material Balance API ]
- CodedValidationError           - Daily Shiraz Format:          - GET .../warehouse-balance/
- code:                            * Inbound, Outbound           - Aggregates by (material, unit)
  'at_least_one_quantity_          * Net Daily Flow Formula      - Computes:
   must_be_positive'             - Weekly 8th Sheet:               * Opening Balance
- Persian Error Message:           * Grouped by (material, unit)   * Total Inbound
  «حداقل یکی از مقادیر ورودی      * Opening Balance (Dynamic)     * Total Outbound
   یا خروجی باید بزرگتر از         * Total In / Total Out          * Current Balance
   صفر باشد»                       * Closing Balance Formula       * Last Movement Date
                                     (=D5+E5-F5)
```

### ۱. معماری شیت هشتم گزارش هفتگی انبار (شیت بالانس تجمعی مصالح)
در ماژول `department_activity_io.py` و متد `generate_weekly_activity_report_xlsx`:
1. چنانچه `warehouse == True` باشد، شیت هشتم به جای «خلاصه هفتگی»، تحت عنوان **«بالانس تجمعی مصالح»** نام‌گذاری می‌شود.
2. ستون‌های جدول شیت بالانس:
   - ستون A (ردیف - Row)
   - ستون B (نوع مصالح - Material Type)
   - ستون C (واحد - Unit)
   - ستون D (موجودی اول دوره - Opening Balance): مانده موجودی پیش از `week_start`
   - ستون E (کل ورودی دوره - Total Inbound)
   - ستون F (کل خروجی دوره - Total Outbound)
   - ستون G (مانده پای کار / موجودی پایان دوره - Closing Balance): با فرمول بومی اکسل `=D{row}+E{row}-F{row}`
   - ستون H (توضیحات و وضعیت اقلام - Notes)
3. نحوه تأمین موجودی اول دوره:
   - متد ویو `DepartmentActivityWeeklyReportView` قبل از فراخوانی تولید اکسل، تجمیع سوابق انبار پروژه را پیش از تاریخ `week_start` محاسبه کرده و به عنوان یک دیکشنری `opening_balances: dict[tuple[str, str], Decimal]` به تابع ارسال می‌کند.
   - کلیه مصالحی که در سوابق دارای مانده مثبت بوده‌اند، حتی در صورت عدم ثبت تراکنش در طول هفته، در جدول بالانس آورده می‌شوند تا کنترل انبارداری کامل شود.
4. ردیف مجموع (Total Row) با فرمول‌های `=SUM(D5:D...)`، `=SUM(E5:E...)`، `=SUM(F5:F...)` و `=SUM(G5:G...)`.

### ۲. اعتبارسنجی سرور و کد خطای `at_least_one_quantity_must_be_positive`
1. در `serializers.py` و متد `validate` برای دپارتمان انبار:
   ```python
   if (
       'quantity_in' not in errors
       and 'quantity_out' not in errors
       and quantity_in <= 0
       and quantity_out <= 0
   ):
       fa_msg = 'حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد'
       errors['quantity_in'] = fa_msg
       errors['quantity_out'] = fa_msg
       raise CodedValidationError(
           errors,
           code='at_least_one_quantity_must_be_positive'
       )
   ```
2. در متد `import_activities_from_xlsx` در `department_activity_io.py`:
   در صورت صفر بودن ورودی و خروجی:
   ```python
   row_errors['quantity_in'] = 'حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد'
   row_errors['quantity_out'] = 'حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد'
   row_errors['code'] = 'at_least_one_quantity_must_be_positive'
   ```
   و در پاسخ ویوی ایمپورت، کد خطای `at_least_one_quantity_must_be_positive` همراه با پیام فارسی بازگردانده می‌شود.

### ۳. گزارش روزانه با فرمت کارگاه شیراز
در `generate_daily_activity_report_xlsx`:
1. عنوان سربرگ:
   `گزارش روزانه گردش مصالح و انبار کارگاه — پروژه {proj_name}`
2. ردیف‌های محاسباتی انتهای جدول:
   - ردیف اول: ستون ۱ تا ۳: «مجموع ورودی روز:» | ستون ۴: `=SUM(D5:D{row-1})` | ستون ۵: «مجموع خروجی روز:» | ستون ۶: `=SUM(F5:F{row-1})`
   - ردیف دوم: ستون ۱ تا ۵: «تراز خالص گردش مصالح روز (خالص افزایش / کاهش موجودی):» | ستون ۶: `=D{row_tot}-F{row_tot}` با استایل برجسته و رنگ متمایز.

### ۴. طراحی اندپوینت استعلام بالانس مصالح انبار
- مسیر: `GET /api/v1/projects/{project_pk}/department-activity-records/warehouse-balance/`
- دسترسی: `IsAuthenticated, IsProjectMember, HasProjectPermission, CanViewBusinessAssignments, IsVisitorReadOnly, IsHrOrAdminOrReadOnly` با مجوز `view_reports`.
- پارامترها: `as_of_date` (اختیاری، پیش‌فرض امروز)، `search` (جستجوی نام مصالح).
- خروجی ساختاریافته شامل نام مصالح، واحد، کل ورودی، کل خروجی، مانده جاری و تاریخ آخرین گردش.

### ۵. ارتقای رابط کاربری فرانت‌اند (`apps/web`)
1. قالب‌بندی مقادیر در جدول:
   استفاده از `Number(val).toLocaleString('fa-IR')` یا کامپوننت فرمت‌دهنده اعداد در ستون‌های ورودی و خروجی.
2. برچسب‌گذاری دقیق اکشن‌های انبار:
   نمایش عناوین اختصاصی انبار در صورت `isWarehouse == true`:
   - «دانلود گزارش روزانه انبار (شیراز)»
   - «دانلود گزارش هفتگی و بالانس تجمعی مصالح (۸ شیت)»
3. هماهنگی مودال ثبت رکورد با کد خطای `at_least_one_quantity_must_be_positive` و استخراج مستقیم پیام سرور.

---

## ۴. برنامه و چک‌لیست اقدامات اصلاحی (Action Plan)

- [ ] **اقدام ۱ (بک‌اند - بالانس تجمعی اکسل):** بازنویسی شیت هشتم هفتگی برای انبار تحت عنوان «بالانس تجمعی مصالح»، گروه‌بندی بر اساس `(material_type, unit)`، محاسبه پویای موجودی اول دوره قبل از `week_start`، درج ستون‌های کل ورودی و کل خروجی، و درج فرمول بومی `=D+E-F` برای مانده پای کار.
- [ ] **اقدام ۲ (بک‌اند - گزارش روزانه شیراز):** درج فرمول تراز خالص گردش مصالح روز (`=In - Out`) در سطر جمع‌بندی اکسل روزانه و اصلاح هدر رسمی کارگاه شیراز.
- [ ] **اقدام ۳ (بک‌اند - اعتبارسنجی و کد خطا):** اعمال `CodedValidationError` با کد `at_least_one_quantity_must_be_positive` و پیام فارسی «حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد» در سریالایزر و فرآیند ایمپورت.
- [ ] **اقدام ۴ (بک‌اند - اندپوینت وب‌سرویس بالانس):** پیاده‌سازی ویو و روت `GET .../warehouse-balance/` جهت تجمیع و بازگرداندن مانده‌های جاری مصالح کارگاه.
- [ ] **اقدام ۵ (فرانت‌اند - فرمت اعداد و برچسب‌های انبار):** به‌روزرسانی `department-page.tsx` جهت فرمت‌بندی اعداد ورودی/خروجی و تفکیک برچسب‌های دانلود گزارش انبار.
- [ ] **اقدام ۶ (تست‌های خودکار - TDD):** افزودن تست‌های جامع pytest برای اعتبارسنجی کد خطای `at_least_one_quantity_must_be_positive`، تست تولید شیت بالانس تجمعی هفتگی با فرمول‌های بومی، و تست وب‌سرویس بالانس مصالح.
- [ ] **اقدام ۷ (درخت تصمیم‌گیری):** به‌روزرسانی دایرکتوری‌های `docs/decision-tree/.../[open-warehouse-department]/` و ثبت سناریوهای بالانس مصالح، فرمت شیراز و کدهای خطا.
