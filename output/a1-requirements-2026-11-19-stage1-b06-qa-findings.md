# Stage 1.2 QA Verification Report: Requirement B06 — بسته تحویل و پذیرش اولیه کارفرما

## 1. شناسه و عنوان نیازمندی (Requirement Identity)
- **شناسه نیازمندی:** B06
- **عنوان:** بسته تحویل و پذیرش اولیه کارفرما (Delivery Package & Client Initial Acceptance)
- **فاز / مرحله:** Phase A.1 / Stage 1.2 (End-User & QA Verification)
- **معیار پذیرش مصوب (Acceptance Criteria):**
  > «Release/SHA، ورودی، expected، راهنمای نقش‌ها، نمونه‌ها، checksum و نتیجه صریح آزمون کارفرما روی همان نسخه ثبت شود.»
- **گروه‌های تحت مالکیت مستقیم (Direct Owned Groups):** E09, Q03, Q04, Q05
- **پیش‌نیازهای معنایی:** تکمیل و بسته شدن معتبر B01 تا B05.

---

## 2. ارزیابی از دیدگاه پرسوناها و کاربران واقعی (End-User Personas & QA Evaluation)

### ۲.۱. پرسونای کارفرما و نماینده عالی پروژه (Client / Owner Representative)
- **خواسته کارفرما:** دریافت یک بسته نهایی غیرقابل دستکاری و منجمد (Frozen Release) به همراه کد منبع مشخص (Git SHA)، پیوند محیط مستقر، چک‌سام فایل‌های دانلودی (SHA-256) اکسل و PDF و امکان تست مستقیم سناریوهای پذیرش بدون مغایرت اعداد و فرمول‌ها، و در نهایت ثبت صورت‌جلسه یا رأی صریح پذیرش اولیه.
- **مشاهده کارفرما:**
  - هیچ بسته رسمی Release یا تگ تثبیت‌شده حاوی آرشیو و چک‌سام نهایی برای فاز A.1 تولید نشده است (آخرین بسته آرشیو مربوط به فاز قبلی A.7 به تاریخ 2026-11-16 بوده است).
  - هیچ صورت‌جلسه، امضای دیجیتال یا ثبت سیستمی رأی کارفرما (Acceptance Sign-off / Protocol) در سیستم وجود ندارد. وضعیت فعلی صرفاً «pending» یا بلاتکلیف است.

### ۲.۲. پرسونای ناظر پروژه و بازرس دفتر فنی (Project Supervisor / Technical Inspector)
- **خواسته ناظر:** اطمینان از صحت درخت تصمیم (Decision Tree)، تفکیک کامل مجوزهای نقش‌های مختلف (تهیه‌کننده، ناظر، کارفرما، کاربر غیرمجاز، و ایزولاسیون پروژه‌ها - Multi-Tenancy / Cross-Project Leakage Prevention).
- **مشاهده ناظر:**
  - کنترل‌های `view_reports` و `IsProjectMember` در بک‌اند پیاده شده‌اند، اما ماتریس تست منفی (Negative Security & Cross-Project Leakage via Direct ID manipulation) روی نسخه مستقر زنده اثبات نشده و تست‌های E2E خودکار به علت بالا نبودن سرورهای محلی اجرا نشده‌اند.
  - درخت تصمیم در `docs/decision-tree/` به ثبت مسیرها پرداخته اما سناریوهای دانلود مستقیم و تمایز دقیق حالت submitted در برابر approved و محدودیت‌های watermark و fingerprint هنوز مستلزم اعتبارسنجی زنده است.

### ۲.۳. پرسونای مهندس اجرا / تهیه‌کننده گزارش و کاربر موبایل (Field Engineer / Report Preparer)
- **خواسته مهندس کارگاه:** دسترسی و آزمایش کامل در دسکتاپ و موبایل، در دو زبان فارسی (RTL) و انگلیسی (LTR)، از ثبت واحد تا تجمیع و اصلاح و صدور فایل اکسل و PDF.
- **مشاهده مهندس کارگاه:**
  - با توجه به نقص‌های باز در پیش‌نیازها (B01 تا B05)، به ویژه عدم تطابق فرم چیدمان اکسل با فرم شیراز (DEF-B03-02)، خطای چاپ ساعات شیفت (DEF-B03-01)، خطای تراز A4 و نبود تکرار هدر (DEF-B03-03)، و ابهام صفر واقعی در برابر نامعلوم (DEF-B03-05)، بسته دانلودی فعلی از نظر کارفرما و تهیه‌کننده غیرقابل پذیرش نهایی است.
  - در حالت موبایل و زبان انگلیسی، برخی برچسب‌های HSE و خطاهای هدر فاقد محلی‌سازی کامل هستند.

