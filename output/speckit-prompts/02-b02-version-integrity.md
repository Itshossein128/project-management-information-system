# A.1 / B02 — اصلاح نسخه‌بندی، قفل مشتقات و حفظ داده

```text
/speckit-specify

این درخواست فقط نگارش specification برای همین زیرمرحله است. طبق قالب فعال SpecKit یک feature specification و checklist کیفیت مستقل تولید کن و سپس متوقف شو؛ plan، tasks، analyze، implement، تست محصول، استقرار و اجرای مرحله بعد مجاز نشده‌اند. خروجی حاضرِ Stage 2 صرفاً ورودی specify است.

ورودی workflow اصلی (عین متن):
Generate ordered speckit-specify prompts for Phase A.1 work packages B01 through B06 from /home/hossein/Desktop/projects/building-management/output/a1-requirements-2026-11-18

ریشه پروژه: /home/hossein/Desktop/projects/building-management
منبع مرحلهٔ ۱: /home/hossein/Desktop/projects/building-management/output/a1-requirements-2026-11-18
پیش از تفسیر، knowledge/agent-instructions.md و راهنمای پروژه را رعایت کن. منابع اصلی زیر را بخوان: README.md، remaining-work.md، scope-decisions.md، requirements-and-delivery.md، requirements.json، source-clauses.json/md، atomic-stories.json، atomic-coverage.md، broader-daily-sections.md، employer-summary.md و evidence/README.md در پوشه منبع. coverage.json همین بسته نگاشت مالکیت است؛ الزام تازه یا تأیید کارفرما نیست. برای هر گروه، بندهای منبع و معیارهای کامل داستان‌های مرتبط را هم بخوان؛ شناسه FR/SC به‌تنهایی یکتا نیست و باید با مسیر و خط همراه باشد.

قواعد نگارش:
- چه چیزی و چرا، نقش‌ها، ارزش کاربر، دامنه/غیردامنه، سناریوهای Given/When/Then و شکست/لبه، نیازمندی‌های قابل آزمون، معیارهای موفقیت قابل اندازه‌گیری، وابستگی و تصمیم‌های باز را در spec بنویس. فناوری/ساختار کد را راه‌حل اجباری نکن. نام API/مدل در شواهد فقط نشانی رفتار فعلی است.
- شناسه‌های H/D/W/E/Q/X و C و US و path:line بندها را به FR/SC و سناریوهای spec وصل کن؛ برای هر بند disposition صریحِ حفظ رفتار، رفع شکاف، تصمیم شرطی یا ارجاع فاز دیگر بده. نگاشت داستان به گروه به معنی اجرای تمام سناریوهای آن نیست؛ اختلاف‌ها را در سطح معیار بررسی کن.
- مبنای ممیزی f41fc378ebfe8a5d227b1e4b34dc85de5aaf3d8a در 2026-11-18 است؛ وضعیت کد امروز از این متن استنباط نشود. ۱۶۲ تست موجود و۲ کنترل موفق و۶ strict XFAIL تاریخی‌اند؛ XFAIL شاهد نقص است. نبود شاهد با نبود قابلیت یکی نیست. اگر نقص در کد روز رفع شده، الزام حفظ رفتار و اثبات باقیمانده را ثبت کن، بازنویسی نکن.
- تصمیم باز را به کارفرما نسبت نده؛ پیشنهاد، تصمیم مصوب و رفتار مشاهده‌شده جدا باشند. C01..C10 را با متن منبع حفظ کن؛ اثرگذاری تصمیم باید پیش از کار وابسته رفع شود. برای پنهان‌کردن ابهام مادی default نساز. حداکثر۳ سؤال بحرانی هر دور؛ باقی موارد در رجیستر باز باقی بمانند.
- هسته روزانه، موتور تجمیع، صفحات واحد، workflow و خروجی‌های موجود را بی‌دلیل از نو تعریف نکن. کل عملیات/آفلاین/منابع A.8، ارتباطات A.3.C، گزارش‌های دوره‌ای A.10 و استقرار/آموزش جامع A.12 در مالک خود باقی‌اند؛ اثر خراب‌کننده آن‌ها بر A.1 قابل چشم‌پوشی نیست. قرارداد دامنه B01 هر توسعه شرطی را به مالک مشخص می‌رساند.
- پیش از ایجاد feature، مسیر/شماره آزاد را با وضعیت واقعی specs انتخاب کن؛ مسیر اشغال‌شده را بازنویسی نکن. شناسه B بسته ثابت است و feature-number نیست. یک feature در هر فراخوانی؛ شماره از پیش تحمیل نشده است.
- خروجی specify: مسیر واقعی spec/checklist، traceability، نتیجه بررسی کیفیت، تصمیم‌های باز و آمادگی واقعی clarify/plan. تولید spec گواه پیاده‌سازی، release یا پذیرش نیست.

زیرمرحله جاری: B02 — اصلاح نسخه‌بندی، قفل مشتقات و حفظ داده
granularity کل A.1: multi؛ granularity این فراخوانی: single.
ترتیب اجباری استفاده: B01 → B02 → B03 → B04 → B05 → B06.
پیش‌نیاز معنایی: B01.
مرحله قبلی در ترتیب: B01.
در زمان نوشتن spec می‌توان وابستگی بسته‌نشده را صریح ثبت کرد، ولی هیچ کار وابسته یا آمادگی کاذب مجاز نیست. handoff قبلی باید قرارداد/نسخه/spec واقعی و شواهد بسته‌شدن مربوط را مشخص کند؛ حدس‌زدن مسیر یا قبولی پیش‌نیاز ممنوع.

مالک مستقیم گروه‌ها: H06, D01, D02, D03, W01, W02, W03, W04, W05, W06, E15
سهم مشترک با مالک دیگر: X01. سهم مشترک را با مالک قبلی هماهنگ کن؛ دوباره مالک اصلی تعریف نکن.

خواسته تفصیلی و معیارهای اجباری این زیرمرحله:
سناریوی اصلی: خلاصه approved حاصل از حداقل دو واحد و چند منبع → ایجاد اصلاحیه با دلیل → رد POST/PATCH/DELETE مستقیم مشتقات → اصلاح واحد منبع و بازسازی مجاز → تأیید نسخه جدید → کنترل جمع و lineage → در شاخه مستقل لغو اصلاحیه و بازگشت دقیق.
- هویت تجمیعی و readonly بودن بر مبنای مالکیت داده در تمام مسیرهای UI، child، batch، offline و legacy حفظ شود؛ metadata مجاز مدیریت با ردیف مشتق خلط نشود.
- مجموعه کامل DailyReportDerivedSource و همه فرزندان به شناسه ردیف‌های مقصد بازنگاشت شوند؛ کپی تک FK کافی نیست. نظر مدیریت، weather/site override مجاز و اطلاعات template/config/aggregation/fingerprint/snapshot مطابق قرارداد نسخه حفظ یا صریح بازتولید شوند.
- فقط نسخه approved جاری در دفتر رسمی جمع شود. مثال ممیزی: دو نسخه پنج‌واحدی باید جمع رسمی ۵ و headcount=۴ بدهند، نه ۱۰ و۸؛ تاریخچه از مسیر مستقل باقی بماند. B04 این سیاست را در فیلترها و جمع کل مصرف می‌کند.
- رقابت دو درخواست اصلاح، یکتایی روز/شیفت مطابق C03، template مؤثر در تاریخ و شش واحد معتبر، منابع روز/پروژه دیگر، draft/rejected/deleted/قدیمی، viewer، نقش غیرمجاز و تفکیک وظایف سناریو داشته باشند. تغییر منبع snapshot approved را پنهانی تغییر ندهد.
پایان قابل آزمون: سناریوهای نقص اصلاحیه/منابع/نظر/override و نسخه تاریخی با assertion صحیح و بدون XFAIL سبز شوند؛ منبع ۲تایی پس از clone همچنان ۲ منبع قابل ردیابی داشته باشد. گیت فنی از پذیرش کارفرما جدا ثبت شود.

متن بسته مرحلهٔ ۱، عیناً برای حفظ دامنه:
## B02 — اصلاح نسخه‌بندی، قفل مشتقات و حفظ داده

**مربوط به:** D01/W02/W03/W04/W05/E15. **پیش‌نیاز:** B01 برای قواعد نسخه و منبع؛ بازتولیدهای فعلی آماده‌اند.

1. نسخه اصلاحی هویت تجمیعی خود را حفظ کند. تمام APIهای child و batch/legacy، مستقل از فرض UI، مالکیت ردیف مشتق را اعمال کنند.
2. تمام فرزندان و مجموعه کامل DailyReportDerivedSource با شناسه‌های ردیف نسخه مقصد بازنگاشت شوند؛ فقط کپی فیلد تک‌منبع کافی نیست.
3. نظر مدیریت و overrideهای مجاز و اطلاعات لازم template/aggregation در اصلاح و لغو به درستی حفظ یا طبق قاعده صریح بازتولید شوند؛ هش/snapshot باید به نسخه مربوط بمانند.
4. دفتر عملیاتی فقط نسخه approved جاری را جمع کند؛ تاریخچه در مسیر مستقل قابل مشاهده بماند.

**آزمون تحویل:** approved summary از دو واحد و چند منبع → اصلاحیه → تلاش مستقیم POST/PATCH/DELETE مشتقات (رد) → اصلاح در واحد منبع و بازسازی مجاز → تأیید → کنترل منبع/نظر/override/جمع → لغو سناریوی دوم و بازگشت دقیق. دو درخواست اصلاح همزمان، نقش مشاهده‌گر و پروژه دیگر پوشش داده شوند. آزمون‌های مشاهده نقص بدون XFAIL سبز شوند؛ XFAIL یا xpass را رفع نقص جا نزنیم.

گروه‌های تحت مالکیت مستقیم — متن نیاز، باقیمانده و پذیرش مرحلهٔ ۱:

H06 — یکتایی گزارش جاری، تاریخ منطقی و پوسته گزارش بدون ثبت خام
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: by-date و نسخه جاری، تجمیع روزانه و منع POST گزارش خام وجود دارند.
باقیمانده: تعیین سازگاری مفهوم یک روز با شیفت هدر؛ کنترل رقابت و دسترسی مشاهده‌گر در پذیرش.
پذیرش: تکرار بازکردن تاریخ گزارش موازی نسازد و مشاهده‌گر نیازی به مجوز ویرایش نداشته باشد.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: apps/api/core/field_reports/daily_report_views.py:191؛ apps/api/core/field_reports/daily_report_views.py:197؛ specs/039-auto-daily-rollup/spec.md:179

D01 — گزارش پروژه فقط تجمیعی؛ ورود داده از صفحات واحدها
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: ناقص
موجود: تجمیع و ممنوعیت ایجاد خام وجود دارد؛ قفل ردیف مشتق به is_auto_summary وابسته است.
باقیمانده: رفع گریز اصلاحیه که این پرچم را از دست می‌دهد؛ پوشش تمام مسیرهای مستقیم/قدیمی/batch.
پذیرش: اصلاحیه هم گزارش تجمیعی بماند؛ هیچ ردیف مشتق با API یا UI قابل تألیف مستقیم نباشد.
حد شاهد: نقص اجرایی: اصلاحیه auto_summary=False و PATCH ردیف مشتق 200؛ correction-write-probe.json
ارجاع: apps/api/core/field_reports/daily_report_views.py:618؛ apps/api/core/field_reports/services/correction_service.py:138؛ specs/032-unit-report-source-truth/spec.md:179

D02 — شش واحد معتبر و پیکربندی مؤثر پروژه در تاریخ گزارش
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: buildings/electrical/mechanical/machinery/warehouse/security و قواعد template در تجمیع وجود دارد.
باقیمانده: اعتبارسنجی روی پروژه واقعی و دو نسخه template با تاریخ اثر متفاوت.
پذیرش: واحد الزامی از template همان تاریخ تعیین شود؛ پیش‌فرض ثابت سه‌رشته‌ای معیار نباشد.
حد شاهد: آزمون‌های منتخب completeness موفق؛ همه صفحات شش واحد در این نوبت مرور نشده
ارجاع: apps/api/core/field_reports/services/daily_report_aggregation.py:119؛ specs/032-unit-report-source-truth/spec.md:144

D03 — انتخاب منابع واجد شرایط: جاری، همان پروژه/روز، submitted یا approved
فاز مالک/اثر منبع: وابستگی A.1 / عملیات A.8
وضعیت تاریخی: پیاده‌سازی موجود
موجود: فیلتر منابع هم‌پروژه/هم‌روز/جاری و وضعیت SUBMITTED یا APPROVED در موتور هست.
باقیمانده: شفاف‌کردن اینکه approved بودن خلاصه به معنای approved بودن تک‌تک منابع نیست؛ سناریوی واقعی.
پذیرش: draft/rejected/deleted/قدیمی و روز یا پروژه دیگر هیچ contribution و اعتبار تکمیل ندهند.
حد شاهد: بازبینی مستقیم کد؛ پذیرش نهایی اجرا نشده
ارجاع: apps/api/core/field_reports/services/daily_report_aggregation.py:41؛ apps/api/core/field_reports/services/daily_report_aggregation.py:53؛ specs/032-unit-report-source-truth/spec.md:176

W01 — گردش draft، submit/review، approve/reject و قفل رسمی
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: مراحل، کنشگرها، زمان‌ها، کدهای خطای وضعیت/رد و قفل approved وجود دارند.
باقیمانده: UAT با تهیه‌کننده، ناظر و تأییدکننده واقعی؛ بررسی SoD و همه مسیرهای جایگزین.
پذیرش: حالت نامعتبر رد شود؛ دلیل رد حداقل ۱۰ کاراکتر؛ کاربر ممنوع نتواند تأیید کند.
حد شاهد: آزمون‌های منتخب workflow/status و validation موفق؛ ماتریس کامل نقش‌ها اجرا نشده
ارجاع: apps/api/core/field_reports/services/__init__.py:28؛ apps/api/core/field_reports/daily_report_views.py:332؛ specs/036-validation-codes-unset-semantics/spec.md:79

W02 — اصلاحیه، نسخه‌بندی، دلیل، لغو و بازگشت به نسخه قبلی
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: ساخت draft بعدی، دلیل، انتقال فرزندان، تاریخچه و لغو وجود دارند؛ قرارداد قبلی آزمون دارد.
باقیمانده: تکمیل انتقال هویت تجمیعی، مجموعه کامل provenance و متادیتای مالک خلاصه؛ بازآزمایی لغو/تأیید نسخه.
پذیرش: نسخه جدید هیچ داده/منبع معتبر را گم نکند؛ اصلاح همزمان تکراری نشود؛ لغو نسخه approved قبلی را بازگرداند.
حد شاهد: آزمون‌های قدیمی اصلاحیه موفق؛ سه نقص تازه در انتقال معنای خلاصه بازتولید شد
ارجاع: apps/api/core/field_reports/services/correction_service.py:138؛ specs/035-correction-lineage-cloning/spec.md:89

W03 — قفل داده مشتق پس از اصلاحیه و منع ویرایش مستقیم
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: قفل روی گزارش auto فعال است؛ نسخه اصلاحی ساخته‌شده این پرچم را حفظ نمی‌کند.
باقیمانده: حفظ هویت تجمیعی و قفل‌کردن بر اساس مالکیت داده در تمام child/batch paths؛ اصلاح فقط در واحد منبع.
پذیرش: POST/PATCH/DELETE ردیف مشتق نسخه اصلاحی هم رد شود؛ جزئیات مجاز مدیریت قابل ویرایش بماند.
حد شاهد: نقص اجرایی: PATCH موفق و ذخیره‌شده روی ردیف derived؛ correction-write-probe.json
ارجاع: apps/api/core/field_reports/services/correction_service.py:138؛ apps/api/core/field_reports/daily_report_views.py:618

W04 — منبع ردیف و مجموعه کامل منابع مقادیر تجمیعی
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: DailyReportDerivedSource و drill-down برای خلاصه اصلی موجودند؛ اصلاحیه این رکوردها را کپی/بازنگاشت نمی‌کند.
باقیمانده: بازنگاشت منبع به شناسه ردیف نسخه جدید و حفظ تمام منابع، نه فقط source FK تک‌ردیفی.
پذیرش: جمع دو منبع در هر نسخه هر دو منبع را نشان دهد؛ اصلاح/لغو هیچ منبعی را گم نکند.
حد شاهد: نقص اجرایی: ۲ رکورد provenance در مبدأ و ۰ در نسخه اصلاحی
ارجاع: apps/api/core/field_reports/services/correction_service.py:138؛ apps/api/core/field_reports/serializers.py:100؛ specs/032-unit-report-source-truth/spec.md:180

W05 — نظر مدیریت، override هوا/تعطیلی و اطلاعات مالک خلاصه در اصلاح
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: بازسازی معمول نظر/override را حفظ می‌کند؛ clone اصلاحیه management_opinion و weather_override را از دست می‌دهد.
باقیمانده: حفظ و تعیین سیاست تمام metadata مالک خلاصه، config/fingerprint/aggregation metadata؛ سازگاری با snapshot نسخه.
پذیرش: اصلاح/لغو/تأیید مجدد نظر و override مجاز را عیناً حفظ کند؛ مقادیر مشتق دوباره دستی نشوند.
حد شاهد: نقص اجرایی نظر و weather_override بازتولید؛ بقیه metadata در کد مشکوک و نیازمند تست دقیق
ارجاع: apps/api/core/field_reports/services/correction_service.py:138؛ apps/api/core/field_reports/services/daily_report_aggregation.py:559؛ specs/032-unit-report-source-truth/spec.md:184

W06 — نسخه رسمی ثابت و تشخیص تفاوت با منابع جاری
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: snapshot مصوب حفظ و در خروجی مقایسه/هشدار منبع نمایش داده می‌شود؛ زمان ثبت و تأیید جدا هستند.
باقیمانده: تطبیق نسخه دانلودشده با نسخه مصوب و اصلاح‌شده؛ قاعده وضعیت مبنای گزارش رسمی مستند شود.
پذیرش: تغییر منبع بدون اصلاح رسمی محتوای snapshot تأییدشده را پنهانی عوض نکند.
حد شاهد: آزمون‌های منتخب summary_snapshot_comparison موفق
ارجاع: apps/api/core/field_reports/services/daily_report_aggregation.py:593؛ apps/api/core/field_reports/shiraz_file4_excel.py:132؛ apps/api/core/field_reports/pdf.py:117

E15 — نسخه جاری در دفتر رسمی؛ تاریخچه جدا از جمع عملیاتی
فاز مالک/اثر منبع: پشتیبان A.1 / عملیات A.8
وضعیت تاریخی: ناقص
موجود: query وضعیت approved را اعمال می‌کند اما is_current را نه؛ نسخه قدیمی approved هم وارد می‌شود.
باقیمانده: فیلتر نسخه جاری برای دفتر عملیاتی و سیاست نمایش تاریخچه مستقل؛ کنترل پس از اصلاح/لغو.
پذیرش: دو نسخه ۵ واحدی یک فعالیت، جمع رسمی ۵ بدهند نه ۱۰؛ سابقه همچنان قابل دسترس بماند.
حد شاهد: نقص اجرایی: ۲ ردیف، quantity=10 و headcount=8 در برابر ۱ ردیف،۵ و۴
ارجاع: apps/api/core/field_reports/services/activity_log.py:9؛ specs/032-unit-report-source-truth/spec.md:163

ردیابی بندهای منبعِ تحت مالکیت این مرحله (متن کامل در coverage.json و source-clauses.json):
- W01 | specs/007-daily-report-gaps/spec.md:126 | FR-007
- W02 | specs/007-daily-report-gaps/spec.md:127 | FR-008
- W06 | specs/007-daily-report-gaps/spec.md:128 | FR-009
- W03 | specs/007-daily-report-gaps/spec.md:132 | FR-013
- W03 | specs/007-daily-report-gaps/spec.md:150 | SC-002
- D01 | specs/028-auto-daily-report-summary/spec.md:92 | FR-001
- D03 | specs/028-auto-daily-report-summary/spec.md:93 | FR-002
- D01 | specs/028-auto-daily-report-summary/spec.md:94 | FR-003
- H06 | specs/028-auto-daily-report-summary/spec.md:109 | FR-005
- D01 | specs/028-auto-daily-report-summary/spec.md:110 | FR-006
- W05 | specs/028-auto-daily-report-summary/spec.md:113 | FR-009
- H06 | specs/028-auto-daily-report-summary/spec.md:115 | FR-011
- D02 | specs/028-auto-daily-report-summary/spec.md:116 | FR-012
- D01 | specs/028-auto-daily-report-summary/spec.md:134 | SC-001
- D01 | specs/028-auto-daily-report-summary/spec.md:135 | SC-002
- D01 | specs/028-auto-daily-report-summary/spec.md:138 | SC-005
- H06 | specs/028-auto-daily-report-summary/spec.md:140 | SC-007
- H06 | specs/031-site-inactivity-security/spec.md:93 | FR-011
- H06 | specs/031-site-inactivity-security/spec.md:94 | FR-012
- H06 | specs/031-site-inactivity-security/spec.md:117 | SC-005
- D02 | specs/032-unit-report-source-truth/spec.md:144 | FR-001
- D02 | specs/032-unit-report-source-truth/spec.md:156 | FR-003
- D02 | specs/032-unit-report-source-truth/spec.md:158 | FR-005
- H06 | specs/032-unit-report-source-truth/spec.md:162 | FR-006
- H06 | specs/032-unit-report-source-truth/spec.md:163 | FR-007
- D01 | specs/032-unit-report-source-truth/spec.md:164 | FR-008
- H06 | specs/032-unit-report-source-truth/spec.md:165 | FR-009
- W01 | specs/032-unit-report-source-truth/spec.md:166 | FR-010
- W03 | specs/032-unit-report-source-truth/spec.md:167 | FR-011
- W01 | specs/032-unit-report-source-truth/spec.md:168 | FR-012
- W02 | specs/032-unit-report-source-truth/spec.md:169 | FR-013
- D01 | specs/032-unit-report-source-truth/spec.md:176 | FR-017
- D03 | specs/032-unit-report-source-truth/spec.md:177 | FR-018
- D03 | specs/032-unit-report-source-truth/spec.md:178 | FR-019
- D01 | specs/032-unit-report-source-truth/spec.md:179 | FR-020
- W04 | specs/032-unit-report-source-truth/spec.md:180 | FR-021
- W04 | specs/032-unit-report-source-truth/spec.md:181 | FR-022
- W04 | specs/032-unit-report-source-truth/spec.md:182 | FR-023
- W04 | specs/032-unit-report-source-truth/spec.md:183 | FR-024
- W05 | specs/032-unit-report-source-truth/spec.md:184 | FR-025
- D02 | specs/032-unit-report-source-truth/spec.md:185 | FR-026
- D02 | specs/032-unit-report-source-truth/spec.md:186 | FR-027
- D02 | specs/032-unit-report-source-truth/spec.md:187 | FR-028
- D01 | specs/032-unit-report-source-truth/spec.md:191 | FR-029
- D01 | specs/032-unit-report-source-truth/spec.md:192 | FR-030
- D01 | specs/032-unit-report-source-truth/spec.md:193 | FR-031
- D01 | specs/032-unit-report-source-truth/spec.md:194 | FR-032
- D01 | specs/032-unit-report-source-truth/spec.md:218 | SC-001
- D03 | specs/032-unit-report-source-truth/spec.md:220 | SC-003
- W04 | specs/032-unit-report-source-truth/spec.md:221 | SC-004
- W04 | specs/032-unit-report-source-truth/spec.md:222 | SC-005
- D02 | specs/032-unit-report-source-truth/spec.md:223 | SC-006
- D01 | specs/032-unit-report-source-truth/spec.md:224 | SC-007
- W04 | specs/033-daily-sections-grid/spec.md:200 | FR-012
- D03 | specs/033-daily-sections-grid/spec.md:243 | FR-037
- W04 | specs/033-daily-sections-grid/spec.md:244 | FR-038
- W04 | specs/033-daily-sections-grid/spec.md:245 | FR-039
- W05 | specs/033-daily-sections-grid/spec.md:248 | FR-042
- W03 | specs/033-daily-sections-grid/spec.md:249 | FR-043
- W04 | specs/033-daily-sections-grid/spec.md:250 | FR-044
- W04 | specs/033-daily-sections-grid/spec.md:270 | SC-002
- W04 | specs/033-daily-sections-grid/spec.md:273 | SC-005
- W03 | specs/033-daily-sections-grid/spec.md:277 | SC-009
- W02 | specs/034-daily-lifecycle-lock/spec.md:87 | FR-001
- W02 | specs/034-daily-lifecycle-lock/spec.md:88 | FR-002
- W02 | specs/034-daily-lifecycle-lock/spec.md:89 | FR-003
- W02 | specs/034-daily-lifecycle-lock/spec.md:90 | FR-004
- W02 | specs/034-daily-lifecycle-lock/spec.md:91 | FR-005
- W02 | specs/034-daily-lifecycle-lock/spec.md:92 | FR-006
- W02 | specs/034-daily-lifecycle-lock/spec.md:93 | FR-007
- W02 | specs/034-daily-lifecycle-lock/spec.md:94 | FR-008
- W01 | specs/034-daily-lifecycle-lock/spec.md:95 | FR-009
- W01 | specs/034-daily-lifecycle-lock/spec.md:96 | FR-010
- W02 | specs/034-daily-lifecycle-lock/spec.md:115 | SC-001
- W02 | specs/034-daily-lifecycle-lock/spec.md:116 | SC-002
- W01 | specs/034-daily-lifecycle-lock/spec.md:117 | SC-003
- W02 | specs/034-daily-lifecycle-lock/spec.md:119 | SC-005
- W02 | specs/035-correction-lineage-cloning/spec.md:89 | FR-001
- W02 | specs/035-correction-lineage-cloning/spec.md:90 | FR-002
- W02 | specs/035-correction-lineage-cloning/spec.md:96 | FR-003
- W02 | specs/035-correction-lineage-cloning/spec.md:97 | FR-004
- W02 | specs/035-correction-lineage-cloning/spec.md:98 | FR-005
- W02 | specs/035-correction-lineage-cloning/spec.md:99 | FR-006
- W02 | specs/035-correction-lineage-cloning/spec.md:100 | FR-007
- W02 | specs/035-correction-lineage-cloning/spec.md:101 | FR-008
- W02 | specs/035-correction-lineage-cloning/spec.md:102 | FR-009
- W02 | specs/035-correction-lineage-cloning/spec.md:103 | FR-010
- W02 | specs/035-correction-lineage-cloning/spec.md:104 | FR-011
- W02 | specs/035-correction-lineage-cloning/spec.md:118 | SC-001
- W02 | specs/035-correction-lineage-cloning/spec.md:119 | SC-002
- W02 | specs/035-correction-lineage-cloning/spec.md:120 | SC-003
- W02 | specs/035-correction-lineage-cloning/spec.md:121 | SC-004
- W01 | specs/036-validation-codes-unset-semantics/spec.md:79 | FR-001
- W01 | specs/036-validation-codes-unset-semantics/spec.md:80 | FR-002
- W01 | specs/036-validation-codes-unset-semantics/spec.md:81 | FR-003
- W01 | specs/036-validation-codes-unset-semantics/spec.md:82 | FR-004
- W01 | specs/036-validation-codes-unset-semantics/spec.md:83 | FR-005
- W01 | specs/036-validation-codes-unset-semantics/spec.md:108 | SC-001
- W03 | specs/037-daily-offline-sync/spec.md:117 | FR-014
- W04 | specs/037-daily-offline-sync/spec.md:118 | FR-015
- W05 | specs/037-daily-offline-sync/spec.md:119 | FR-016
- D02 | specs/038-discipline-sub-reports/spec.md:180 | FR-016
- D01 | specs/038-discipline-sub-reports/spec.md:184 | FR-018
- W03 | specs/038-discipline-sub-reports/spec.md:186 | FR-020
- D01 | specs/038-discipline-sub-reports/spec.md:224 | SC-007
- H06 | specs/039-auto-daily-rollup/spec.md:179 | FR-001
- H06 | specs/039-auto-daily-rollup/spec.md:180 | FR-002
- D01 | specs/039-auto-daily-rollup/spec.md:182 | FR-004
- W03 | specs/039-auto-daily-rollup/spec.md:185 | FR-007
- W03 | specs/039-auto-daily-rollup/spec.md:186 | FR-008
- W05 | specs/039-auto-daily-rollup/spec.md:191 | FR-013
- D02 | specs/039-auto-daily-rollup/spec.md:192 | FR-014
- D02 | specs/039-auto-daily-rollup/spec.md:193 | FR-015
- D02 | specs/039-auto-daily-rollup/spec.md:194 | FR-016
- H06 | specs/039-auto-daily-rollup/spec.md:211 | SC-001
- H06 | specs/039-auto-daily-rollup/spec.md:212 | SC-002
- W03 | specs/039-auto-daily-rollup/spec.md:214 | SC-004
- D02 | specs/039-auto-daily-rollup/spec.md:217 | SC-007
- W05 | specs/039-auto-daily-rollup/spec.md:218 | SC-008
- W01 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:60 | FR-DR-007
- W02 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:61 | FR-DR-008
- W06 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:62 | FR-DR-009

داستان‌های اتمیک مرتبط (همه معیارهای متن کامل بررسی شوند؛ بخش خارج دامنه ارجاع شود):
- US-DR-03 | reports_documentation/atomic-specs/SPEC-01-DAILY-HEADER-WEATHER.md:67 | سهم این مرحله: H06؛ کل گروه‌ها: H06
- US-DR-11 | reports_documentation/atomic-specs/SPEC-03-DAILY-LIFECYCLE-LOCK.md:26 | سهم این مرحله: W01؛ کل گروه‌ها: W01
- US-DR-12 | reports_documentation/atomic-specs/SPEC-03-DAILY-LIFECYCLE-LOCK.md:53 | سهم این مرحله: W03؛ کل گروه‌ها: W03
- US-DR-13 | reports_documentation/atomic-specs/SPEC-03-DAILY-LIFECYCLE-LOCK.md:74 | سهم این مرحله: W02, W04, W05؛ کل گروه‌ها: W02, W04, W05
- US-SR-01 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:30 | سهم این مرحله: D01؛ کل گروه‌ها: X02, E10, D01
- US-SR-02 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:53 | سهم این مرحله: D01؛ کل گروه‌ها: X02, E10, D01
- US-SR-03 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:70 | سهم این مرحله: D01؛ کل گروه‌ها: X02, E10, D01
- US-SR-04 | reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:87 | سهم این مرحله: D01؛ کل گروه‌ها: X02, E10, D01
- US-AG-01 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:34 | سهم این مرحله: D01, H06؛ کل گروه‌ها: D01, H06
- US-AG-02 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:55 | سهم این مرحله: D03, W04؛ کل گروه‌ها: D03, D04, D06, D11, W04
- US-AG-03 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:78 | سهم این مرحله: W03؛ کل گروه‌ها: W03
- US-AG-04 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:95 | سهم این مرحله: W05؛ کل گروه‌ها: H02, W05
- US-AG-05 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:112 | سهم این مرحله: D02؛ کل گروه‌ها: D02
- US-AG-06 | reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:129 | سهم این مرحله: E15؛ کل گروه‌ها: E11, E13, E14, E15

پس از نگارش و بررسی specification همین زیرمرحله متوقف شو. این پرامپت مجوز عبور خودکار به فاز بعد نیست.
```
