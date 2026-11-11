# پرامپت‌های اجرای A.7 با SpecKit

این بسته شش پرامپت مستقل و متوالی دارد. هر فایل را کامل در چت همان پروژه وارد کنید؛ اولین پرامپت اجرای مرحله ۱ را تا پیاده‌سازی و راستی‌آزمایی درخواست می‌کند. پس از handoff واقعی آن مرحله، پرامپت بعدی را اجرا کنید. نیاز نیست همه مراحل را در یک چت جا بدهید.

این فایل‌ها خودشان چیزی را اجرا نکرده‌اند و هیچ feature یا کد محصولی با ساخت این بسته تغییر نکرده است.

## ترتیب اجرا

1. [پروژه مرجع، اطلاعات پایه و قرارداد داده](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/speckit-prompts/01-project-reference.md>) — مسیر پیشنهادی `specs/051-a7-p1-project-reference`
2. [ایمنی واردسازی، دسترسی و حفظ تاریخچه](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/speckit-prompts/02-import-safety.md>) — مسیر پیشنهادی `specs/052-a7-p2-import-safety`
3. [صحت نگاشت WBS، فعالیت و زمان‌بندی](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/speckit-prompts/03-import-fidelity.md>) — مسیر پیشنهادی `specs/053-a7-p3-import-fidelity`
4. [پیش‌نمایش، تطبیق نتیجه و تجربه کاربر](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/speckit-prompts/04-import-experience.md>) — مسیر پیشنهادی `specs/054-a7-p4-import-experience`
5. [پایداری پردازش، فایل‌ها و محیط اجرا](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/speckit-prompts/05-import-operations.md>) — مسیر پیشنهادی `specs/055-a7-p5-import-operations`
6. [پذیرش یکپارچه و بسته تحویل کارفرما](</home/hossein/Desktop/projects/building-management/output/a7-requirements-2026-11-10/speckit-prompts/06-delivery-acceptance.md>) — مسیر پیشنهادی `specs/056-a7-p6-delivery-acceptance`

## قواعد استفاده

- این شش کار در همین workspace هم‌زمان اجرا نشوند؛ فایل‌های واردسازی و اشاره‌گر feature مشترک‌اند. مراحل به خروجی یکپارچه‌شده قبلی وابسته‌اند.
- مسیرهای 051 تا 056 پیشنهاد بر پایه وضعیت فعلی‌اند. هر پرامپت برخورد با شماره‌ای را که بعداً اشغال شده مدیریت می‌کند؛ مسیر واقعی در phase-map ثبت می‌شود.
- هر پرامپت چرخه specify → clarify در صورت نیاز → plan → tasks → analyze → implement → converge را درخواست می‌کند. اگر ابزار محیط فقط تک‌فرمان اجرا می‌کند، همین فرمان‌ها را به‌ترتیب و با مسیر صریح feature اجرا کنید؛ پس از specify کار را کامل‌شده تلقی نکنید.
- شش مرحله جدید متن‌های موجود 003/004/005/008/026/029 یا A.6 را جایگزین نمی‌کنند؛ برای شکاف‌های باقی‌مانده و شواهد تحویل‌اند. قابلیت موجود به‌جای بازنویسی با آزمون محافظت می‌شود.
- هر یک از ۵۶ قلم ممیزی یک مالک مستقیم دارد؛ مرحله ۶ همه را دوباره برای پذیرش بررسی می‌کند. شناسه‌های ممیزی، شناسه قرارداد نیستند. وضعیت ممیزی قبلی باید در کد روز بازبینی شود.
- ابهام واقعی، گیت بازبینی یا فقدان محیط واقعی می‌تواند پاسخ شما را لازم کند؛ متن‌ها مجوز ساخت تصمیم کارفرما یا نتیجه موفق فرضی نمی‌دهند.

## خروجی نهایی مورد انتظار

پروژه واقعی و داده صحیح واردشده؛ حفظ تاریخچه و نسخه‌های مصوب؛ ارقام و هشدارهای قابل تطبیق؛ واردسازی ایمن در اجرای واقعی؛ شواهد مرورگری دو زبان؛ راهنمای کوتاه و بسته تست کارفرما با نقص‌ها/پاسخ‌های باز. آمادگی فنی و پذیرش کارفرما دو وضعیت جدا هستند.

[نگاشت پوشش همه اقلام](coverage.json)