---

## 3. نقص‌ها و شکاف‌های احراز شده (Identified Defects & Gaps)

1. **DEF-B06-01: فقدان بسته رسمی و منجمد فاز A.1 (Missing A.1 Frozen Release & Checksum Package)**
   - *شرح:* بسته قابل تحویل فاز A.1 با مشخصات Commit SHA، تارگت، فایل‌های خروجی اکسل/PDF همراه با Digest/SHA-256 و داده‌های ورودی/Expected مستقل در پوشه خروجی‌ها ایجاد نشده است.
   - *شدت:* Critical (مسدودکننده پذیرش)

2. **DEF-B06-02: باز ماندن پیش‌نیازهای زنجیره پذیرش (Unresolved Hard Dependencies B01-B05)**
   - *شرح:* پیش‌نیازهای حیاتی بسته B06 شامل قرارداد داده (B01)، یکپارچگی نسخه و قفل مشتقات (B02)، تطابق اکسل/PDF با فرم مرجع (B03)، فیلترها و تجمیع مستقل (B04) و تطابق مستقل محاسبات (B05) همگی دارای نقص‌های باز، Strict XFAIL و عدم انطباق با نمونه مرجع هستند.

3. **DEF-B06-03: فقدان مکانیسم و صورت‌جلسه صریح ثبت پذیرش اولیه کارفرما (Missing Client Acceptance Sign-off Mechanism)**
   - *شرح:* طبق تصریح معیار پذیرش و دستورالعمل‌های پروژه، آزمون‌های خودکار و ابزارهای توسعه‌دهنده مجاز به امضا به جای کارفرما نیستند. هیچ فیلد یا فرایندی برای ثبت پذیرش یا رد صریح توسط کارفرما پیاده‌سازی و ثبت نشده است.

4. **DEF-B06-04: عدم اثبات زنده ایزولاسیون دسترسی و نشت بین‌پروژه‌ای (Unverified Cross-Project Isolation on Live Release)**
   - *شرح:* بررسی مجوز مشاهده/دانلود (گروه E09) و عدم نشت اطلاعات با ID مستقیم به صورت زنده روی سرور مستقر دسکتاپ/موبایل انجام نشده و با خاموش بودن محیط‌های محلی (5173 / 8000)، شواهد اجرای زنده مفقود است.

5. **DEF-B06-05: نقص‌های تجربه کاربری دو زبانه و موبایل (FA/EN and Responsive Mobile Gaps - Group Q03)**
   - *شرح:* تست کامل ثبت، بازبینی، دانلود و چاپ در مرورگر موبایل و زبان انگلیسی همراه با RTL/LTR صحیح برای کلیه ۱۸ بخش گزارش روزانه به صورت مستند و بدون نقص در قالب بسته آزمون ثبت نشده است.

---

## 4. وضعیت کنترل کیفیت و نتیجه نهایی (QA Verdict)

```json
{
  "requirementId": "B06",
  "title": "بسته تحویل و پذیرش اولیه کارفرما",
  "phase": "A.1",
  "stage": "1.2",
  "evaluatedAt": "2026-11-19T17:12:00+03:30",
  "acceptanceCriteria": "Release/SHA، ورودی، expected، راهنمای نقش‌ها، نمونه‌ها، checksum و نتیجه صریح آزمون کارفرما روی همان نسخه ثبت شود.",
  "qaStatus": "qa_failed",
  "defects": [
    "DEF-B06-01: Missing A.1 frozen delivery package (Commit SHA, archive, and SHA-256 checksums)",
    "DEF-B06-02: Open blocker defects and Strict XFAILs in prerequisite packages B01 through B05",
    "DEF-B06-03: Missing client initial acceptance protocol/sign-off mechanism (agent cannot sign on behalf of client)",
    "DEF-B06-04: Unverified live multi-tenant cross-project authorization and direct ID download isolation (Group E09)",
    "DEF-B06-05: Incomplete mobile responsive & bilingual FA/EN verification evidence for end-to-end report workflow (Group Q03)"
  ],
  "summary": "Requirement B06 failed QA verification because the frozen release package (Release/SHA, inputs, expected files, checksums) for Phase A.1 is not generated, prerequisite packages B01-B05 remain open with defects, live cross-project authorization on running instances is unverified, and no explicit client initial acceptance protocol is recorded."
}
```
