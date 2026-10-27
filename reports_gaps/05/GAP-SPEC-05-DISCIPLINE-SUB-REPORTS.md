# سند نهایی ارزیابی شکاف‌ها و تحلیل انطباق: ساب‌ریپورت‌های تخصصی دیسیپلین‌ها

**شناسه سند:** `GAP-SPEC-05-DISCIPLINE-SUB-REPORTS`  
**سند مشخصات فنی هدف:** [`SPEC-05-DISCIPLINE-SUB-REPORTS.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md)  
**اسناد مرجع همبسته:**  
- [`01-.../مستندات فرم‌های اکسل شیراز (FILE 5 و FILE 6)`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/01-core-requirements-and-excel-blueprints/مستندات%20فرم‌های%20اکسل%20شیراز%20(Shiraz%20Excel%20Forms%20Documentation).md)  
- [`03-.../sub_reports_ENDPOINTS.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/03-daily-field-reports-and-apis/sub_reports_ENDPOINTS.md)  
- [`07-.../discipline-sub-reports-user-flow.md`](file:///home/hossein/Desktop/projects/building-management/reports_documentation/07-decision-tree-and-user-flows/discipline-sub-reports-user-flow.md)  
- [`specs/032-unit-report-source-truth/spec.md`](file:///home/hossein/Desktop/projects/building-management/specs/032-unit-report-source-truth/spec.md)  
- [`specs/033-daily-sections-grid/spec.md`](file:///home/hossein/Desktop/projects/building-management/specs/033-daily-sections-grid/spec.md)  
**تاریخ ارزیابی:** ۶ آبان ۱۴۰۵ (2026-10-28)  
**دامنه ارزیابی:**  
- بک‌اند: `apps/api/core/sub_reports/` (مدل‌ها، سرویس‌ها، سریالایزرها، ویوها، مسیرها، تست‌ها)، `apps/api/core/field_reports/services/daily_report_aggregation.py`، `apps/api/core/common/reporting_units.py`  
- فرانت‌اند: `apps/web/src/components/department/`، `apps/web/src/components/sub_reports/`، `apps/web/src/app/lib/api/unit-reports.ts`، `apps/web/src/app/routes/`  
**وضعیت کلی سند:** ❌ **دارای شکاف‌های بحرانی و مغایرت‌های معماری بنیادین (Fail - Blocked for Parity)**

---

## ۱. خلاصه‌ی اجرایی و تحلیل انطباق (Executive Summary)

سند مشخصات فنی اتمیک **`SPEC-05-DISCIPLINE-SUB-REPORTS`** وظیفه تعریف و ثبت ساب‌ریپورت‌های مستقل و تخصصی توسط سرپرستان واحدهای اجرایی (ابنیه و سازه، تأسیسات الکتریکی، تأسیسات مکانیکی، لوله‌کشی، تهویه مطبوع و معماری/نازک‌کاری) را بر اساس ساختار فرم‌های اکسل شیراز (FILE 5 ابنیه و FILE 6 برق) بر عهده دارد.

بررسی عمیق مخزن کد نشان می‌دهد که بین مشخصات تعریف‌شده در **SPEC-05** و وضعیت پیاده‌سازی جاری یک **انقطاع دوگانه (Architectural Bifurcation)** وجود دارد:
1. **واگرایی معماری مسیرها و موجودیت‌ها (Legacy vs Canonical):**  
   مجموعه اندپوینت‌های سنتی `/api/v1/projects/{project_id}/sub-reports/` که در مستندات ENDPOINTS و User Flow برای ساب‌ریپورت‌ها ذکر شده بودند، در جریان ویژگی `032-unit-report-source-truth` لغو ثبت (Unregister) شده و کلاس تست آن‌ها [`TestSubReportsAPI`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/tests/test_sub_reports.py#L35) به صورت کامل `@pytest.mark.skip` شده است. به جای آن، مسیرهای کانونیکال `/api/v1/projects/{project_id}/units/{unit}/daily-reports/` ایجاد شده‌اند. با این حال، دامنه کسب‌وکار SPEC-05 شامل دیسیپلین‌های ۶ گانه، فیلدهای اختصاصی ابنیه، تست‌های مکانیک و قوانین اعتبارسنجی در ساختار جدید به درستی بازطراحی یا حفظ نشده‌اند.
2. **فقدان فیلدها و اعتبارسنجی‌های تخصصی دیسیپلین‌ها:**
   - فیلد درصد اجرای روزانه (`daily_percent` یا `execution_percentage`) و اعتبارسنجی بازه ۰ تا ۱۰۰ همراه با خطای `percent_must_be_between_0_and_100` نه در سریالایزر کانونیکال فعالیت‌ها و نه در فرم فرانت‌اند وجود ندارد.
   - امکان ارسال ساب‌ریپورت کاملاً تهی و خالی وجود دارد و هیچ ممانعتی با خطای `cannot_submit_empty_sub_report` انجام نمی‌شود.
   - بخش مصالح (`materials`) در فرانت‌اند برای واحد مکانیک به طور کامل غیرفعال (Disable) است و هیچ لیست پیشنهاد سریعی برای اقلام مکانیکی (لوله ۵ لایه، پلیکا و...) وجود ندارد.
   - هیچ سازوکاری برای ثبت تست‌های هیدرواستاتیک و فشار مکانیکی و اتصال آن‌ها به ماژول کنترل کیفیت (`risk.Inspection`) در سیستم پیاده‌سازی نشده است.
   - تخصیص اکیپ پیمانکار به فعالیت‌ها هیچ تأثیری در کارکرد و ساعات کاری پیمانکار در سیستم ندارد.

---

### جدول ماتریس ارزیابی انطباق سناریوها

| شناسه داستان / سناریو | شرح در سند مشخصات (SPEC-05) | وضعیت انطباق | علت و خلاصه شواهد در کد جاری |
| :--- | :--- | :---: | :--- |
| **Enum دیسیپلین‌ها** | تعریف دیسیپلین‌های ۶‌گانه (`CIVIL`, `ELECTRICAL`, `MECHANICAL`, `PLUMBING`, `HVAC`, `FINISHING`) | ⚠️ مغایرت ساختاری | در مدل دیسیپلین حروف کوچک (`civil`, ...) است؛ اما در معماری جدید ۶ واحد کانونیکال (`SpecialtyUnit`) جایگزین شده که `civil/finishing` را به `buildings` و `plumbing/hvac` را به `mechanical` ادغام کرده است. |
| **US-SR-01 (سناریو ۱)** | ثبت ردیف فعالیت عمرانی با درصد اجرای روزانه (`daily_percent`) و اکیپ | ❌ شکاف داده و UI | در مدل وجود دارد؛ اما در سریالایزر کانونیکال [`UnitReportActivitySectionSerializer`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/serializers.py#L47) و در فرم فرانت‌اند [`section-activities.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/department/section-activities.tsx#L55) این فیلد حذف شده است. |
| **US-SR-01 (سناریو ۲)** | اعتبارسنجی بازه درصد اجرا (۰ تا ۱۰۰) با خطای `percent_must_be_between_0_and_100` | ❌ شکاف اعتبارسنجی | هیچ اعتبارسنجی Min/Max روی فیلد وجود ندارد و خطای `percent_must_be_between_0_and_100` در کل مخزن کد تعریف نشده است. |
| **US-SR-01 (سناریو ۳)** | اتصال پیمانکار دست‌دوم و منظور شدن کارکرد به حساب پیمانکار | ❌ شکاف منطق تجاری | `contractor_ref` ذخیره می‌شود اما هیچ منطقی برای ثبت ساعت کاری در حساب/تایم‌شیت پیمانکاران در اپلیکیشن `subcontractors` وجود ندارد. |
| **US-SR-02 (سناریو ۱)** | ثبت ردیف‌های برقی با واحد متر/عدد و دیسیپلین `ELECTRICAL` | ⚠️ انطباق نسبی | امکان ثبت فعالیت برای واحد `electrical` وجود دارد اما به صورت `unit='electrical'` است نه دیسیپلین مستقل؛ ردیف‌ها فاقد جداسازی ساختاری فیلدها هستند. |
| **US-SR-02 (سناریو ۲)** | تفکیک و عدم دسترسی به فیلدهای عمرانی (رده بتن، بچینگ) در فرم برق | ✅ منطبق | در کامپوننت [`unit-daily-report-panel.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/department/unit-daily-report-panel.tsx#L10) سکشن بتن برای واحد برق پنهان و غیرفعال است. |
| **US-SR-03 (سناریو ۱)** | انتخاب دیسیپلین MECHANICAL/HVAC و پیشنهاد خودکار مصالح مکانیکی (پلیکا، ۵ لایه و...) | ❌ شکاف کامل UI/API | سکشن مصالح برای واحد مکانیک غیرفعال (`unitSupportsMaterialsSection` فقط برای `warehouse` فعال است) و لیست پیشنهاد سریع وجود ندارد. |
| **US-SR-03 (سناریو ۲)** | ثبت تست هیدرواستاتیک و فشار لوله‌کشی و اتصال به مستند کنترل کیفیت | ❌ شکاف کامل مدل و سرویس | هیچ مدل، فیلد، رابط یا اتصال QC برای تست‌های هیدرواستاتیک مکانیک پیاده‌سازی نشده است. |
| **US-SR-04 (سناریو ۱)** | ارسال ساب‌ریپورت (Submit) از Draft به SUBMITTED و فراخوانی رول‌آپ خودکار | ⚠️ انطباق نسبی | متد ارسال وضعیت را به `SUBMITTED` تغییر داده و `rebuild_daily_report_summary` را صدا می‌زند؛ اما اندپوینت آن به جای `/sub-reports/{id}/submit/` روی روت کانونیکال است. |
| **US-SR-04 (سناریو ۲)** | تأیید ساب‌ریپورت (Approve) و قفل شدن ویرایش فیلدهای داخلی | ✅ منطبق | تغییر وضعیت به `APPROVED` انجام شده و ویرایش در وضعیت تأییدشده مسدود می‌گردد. |
| **US-SR-04 (سناریو ۳)** | ممانعت از ارسال ساب‌ریپورت فاقد ردیف با خطای `cannot_submit_empty_sub_report` | ❌ باگ/شکاف بحرانی | ارسال ساب‌ریپورت کاملاً خالی با وضعیت HTTP 200 با موفقیت انجام می‌شود و هیچ خطای ممانعتی وجود ندارد. |
| **مسیرها و روت‌ها** | صفحات `/projects/:projectId/sub-reports` و ثبت مستقل ساب‌ریپورت | ❌ شکاف فرانت‌اند | روت‌های فوق در React Router وجود ندارند؛ کامپوننت `SpecialtyContributionForm.tsx` یتیم و بلااستفاده رها شده است. |

---

## ۲. یافته‌های تفصیلی و شواهد کد (Detailed Findings & Code Evidence)

### G01 — P1 — عدم اعتبارسنجی بازه ۰ تا ۱۰۰ درصد و فقدان کد خطای `percent_must_be_between_0_and_100`

**شرح نیازمندی:**  
در سناریوی ۲ از داستان کاربردی US-SR-01 صراحتاً قید شده است که سرپرست ابنیه هنگام ثبت فعالیت عمرانی، درصد اجرای روزانه (`daily_percent`) را مشخص می‌کند. در صورتی که کاربر عددی منفی یا بزرگتر از ۱۰۰ وارد کند، سیستم باید با کد خطای صریح `percent_must_be_between_0_and_100` از ذخیره‌سازی ردیف ممانعت به عمل آورد.

**وضعیت در کد جاری:**  
در مدل [`DisciplineSubReportActivity`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/models.py#L248):
```python
execution_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
```
فیلد `execution_percentage` فاقد هرگونه اعتبارسنجی (`MinValueValidator(0)` یا `MaxValueValidator(100)`) در سطح مدل است. همچنین در سریالایزرهای [`sub_reports/serializers.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/serializers.py) هیچ متد `validate_execution_percentage` وجود ندارد.  
جستجوی سراسری رشته `percent_must_be_between_0_and_100` در کل مخزن کد نشان می‌دهد که این کد خطا فقط در فایل سند SPEC-05 ذکر شده و در هیچ فایل پایتون یا تایپ‌اسکریپت وجود خارجی ندارد.

---

### G02 — P1 — حذف و عدم پشتیبانی از `execution_percentage` در سریالایزر کانونیکال و فرم فرانت‌اند

**شرح نیازمندی:**  
بر اساس فرم استاندارد شیراز FILE 5 و US-SR-01، ثبت درصد پیشرفت روزانه برای فعالیت‌های عمرانی الزامی و منحصر‌به‌فرد است.

**وضعیت در کد جاری:**  
در جریان ارتقای سیستم به کانونیکال یونیت‌ها (ویژگی 033)، سریالایزر اصلی ردیف فعالیت‌ها به [`UnitReportActivitySectionSerializer`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/serializers.py#L47-L109) تغییر یافته است. لیست فیلدهای این سریالایزر به شرح زیر است:
```python
class Meta:
    model = DisciplineSubReportActivity
    fields = [
        'id', 'sync_revision', 'row_number', 'shift', 'crew_name',
        'foreman_count', 'worker_count', 'headcount', 'activity_ref',
        'activity_code', 'activity_name', 'activity_description',
        'contractor_ref', 'contractor_name', 'parcel', 'zone',
        'block', 'floor', 'quantity', 'unit', 'notes',
    ]
```
فیلد `execution_percentage` (یا `daily_percent`) به طور کامل از این سریالایزر **حذف** شده است!  
در سمت فرانت‌اند نیز، در فایل [`section-activities.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/department/section-activities.tsx#L55-L87)، ساختار `ActivityFormState` و `EMPTY_ACTIVITY_FORM` فاقد فیلد درصد است:
```typescript
interface ActivityFormState {
  activity_ref: string;
  activity_description: string;
  shift: string;
  contractor_ref: string;
  crew_name: string;
  foreman_count: string;
  worker_count: string;
  parcel: string;
  block: string;
  floor: string;
  zone: string;
  quantity: string;
  unit: string;
  notes: string;
}
```
در نتیجه سرپرست ابنیه هیچ امکانی برای ثبت یا مشاهده درصد پیشرفت روزانه فعالیت در رابط کاربری ندارد.

---

### G03 — P1 — امکان ارسال ساب‌ریپورت کاملاً خالی و فقدان خطای `cannot_submit_empty_sub_report`

**شرح نیازمندی:**  
طبق سناریوی ۳ از داستان کاربردی US-SR-04:
> «با فرض اینکه ساب‌ریپورت فاقد هرگونه ردیف فعالیت یا نیروی انسانی باشد، هنگامی که کاربر دکمه ارسال را بزند، آنگاه سامانه با خطای `cannot_submit_empty_sub_report` مانع تغییر وضعیت شود.»

**وضعیت در کد جاری:**  
در هر دو سرویس ارسال ساب‌ریپورت:
1. سرویس سنتی [`submit_sub_report`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/services/__init__.py#L26-L41):
   ```python
   def submit_sub_report(sub_report, user):
       if sub_report.status != SubReportStatus.DRAFT:
           raise ValidationError('فقط گزارش‌های پیش‌نویس قابل ارسال هستند')
       sub_report.status = SubReportStatus.SUBMITTED
       ...
       return sub_report
   ```
2. سرویس کانونیکال [`submit_unit_report`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/unit_report_services.py#L241-L275):
   تنها وضعیت گزارش (`locked.status not in EDITABLE_STATUSES`) و دسترسی کاربر بررسی می‌شود.

هیچ‌کدام از این دو تابع بررسی نمی‌کنند که آیا گزارش ردیف فعالیت، نیروی انسانی، مصالح یا یادداشتی دارد یا خیر.  
**اثبات قطعی از طریق تست خودکار سیستم:**  
در تست [`test_unit_report_workflow.py:80`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/tests/test_unit_report_workflow.py#L80-L90)، یک پیش‌نویس کاملاً خالی بلافاصله سابمیت می‌شود و با پاسخ HTTP 200 به وضعیت `SUBMITTED` درمی‌آید:
```python
def test_submit_moves_draft_to_submitted(self, auth_client, base, user):
    created = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
    rid = created.data['id']
    res = auth_client.post(f'{base}{rid}/submit/')
    assert res.status_code == status.HTTP_200_OK
    assert res.data['status'] == SubReportStatus.SUBMITTED
```
این امر باعث می‌شود گزارش‌های خالی وارد فرآیند تجمیع روزانه کارگاه شده و محاسبات و آمار کارگاه را تحریف کنند.

---

### G04 — P1 — انقطاع معماری روت‌ها و اندپوینت‌ها (لغو ثبت روت‌های `/sub-reports/`)

**شرح نیازمندی:**  
بر اساس بخش ۱ اسناد `sub_reports_ENDPOINTS.md` و `discipline-sub-reports-user-flow.md` و SPEC-05:
- مسیرهای اندپوینت: `/api/v1/projects/<project_id>/sub-reports/` و متدهای `.../submit/` و `.../approve/`
- مسیرهای صفحات فرانت‌اند: `/projects/:projectId/sub-reports` و `/projects/:projectId/sub-reports/new`

**وضعیت در کد جاری:**  
در فایل [`apps/api/core/sub_reports/urls.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/urls.py#L72-L77) یادداشت صریح زیر ثبت شده است:
```python
# NOTE (FR-032 / US5 / research D2):
# Legacy client endpoints under `/api/v1/projects/{project_id}/sub-reports/`
# (list, detail, submit, approve, reject) have been unregistered from client exposure.
```
همچنین تمام تست‌های مربوط به این اندپوینت‌ها در فایل [`test_sub_reports.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/tests/test_sub_reports.py#L35) اسکیپ شده‌اند:
```python
@pytest.mark.skip(reason="Legacy sub-reports endpoints unregistered per FR-032; superseded by canonical unit daily-reports endpoints")
```
در فرانت‌اند، در فایلهای [`apps/web/src/app/routes.ts`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes.ts) و [`business-setup.routes.ts`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/routes/business-setup.routes.ts)، هیچ روتی تحت عنوان `/projects/:projectId/sub-reports` تعریف نشده است. به جای آن، صفحات تحت دپارتمان‌های تجاری مانند `/businesses/:businessId/buildings` قرار گرفته‌اند که با ساختار درختی پروژه و سند SPEC-05 ناهمخوان است. کامپوننت [`SpecialtyContributionForm.tsx`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/sub_reports/SpecialtyContributionForm.tsx) نیز در هیچ کجای فرانت‌اند استفاده نشده و رها شده است.

---

### G05 — P2 — غیرفعال بودن سکشن مصالح برای واحد مکانیک و فقدان لیست پیشنهادات سریع مصالح

**شرح نیازمندی:**  
در داستان کاربری US-SR-03 (سناریو ۱):
> «هنگامی که ساب‌ریپورت جدید با انتخاب دیسیپلین MECHANICAL یا HVAC ایجاد کند، آنگاه فرم به صورت خودکار اقلام کاری و مصالح پرکاربرد مکانیکی (لوله ۵ لایه، لوله پلیکا، اتصالات جوشی، عایق) را در لیست انتخاب سریع پیشنهاد دهد.»

**وضعیت در کد جاری:**  
در فایل کلاینت فرانت‌اند [`apps/web/src/app/lib/api/unit-reports.ts`](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/lib/api/unit-reports.ts#L44-L70):
```typescript
export const MATERIALS_ENABLED_UNITS: readonly CanonicalUnit[] = [
  "warehouse",
] as const;

export function unitSupportsMaterialsSection(unit: CanonicalUnit | string): boolean {
  return (MATERIALS_ENABLED_UNITS as readonly string[]).includes(unit);
}
```
تنها واحدی که مجاز به ثبت مصالح است واحد `warehouse` (انبار) است! اگر سرپرست تأسیسات مکانیکی وارد صفحه واحد مکانیک شود، تب مصالح اصلاً برای او رندر نمی‌شود!  
علاوه بر این، در هیچ کجای سیستم (نه در بک‌اند و نه در فرانت‌اند) لیست پیشنهاد اقلام استاندارد مکانیکی نظیر لوله ۵ لایه یا پلیکا پیاده نشده است.

---

### G06 — P2 — فقدان مدل داده، فیلدها و اتصال تست‌های هیدرواستاتیک مکانیک به کنترل کیفیت (QC)

**شرح نیازمندی:**  
در داستان کاربری US-SR-03 (سناریو ۲):
> «با فرض اینکه لوله‌کشی بخشی از ساختمان انجام و تست فشار شده باشد، هنگامی که کاربر تیک «انجام تست هیدرواستاتیک موفق» را بزند و فشار تست (مثلاً ۶ بار) را وارد کند، آنگاه سیستم این تأیید فنی را به عنوان مستند کنترل کیفیت به گزارش پیوست کند.»

**وضعیت در کد جاری:**  
در ماژول سرویس [`qc_linkage.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/services/qc_linkage.py#L45-L75)، صرفاً پیوند نمونه‌گیری بتن به `risk.Inspection` پیاده شده است (`link_declared_concrete_sampling`).  
در تمام مدل‌های موجود در [`sub_reports/models.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/sub_reports/models.py):
- هیچ فیلدی برای تست هیدرواستاتیک (`is_hydrostatic_tested`) وجود ندارد.
- هیچ فیلدی برای مقدار فشار تست (`test_pressure_bar`) وجود ندارد.
- هیچ ارجاعی به `risk.Inspection` یا ماژول کنترل کیفی در فعالیت‌ها یا یادداشت‌های تأسیساتی برای تست فشار تعبیه نشده است.

---

### G07 — P2 — عدم محاسبه ساعت کارکرد اکیپ پیمانکار در سیستم کارکرد پیمانکاران

**شرح نیازمندی:**  
در داستان کاربری US-SR-01 (سناریو ۳):
> «با فرض اینکه فعالیت توسط یک پیمانکار دست‌دوم اجرا شده باشد، هنگامی که شناسه پیمانکار انتخاب شود، آنگاه ساعت کاری اکیپ به حساب کارکرد آن پیمانکار در سیستم منظور شود.»

**وضعیت در کد جاری:**  
در مدل `DisciplineSubReportActivity`، فیلد `contractor_ref` به عنوان کلید خارجی به مدل `projects.Stakeholder` ذخیره می‌شود. با این حال، در لایه بک‌اند هیچ‌گونه لاجیک، سیگنال یا تسک تجمیعی وجود ندارد که نفر-ساعت کارکرد (`foreman_count + worker_count * shift_hours`) را به سیستم مالی یا صورت‌وضعیت پیمانکاران در اپلیکیشن [`contracts`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/contracts) یا [`subcontractors`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/subcontractors) منتقل یا لینک کند. `contractor_ref` صرفاً به عنوان یک فیلد متنی/ارجاعی غیرفعال باقی می‌ماند.

---

### G08 — P2 — واگرایی ساختار دیسیپلین‌ها (Enum دیسیپلین‌ها در برابر کانونیکال یونیت‌ها)

**شرح نیازمندی:**  
بخش ۲ سند SPEC-05 دیسیپلین‌های استاندارد زیر را تعریف می‌کند:
```typescript
export enum Discipline {
  CIVIL = 'CIVIL',            // ابنیه و سازه
  ELECTRICAL = 'ELECTRICAL',  // تأسیسات برقی
  MECHANICAL = 'MECHANICAL',  // تأسیسات مکانیکی
  PLUMBING = 'PLUMBING',      // لوله‌کشی و آب و فاضلاب
  HVAC = 'HVAC',              // سرمایش، گرمایش و تهویه مطبوع
  FINISHING = 'FINISHING'     // معماری و نازک‌کاری
}
```
**وضعیت در کد جاری:**  
در فایل [`common/reporting_units.py`](file:///home/hossein/Desktop/projects/building-management/apps/api/core/common/reporting_units.py#L15-L36):
```python
class SpecialtyUnit(models.TextChoices):
    BUILDINGS = 'buildings', 'Buildings'
    ELECTRICAL = 'electrical', 'Electrical'
    MECHANICAL = 'mechanical', 'Mechanical'
    MACHINERY = 'machinery', 'Machinery'
    WAREHOUSE = 'warehouse', 'Warehouse'
    SECURITY = 'security', 'Security/HSE'
```
این دسته‌بندی باعث شده دیسیپلین‌های `plumbing` و `hvac` در واحد `mechanical` ادغام شوند و دیسیپلین `finishing` در `buildings` ذوب شود. در نتیجه اگر سرپرستی بخواهد گزارشی اختصاصی صرفاً برای لوله‌کشی (`PLUMBING`) یا نازک‌کاری (`FINISHING`) ثبت کند، سیستم اجازه تفکیک مستقیم را به او نمی‌دهد.

---

## ۳. ریشه‌یابی معماری و تناقضات سیستمی (Architectural Root Cause Analysis)

علت اصلی این شکاف‌ها ناشی از هم‌پوشانی ناقص دو فاز طراحی در پروژه است:
1. **طراحی سنتی گزارشات بر اساس فرم‌های شیراز (SPEC-05):**  
   این سند مستقیماً بر اساس اکسل‌های کارگاهی طراحی شده بود که دیسیپلین‌محور (`Discipline`)، دارای فیلد درصد پیشرفت روزانه، و دارای اندپوینت‌های مستقل `/api/v1/projects/:id/sub-reports/` بود.
2. **اصلاح معماری تک‌منبعی (Feature 032 & 033):**  
   در فازهای 032 و 033، تیم معماری تصمیم گرفت برای جلوگیری از ایجاد منابع چندگانه، روت‌های مستقل `/sub-reports/` را بازنشسته کرده و سیستم را بر مبنای «واحدهای تخصصی پروژه» (`SpecialtyUnit`) بازطراحی کند.  
   **مشکل اینجاست:** در زمان اجرای فازهای 032 و 033، الزامات اتمیک SPEC-05 (شامل درصد پیشرفت روزانه `daily_percent`، ولیدیشن بازه ۰ تا ۱۰۰، ممانعت از ارسال گزارش خالی، مصالح مصرفی مکانیک، و تست فشار) به ساختار جدید پورت (Port) نشدند و عملاً گم شدند!

---

## ۴. برنامه اقدام و ماتریس اولویت‌بندی رفع شکاف‌ها (Action Plan)

| کد شکاف | عنوان اقدام اصلاحی | اولویت | لایه آسیب‌دیده | فایل‌های هدف |
| :---: | :--- | :---: | :---: | :--- |
| **G01** | اضافه کردن ولیدیتور بازه ۰ تا ۱۰۰ روی `execution_percentage` و ایجاد کد خطای رسمی `percent_must_be_between_0_and_100` | **P1** | Backend Model & Serializer | `apps/api/core/sub_reports/models.py`, `serializers.py` |
| **G02** | بازگرداندن فیلد `execution_percentage` به `UnitReportActivitySectionSerializer` و فرم `section-activities.tsx` در فرانت‌اند | **P1** | API Contract & Frontend UI | `sub_reports/serializers.py`, `apps/web/src/components/department/section-activities.tsx` |
| **G03** | اضافه کردن اعتبارسنجی ممانعت از ارسال گزارش خالی با خطای `cannot_submit_empty_sub_report` در هر دو سرویس `submit_sub_report` و `submit_unit_report` | **P1** | Backend Service | `sub_reports/unit_report_services.py`, `sub_reports/services/__init__.py` |
| **G04** | اصلاح شفاف معماری قراردادها: تعیین تکلیف روت‌های اندپوینت ساب‌ریپورت و اتصال پایدار فرم‌های تخصصی به ساختار صفحات پروژه | **P1** | Routing & Controller | `apps/api/core/sub_reports/urls.py`, `apps/web/src/app/routes.ts` |
| **G05** | فعال‌سازی سکشن مصالح مصرفی برای دیسیپلین مکانیک و افزودن لیست اقلام پرکاربرد مکانیکی (پلیکا، لوله ۵ لایه) | **P2** | Frontend & API Contract | `apps/web/src/app/lib/api/unit-reports.ts`, `section-materials.tsx` |
| **G06** | ایجاد فیلدها و ساختار تست‌های هیدرواستاتیک و فشار در ساب‌ریپورت‌های تأسیسات و اتصال به `risk.Inspection` | **P2** | Backend Model & Service | `sub_reports/models.py`, `sub_reports/services/qc_linkage.py` |
| **G07** | پیوند نفر-ساعت فعالیت‌های دارای `contractor_ref` با کارکرد ثبت‌شده پیمانکار در سیستم | **P2** | Business Logic | `apps/api/core/field_reports/services/daily_report_aggregation.py` |
| **G08** | تعیین تکلیف رابطه ۶ دیسیپلین سنتی با ۶ واحد تخصصی کانونیکال (ذخیره تگ دیسیپلین در کنار واحد) | **P2** | Taxonomy & Schema | `apps/api/core/sub_reports/models.py`, `common/reporting_units.py` |
