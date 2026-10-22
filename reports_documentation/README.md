# مستندات جامع، یکپارچه و بهینه‌شده گزارشات و دپارتمان‌های پروژه Velora

این پوشه مرجع پالایش‌شده و بدون افزونگی (Deduplicated) از کلیه مشخصات فنی، نیازمندی‌ها، مدل‌های داده، قراردادهای API، فرم‌های اکسل کارگاهی و جریان‌های کاربری سیستم گزارش‌گیری پروژه Velora است.

کلیه مستندات تکراری، فایل‌های موقت آزمون، قراردادهای جزئی همپوشان و کدهای زائد شناسایی و حذف شده‌اند تا ساختاری کاملاً تمیز، متمرکز و یکپارچه در اختیار تیم فنی و مهندسی قرار گیرد.

---

## ساختار پوشه و دسته‌بندی اسناد

```
reports_documentation/
├── README.md                                          # همین راهنما و نقشه راه اسناد
│
├── atomic-specs/                                      # ★ مشخصات فنی و داستان‌های کاربری اتمیک (۱۱ سند و ۳۷ داستان)
│   ├── INDEX.md                                       # فهرست و ماتریس ردیابی کامل داستان‌های کاربری
│   ├── SPEC-01-DAILY-HEADER-WEATHER.md                # هدر گزارش روزانه، شیفت و شرایط جوی
│   ├── SPEC-02-DAILY-SECTIONS-GRID.md                 # ردیف‌ها و سکشن‌های فرزند گزارش روزانه (۷ سکشن)
│   ├── SPEC-03-DAILY-LIFECYCLE-LOCK.md                # چرخه حیات، قفل، بازنگری و اصلاح گزارش روزانه
│   ├── SPEC-04-DAILY-OFFLINE-SYNC.md                  # کارکرد آفلاین، همگام‌سازی دسته‌ای و رفع تعارض
│   ├── SPEC-05-DISCIPLINE-SUB-REPORTS.md              # ساب‌ریپورت‌های تخصصی واحدها (ابنیه، برق، مکانیک و...)
│   ├── SPEC-06-AUTO-DAILY-ROLLUP.md                   # موتور تجمیع خودکار ساب‌ریپورت‌ها در گزارش جامع روزانه
│   ├── SPEC-07-PHYSICAL-PROGRESS-MEASUREMENT.md       # روش‌های اندازه‌گیری و پیشرفت فیزیکی ۴ گانه
│   ├── SPEC-08-PERIODIC-REPORTS-ROLLUP.md             # تولید خودکار گزارشات دوره‌ای (هفتگی/ماهانه) و ردپای ارقام
│   ├── SPEC-09-DEPARTMENT-ACTIVITY-REPORTS.md         # رکوردهای فعالیت و گزارشات دپارتمان‌های ۵ گانه
│   ├── SPEC-10-WAREHOUSE-DEPARTMENT-REPORTS.md        # گزارشات و گردش مصالح دپارتمان انبار (فیلدهای ۸ گانه)
│   └── SPEC-11-SHIRAZ-EXCEL-PARITY-PDF.md             # انطباق با فرم‌های اکسل شیراز، خروجی PDF و فیلترها
│
├── 01-core-requirements-and-excel-blueprints/         # نیازمندی‌های بنیادی، چرخه‌ها و معماری فرم‌های شیراز
│   ├── مستندات فرم‌های اکسل شیراز... .md               # تحلیل فرم‌های واقعی کارگاه (گزارش کل، ابنیه، برق و دیتابیس)
│   ├── چرخه اطلاعات و عملیات کنترل پروژه... .md         # ۱۸ سرفصل گزارش روزانه، فرمول‌های پیشرفت و چرخه‌ها
│   ├── 07-گزارش روزانه کارگاه.md                      # سند استاندارد نیازمندی‌های گزارش روزانه (FR-DR)
│   └── 08-پیشرفت فیزیکی و گزارش‌های دوره‌ای.md          # سند استاندارد نیازمندی‌های گزارشات دوره‌ای (FR-PRG)
│
├── 02-auto-daily-summary-and-discipline-rollup/       # اسپک 028: تجمیع خودکار ساب‌ریپورت‌ها در گزارش روزانه
│   ├── spec.md                                        # نیازمندی‌ها، داستان‌های کاربر و منطق تجمیع خودکار
│   ├── data-model.md                                  # مدل داده و پیوند ساب‌ریپورت‌ها با گزارش روزانه
│   ├── daily-report-summary-api.md                    # قرارداد API اندپوینت /daily-reports/by-date/
│   └── daily-report-summary-ui.md                     # رفتار UI و تطابق سکشن‌ها با اکسل شیراز
│
├── 03-daily-field-reports-and-apis/                   # اسپک 007 و اندپوینت‌های API گزارشات کارگاه
│   ├── spec_007.md                                    # سند مشخصات گزارشات کارگاه و اعتبارسنجی‌ها
│   ├── data-model_007.md                              # مدل داده هدر، ردیف‌ها و درخواست‌های اصلاح
│   ├── field_reports_ENDPOINTS.md                     # مرجع کامل اندپوینت‌های گزارش روزانه، ردیف‌ها و پی‌لودها
│   └── sub_reports_ENDPOINTS.md                       # مرجع کامل اندپوینت‌های ساب‌ریپورت‌های تخصصی
│
├── 04-periodic-weekly-monthly-reports/                # اسپک 009 و اندپوینت‌های گزارشات پیشرفت
│   ├── spec_009.md                                    # مشخصات تولید خودکار گزارش هفتگی و ماهانه
│   ├── data-model_009.md                              # مدل داده گزارشات دوره‌ای و ثبت ردپای ارقام
│   └── schedule_and_progress_ENDPOINTS.md             # مرجع اندپوینت‌های پیشرفت فیزیکی و گزارش دوره‌ای
│
├── 05-department-and-warehouse-reports/               # اسپک 001: گزارشات دپارتمان‌ها و انبار کارگاه
│   ├── spec_001_warehouse.md                          # مشخصات گزارشات و گردش مصالح دپارتمان انبار
│   └── department-activity-records.md                 # قرارداد API و خروجی‌های روزانه/هفتگی دپارتمان‌ها
│
└── 07-decision-tree-and-user-flows/                   # درخت تصمیم و جریان‌های تعاملی یکپارچه
    ├── daily-reports-user-flow.md                     # جریان کاربری گزارش روزانه، تب‌ها و ماشین وضعیت
    ├── discipline-sub-reports-user-flow.md            # جریان کاربری ساب‌ریپورت‌های دیسیپلین و تجمیع آنی
    └── department-activities-user-flow.md             # ماتریس تعاملی ۵ دپارتمان (ابنیه، برق، مکانیک و...)
```

