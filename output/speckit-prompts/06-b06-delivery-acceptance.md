# A.1 / B06 — بسته تحویل قابل آزمون و پذیرش اولیه کارفرما

```text
/speckit-specify

این درخواست فقط نگارش specification برای همین زیرمرحله است. طبق قالب فعال SpecKit یک feature specification و checklist کیفیت مستقل تولید کن و سپس متوقف شو؛ plan، tasks، analyze، implement، تست محصول، استقرار و اجرای مرحله بعد مجاز نشده‌اند. خروجی حاضرِ Stage 2 صرفاً ورودی specify است.

ورودی workflow اصلی (عین متن):
Go for the next step to deliver the application, based on A.1 phase in http://localhost:5173/delivery-plan

ریشه پروژه: /home/hossein/Desktop/projects/building-management
منبع مرحلهٔ ۱: /home/hossein/Desktop/projects/building-management/output/a1-requirements-2026-11-18
پیش از تفسیر، knowledge/agent-instructions.md و راهنمای پروژه را رعایت کن. منابع اصلی زیر را بخوان: README.md، remaining-work.md، scope-decisions.md، requirements-and-delivery.md، requirements.json، source-clauses.json/md، atomic-stories.json، atomic-coverage.md، broader-daily-sections.md، employer-summary.md و evidence/README.md در پوشه منبع. coverage.json همین بسته نگاشت مالکیت است؛ الزام تازه یا تأیید کارفرما نیست. برای هر گروه، بندهای منبع و معیارهای کامل داستان‌های مرتبط را هم بخوان؛ شناسه FR/SC به‌تنهایی یکتا نیست و باید با مسیر و خط همراه باشد.

قواعد نگارش:
- چه چیزی و چرا، نقش‌ها، ارزش کاربر، دامنه/غیردامنه، سناریوهای Given/When/Then و شکست/لبه، نیازمندی‌های قابل آزمون، معیارهای موفقیت قابل اندازه‌گیری، وابستگی و تصمیم‌های باز را در spec بنویس. فناوری/ساختار کد را راه‌حل اجباری نکن. نام API/مدل در شواهد فقط نشانی رفتار فعلی است.
- شناسه‌های H/D/W/E/Q/X و C و US و path:line بندها را به FR/SC و سناریوهای spec وصل کن؛ برای هر بند disposition صریحِ حفظ رفتار، رفع شکاف، تصمیم شرطی یا ارجاع فاز دیگر بده. نگاشت داستان به گروه به معنی اجرای تمام سناریوهای آن نیست؛ اختلاف‌ها را در سطح معیار بررسی کن.
- مبنای ممیزی f41fc378ebfe8a5d227b1e4b34dc85de5aaf3d8a در 2026-11-18 است؛ وضعیت کد امروز از این متن استنباط نشود. ۱۶۲ تست موجود و۲ کنترل موفق و۶ strict XFAIL تاریخی‌اند؛ XFAIL شاهد نقص است. نبود شاهد با نبود قابلیت یکی نیست. اگر نقص در کد روز رفع شده، الزام حفظ رفتار و اثبات باقیمانده را ثبت کن، بازنویسی نکن. وضعیت‌ها و تصمیم‌های نقل‌شده از ممیزی پایه تاریخی‌اند؛ برای رفتار جاری، قرارداد نسخه‌دار و شواهد تاریخ‌دار پایین را بررسی کن.
- تصمیم باز را به کارفرما نسبت نده؛ پیشنهاد، تصمیم مصوب و رفتار مشاهده‌شده جدا باشند. C01..C10 را با متن منبع حفظ کن؛ اثرگذاری تصمیم باید پیش از کار وابسته رفع شود. برای پنهان‌کردن ابهام مادی default نساز. حداکثر۳ سؤال بحرانی هر دور؛ باقی موارد در رجیستر باز باقی بمانند.
- هسته روزانه، موتور تجمیع، صفحات واحد، workflow و خروجی‌های موجود را بی‌دلیل از نو تعریف نکن. کل عملیات/آفلاین/منابع A.8، ارتباطات A.3.C، گزارش‌های دوره‌ای A.10 و استقرار/آموزش جامع A.12 در مالک خود باقی‌اند؛ اثر خراب‌کننده آن‌ها بر A.1 قابل چشم‌پوشی نیست. قرارداد دامنه B01 هر توسعه شرطی را به مالک مشخص می‌رساند.
- پیش از ایجاد feature، مسیر/شماره آزاد را با وضعیت واقعی specs انتخاب کن؛ مسیر اشغال‌شده را بازنویسی نکن. شناسه B بسته ثابت است و feature-number نیست. یک feature در هر فراخوانی؛ شماره از پیش تحمیل نشده است.
- خروجی specify: مسیر واقعی spec/checklist، traceability، نتیجه بررسی کیفیت، تصمیم‌های باز و آمادگی واقعی clarify/plan. تولید spec گواه پیاده‌سازی، release یا پذیرش نیست.

زیرمرحله جاری: B06 — بسته تحویل قابل آزمون و پذیرش اولیه کارفرما
granularity کل A.1: multi؛ granularity این فراخوانی: single.
ترتیب اجباری استفاده: B01 → B02 → B03 → B04 → B05 → B06.
پیش‌نیاز معنایی: B01, B02, B03, B04, B05.
مرحله قبلی در ترتیب: B05.
در زمان نوشتن spec می‌توان وابستگی بسته‌نشده را صریح ثبت کرد، ولی هیچ کار وابسته یا آمادگی کاذب مجاز نیست. handoff قبلی باید قرارداد/نسخه/spec واقعی و شواهد بسته‌شدن مربوط را مشخص کند؛ حدس‌زدن مسیر یا قبولی پیش‌نیاز ممنوع.

مالک مستقیم گروه‌ها: E09, Q03, Q04, Q05
سهم مشترک با مالک دیگر: ندارد. سهم مشترک را با مالک قبلی هماهنگ کن؛ دوباره مالک اصلی تعریف نکن.

خواسته تفصیلی و معیارهای اجباری این زیرمرحله:
سناریوی اصلی: تهیه‌کننده، ناظر و کارفرما از مسیر قابل دسترسی همان release/SHA آزموده‌شده، فایل روز مرجع را دانلود می‌کنند، سناریوهای پذیرش را اجرا کرده و نتیجه اولیه را صریح ثبت می‌کنند.
- بسته شامل شناسه release/SHA و محیط/URL، تاریخ شواهد، ورودی و expected مستقل، فایل‌های نهایی با checksum، راهنمای نقش‌ها و مسیرهای واقعی، نقشه تصمیم کاربر، سناریو و نتیجه باشد. لینک شکسته صفر؛ راهنما دامنه واقعی fingerprint و وضعیت مستقل منابع را توضیح دهد.
- API و مرورگر روی همان نسخه: دسکتاپ/موبایل × فارسی/انگلیسی، تهیه‌کننده/ناظر/تأییدکننده/viewer مجاز، نقش غیرمجاز و پروژه دیگر؛ از ثبت واحد تا تجمیع، اصلاح، لغو، تاریخچه و دانلود. ID مستقیم، مسیر جایگزین، دانلود و پیوست تابع دسترسی منبع/پروژه باشند؛ SoD با قرارداد A.6 بازآزمایی شود.
- B05 را برای فایل واقعاً دانلودشده از نسخه هدف معتبر کن؛ SHA و checksum نامنطبق یا تغییر مؤثر پس از آزمون مستلزم بررسی دوباره است. صرف CI یا سرویس فعال یا آزمون محلی، استقرار production را ثابت نمی‌کند.
- B01..B05 باید handoff بسته داشته باشند؛ همه۶۱ گروه،۳۷۰ بند و۴۲ داستان را طبق disposition و مرز قرارداد مرور کن، نه اینکه خارج‌دامنه‌ها را پیاده‌شده یا پذیرفته‌شده حساب کنی. پرونده انتقال به A.3.C/A.4/A.7/A.8/A.9/A.10/A.12 حفظ شود.
- سه وضعیت مستقل گزارش شوند: آمادگی فنی، نسخه قابل دسترسی آزموده‌شده، و پذیرش اولیه کارفرما. هیچ عامل یا تستی به‌جای کارفرما امضا نکند. نبود کارفرما/محیط واقعی/داده لازم نتیجه pending با مسئول و شاهد لازم دارد.
پایان A.1 تنها با بسته‌شدن نقص اجرایی مؤثر، گواه مستقل عدد/فرمول/چاپ، تصمیم‌های دامنه مؤثر، صفر خطای باز رسمی و صورت‌جلسه پذیرش اولیه صریح کارفرما قابل اعلام است.

Current Stage 1 package evidence (2026-11-22)
- QA verdict for B06: qa_failed. Specify after B05 in the sequence. Release acceptance requires the B05 evidence and same-candidate clearance of B01–B05.
- Reports: output/a1-requirements-2026-11-22-stage1-b06-qa-findings.md and output/a1-requirements-2026-11-22-stage1-b06-qa-findings.json.
- The historical blocks below retain the baseline, prior verdicts, and original defect meanings. Use the dated package reports for their tested scopes and the published contract for decisions and deliverable IDs. Stage 2 did not run product QA.
- Specify a frozen release manifest and sample hashes, independent B05 evidence, role/access guide, and a walkthrough with explicit employer disposition, identity, date and release. B01–B04 reported passes supersede the blanket upstream QA claim within their tested scopes. B05 remains open. Require candidate-bound clearance for B01–B05. Record authorized access-control verification by role, project and download surface, desktop and 390×844 mobile in FA RTL and EN LTR across 18 sections, and reconcile the decision tree with deployed permissions. Keep acceptance pending until the employer records it.
- DEF-B06-01 — Missing frozen Phase A.1 release package with commit SHA, independent inputs/expected fixtures, final sample exports, and verified SHA-256 checksums
- DEF-B06-02 — Hard dependency block: upstream delivery packages B01 through B05 have open blocker defects
- DEF-B06-03 — Missing explicit employer review and sign-off protocol
- DEF-B06-04 — Unverified live cross-project isolation matrix and negative security tests for direct ID download endpoints
- DEF-B06-05 — Incomplete mobile responsive and bilingual (FA/EN) verification evidence across all 18 daily report sections
- DEF-B06-06 — Decision tree in docs/decision-tree/ lacks final verification against deployed authorization gates and export routes

ردیابی QA مرحله ۱.۲ (2026-11-19)
اقلام رسمی تحویل: A.1.04
معیار بسته در کشف مرحله ۱: یک release/SHA و فایل‌های checksum‌دار با راهنمای نقش و سناریو ارائه شود؛ آزمون API و مرورگر در دسکتاپ/موبایل و FA/EN انجام و سه وضعیت فنی، نسخه قابل دسترسی آزموده‌شده و پذیرش صریح کارفرما جدا ثبت شوند.
منابع گزارش: output/a1-requirements-2026-11-19-stage1-b06-qa-findings.md و output/a1-requirements-2026-11-19-stage1-b06-qa-findings.json. خلاصه قابل حمل در coverage.json ثبت شده است.
برای هر شناسه زیر معیار سنجش یا تصمیم دامنه ثبت کن. qa_failed وضعیت گزارش قبلی است. یافته احتمالی، نبود شاهد، بازتولید تاریخی و تصمیم باز را با هم یکی نگیر.
- DEF-B06-01 — آرشیو منجمد با release/SHA، ورودی، expected، فایل‌ها، راهنمای نقش و SHA-256 تحویل شود.
- DEF-B06-02 — بسته‌شدن B01..B05 و تعیین تکلیف شواهد نقص‌های باز قبل از اعلام آمادگی ثبت شود.
- DEF-B06-03 — نتیجه صریح کارفرما روی همان نسخه، همراه با تاریخ، نقش، اختلاف و وضعیت pending/accepted/rejected ثبت شود.
- DEF-B06-04 — برای E09 معیار دفاعی رد دسترسی و دانلود میان پروژه‌ها را با نقش‌ها و داده آزمون مجاز روی نسخه هدف مشخص کن.
- DEF-B06-05 — گردش واقعی نقش‌ها روی دسکتاپ/موبایل و FA/EN را با وضعیت و شواهد هر یک از ۱۸ بخش مرتبط ثبت کن.

Historical Stage 1 evidence (2026-11-21, retained for regression traceability)
- QA verdict for B06: qa_failed. Acceptance criterion: Fixed release/SHA, guide, inputs/expected values, checksums, role/device/language/cross-project tests, and explicit employer review are recorded.
- Source reports: output/a1-requirements-2026-11-21-stage1-b06-qa-findings.md and output/a1-requirements-2026-11-21-stage1-b06-qa-findings.json.
- Use the 2026-11-19 entries and baseline audit below as traceability and regression evidence. Use the newer package-specific report for its stated technical scope. Reconcile any disagreement by scope and tested build before relying on it. Existing specs are the first place to carry forward verified behavior and identify residual gaps.
- Require a frozen release/SHA with inputs, expected values, outputs, checksums and role guide. Require authenticated desktop and 390×844 mobile evidence in Persian RTL and English LTR across all 18 sections, including scoped permission-denial checks on the candidate and verification against docs/decision-tree/. Require named employer disposition (accepted, rejected or conditional), date and feedback. Record technical QA separately. B01–B03 have reported technical passes, with same-release verification still due. B04/B05 remain failed. Require evidence before checking off A.1.01–A.1.04 at http://localhost:5173/delivery-plan. The Stage 1 live visit redirected to login, so authenticated status remains unverified.
- DEF-B06-01 — Missing frozen Phase A.1 release package with commit SHA, independent inputs/expected fixtures, final sample exports, and verified SHA-256 checksums
- DEF-B06-02 — Hard dependency block: upstream delivery packages B01 through B05 have open blocker defects
- DEF-B06-03 — Missing explicit employer review and sign-off protocol
- DEF-B06-04 — Unverified live cross-project isolation matrix and negative security tests for direct ID download endpoints
- DEF-B06-05 — Incomplete mobile responsive and bilingual (FA/EN) verification evidence across all 18 daily report sections
- DEF-B06-06 — Decision tree in docs/decision-tree/ lacks final verification against deployed authorization gates and export routes

متن بسته مرحلهٔ ۱، عیناً برای حفظ دامنه:
## B06 — بسته تحویل قابل آزمون و پذیرش اولیه کارفرما

**مربوط به:** E09/Q03/Q04/Q05. **پیش‌نیاز:** B01 تا B05 بسته شده باشند.

یک release/SHA مشخص، مسیر دسترسی، ورودی/expected، راهنمای نقش‌ها، فایل‌های نمونه با checksum و سناریوهای پذیرش ارائه شود. API و مرورگر روی همان نسخه، دسکتاپ/موبایل و فارسی/انگلیسی، نقش مجاز/غیرمجاز و پروژه دیگر آزموده شوند. تهیه‌کننده/ناظر/کارفرما همان نسخه را دانلود کنند و تفاوت منبع submitted با approved و حدود fingerprint توضیح داده شود.

**معیار پایان A.1:** نقص‌های اجرایی اثرگذار بسته؛ گواه مستقل عدد/فرمول/چاپ موجود؛ همه تصمیم‌های دامنه اثرگذار ثبت‌شده؛ هیچ خطای باز تأثیرگذار بر گزارش رسمی؛ نتیجه مرور کارفرما و پذیرش اولیه صریح ثبت شود. قبولی اتوماتیک تست‌ها به جای صورت‌جلسه کارفرما نیست.

گروه‌های تحت مالکیت مستقیم — متن نیاز، باقیمانده و پذیرش مرحلهٔ ۱:

E09 — مجوز مشاهده و دانلود و جلوگیری از نشت بین پروژه‌ها
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: endpointهای خروجی و عضویت/مجوز view_reports وجود دارند و تست منتخب دارند.
باقیمانده: ماتریس کامل نقش مجاز/غیرمجاز/کاربر پروژه دیگر در API و مرورگر روی همان نسخه تحویل.
پذیرش: کاربر غیرمجاز نتواند با ID مستقیم گزارش یا فایل را بگیرد؛ viewer مجاز بتواند دانلود کند.
حد شاهد: بخشی از آزمون مجوز در بسته‌های موفق؛ پوشش منفی کامل و استقرار زنده اثبات نشده
ارجاع: apps/api/core/field_reports/daily_report_views.py:423؛ apps/api/core/field_reports/daily_report_views.py:435؛ specs/044-shiraz-excel-parity-pdf/spec.md:188

Q03 — پذیرش مرورگری دسکتاپ/موبایل و فارسی/انگلیسی
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: UI و سناریوهای E2E/گزارش‌های قبلی وجود دارند.
باقیمانده: اجرای تازه از ثبت واحد تا تجمیع، اصلاح، مشاهده نسخه و دانلود با نقش‌های واقعی و اندازه موبایل.
پذیرش: مسیرهای لازم بدون خطای UI، داده گمشده و دورزدن مجوز در هر دو زبان کامل شوند.
حد شاهد: گزارش‌های قدیمی صرفاً تاریخی؛ در این ممیزی اجرای تازه مرورگر انجام نشده
ارجاع: specs/007-daily-report-gaps/spec.md:130؛ specs/033-daily-sections-grid/verification-report.md:1

Q04 — راهنمای مسیرها و درخت تصمیم مطابق رفتار واقعی
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: پیاده‌سازی موجود
موجود: سندهای مسیر کاربر و تصمیم‌گیری برای دانلودها وجود دارند.
باقیمانده: تطبیق همه لینک‌ها و gateهای نقش با نسخه نهایی و حذف ادعای امضای گواهی‌دار اثبات‌نشده.
پذیرش: هر اقدام خروجی از مسیر واقعی و مجوز درست به فایل صحیح برسد؛ لینک شکسته صفر.
حد شاهد: وجود docs بررسی شده؛ ممیزی کامل همه لینک‌ها این نوبت انجام نشده
ارجاع: specs/044-shiraz-excel-parity-pdf/spec.md:201؛ docs/decision-tree/README.md:1

Q05 — بسته تحویل همان نسخه، راهنمای آزمون و صورت‌جلسه پذیرش
فاز مالک/اثر منبع: A.1
وضعیت تاریخی: ناقص
موجود: زیرساخت برنامه و اسناد تحویل وجود دارد؛ کد و تست هم بخش عمده موجودند.
باقیمانده: ثبت SHA انتشار، فایل‌ها و checksum، ورودی/expected، لاگ بازحساب و صفحات PDF و اجرای آزمون کارفرما.
پذیرش: کارفرما دقیقاً فایل و نسخه آزموده‌شده را دانلود و نتیجه پذیرش اولیه را صریح ثبت کند.
حد شاهد: استقرار، فایل دانلودی تولید و صورت‌جلسه کارفرما در این ممیزی احراز/ایجاد نشده
ارجاع: output/delivery-plan-2026-11-03/delivery-plan.md:113؛ docs/delivery/R0-scope-and-reports-contract.md:22

ردیابی بندهای منبعِ تحت مالکیت این مرحله (متن کامل در coverage.json و source-clauses.json):
- Q03 | specs/007-daily-report-gaps/spec.md:130 | FR-011
- Q03 | specs/007-daily-report-gaps/spec.md:149 | SC-001
- E09 | specs/028-auto-daily-report-summary/spec.md:114 | FR-010
- Q03 | specs/030-daily-header-weather/spec.md:143 | SC-007
- Q03 | specs/031-site-inactivity-security/spec.md:119 | SC-007
- Q03 | specs/032-unit-report-source-truth/spec.md:155 | FR-002
- E09 | specs/032-unit-report-source-truth/spec.md:170 | FR-014
- E09 | specs/032-unit-report-source-truth/spec.md:171 | FR-015
- E09 | specs/032-unit-report-source-truth/spec.md:172 | FR-016
- E09 | specs/032-unit-report-source-truth/spec.md:219 | SC-002
- Q03 | specs/032-unit-report-source-truth/spec.md:227 | SC-010
- Q03 | specs/033-daily-sections-grid/spec.md:269 | SC-001
- E09 | specs/033-daily-sections-grid/spec.md:271 | SC-003
- Q03 | specs/033-daily-sections-grid/spec.md:278 | SC-010
- Q03 | specs/034-daily-lifecycle-lock/spec.md:100 | FR-014
- E09 | specs/035-correction-lineage-cloning/spec.md:105 | FR-012
- E09 | specs/035-correction-lineage-cloning/spec.md:122 | SC-005
- Q03 | specs/036-validation-codes-unset-semantics/spec.md:91 | FR-013
- Q03 | specs/036-validation-codes-unset-semantics/spec.md:92 | FR-014
- Q03 | specs/036-validation-codes-unset-semantics/spec.md:93 | FR-015
- E09 | specs/036-validation-codes-unset-semantics/spec.md:94 | FR-016
- Q03 | specs/036-validation-codes-unset-semantics/spec.md:111 | SC-004
- Q03 | specs/036-validation-codes-unset-semantics/spec.md:112 | SC-005
- Q03 | specs/038-discipline-sub-reports/spec.md:185 | FR-019
- Q03 | specs/038-discipline-sub-reports/spec.md:225 | SC-008
- E09 | specs/044-shiraz-excel-parity-pdf/spec.md:188 | FR-010
- Q04 | specs/044-shiraz-excel-parity-pdf/spec.md:201 | FR-020
- Q04 | specs/044-shiraz-excel-parity-pdf/spec.md:224 | SC-006
- Q03 | reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:64 | FR-DR-011

داستان‌های اتمیک مرتبط (همه معیارهای متن کامل بررسی شوند؛ بخش خارج دامنه ارجاع شود):

پس از نگارش و بررسی specification همین زیرمرحله متوقف شو. این پرامپت مجوز عبور خودکار به فاز بعد نیست.
```