---

## ماتریس نگاشت موضوعی

| موضوع گزارش | اسناد نیازمندی و بیزنس | اسناد مدل داده و API | جریان تعاملی کاربر |
| :--- | :--- | :--- | :--- |
| **گزارش روزانه کارگاه (Daily Report)** | `01-.../07-گزارش روزانه کارگاه.md` | `03-.../field_reports_ENDPOINTS.md` و `data-model_007.md` | `07-.../daily-reports-user-flow.md` |
| **تجمیع خودکار ساب‌ریپورت‌ها (Auto Summary)** | `02-.../spec.md` و فرم شیراز | `02-.../daily-report-summary-api.md` و `data-model.md` | `07-.../daily-reports-user-flow.md` |
| **گزارش واحد ابنیه (Civil Sub-Report)** | فرم ۵ شیراز و چرخه‌های اطلاعاتی | `03-.../sub_reports_ENDPOINTS.md` (دیسیپلین `CIVIL`) | `07-.../discipline-sub-reports-user-flow.md` |
| **گزارش واحد برق (Electrical Sub-Report)** | فرم ۶ شیراز و چرخه‌های اطلاعاتی | `03-.../sub_reports_ENDPOINTS.md` (دیسیپلین `ELECTRICAL`) | `07-.../discipline-sub-reports-user-flow.md` |
| **گزارش واحد مکانیک و تأسیسات** | چرخه‌های اطلاعاتی و چرخه‌های پیشرفت | `03-.../sub_reports_ENDPOINTS.md` (دیسیپلین `MECHANICAL`) | `07-.../discipline-sub-reports-user-flow.md` |
| **گزارش هفتگی و ماهانه (Periodic Reports)** | `01-.../08-پیشرفت فیزیکی...md` و `04-.../spec_009.md` | `04-.../schedule_and_progress_ENDPOINTS.md` | تب پیشرفت و گزارشات دوره‌ای |
| **گزارش دپارتمان انبار و مصالح** | `05-.../spec_001_warehouse.md` | `05-.../department-activity-records.md` | `07-.../department-activities-user-flow.md` |
| **گزارش دپارتمان ماشین‌آلات** | چرخه‌های روزانه و جدول تجهیزات | `05-.../department-activity-records.md` | `07-.../department-activities-user-flow.md` |
