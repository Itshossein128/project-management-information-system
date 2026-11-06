# شواهد بازبینی فاز دوم — ۱۵ آبان ۱۴۰۵

مبنا: HEAD `5234cf7317c3fa33fe70aa52b58206ea38e207a4` با تغییرات commitنشده فاز دوم. کد محصول در این بازبینی تغییر نکرد. پایگاه تست مستقل `test_velora_p2_review_20261105` بود.

- ۱۹ آزمون موجود دوباره موفق شدند؛ سه آزمون تکمیلی این پوشه شکست خوردند. این شکست‌ها رفتار مطلوب را assert می‌کنند و xfail نیستند.
- خواندن نقش محلی توسط غیرعضو از مسیر سراسری: HTTP 200، انتظار منع.
- تغییر مجوز نقش محلی توسط staff فاقد عضویت از مسیر سراسری: HTTP 200 و تغییر واقعی، انتظار منع.
- تغییر نام نقش محلی: HTTP 200 و صفر رکورد RoleAccessChange، انتظار ردپای پایه.
- `pnpm typecheck` با کد خروج صفر موفق بود. مرورگر محصول در این بازبینی دوباره اجرا نشد.
- بازیابی دانش به علت stale بودن رد شد و تازه‌سازی semantic با خطای محلی 502 کامل نشد؛ شاهد این بررسی، فایل اصلی جاری و اجرای API/pytest است.

برای بازاجرا از apps/api/core، تنظیمات محلی را بدون چاپ secrets بارگذاری کنید و TEST_DATABASE_NAME را به پایگاه تست مستقل تنظیم کنید. pytest.ini همین پوشه core مبنای تنظیمات است. conftest.py همراه، عکس fixtureهای اصلی در زمان بازبینی است.

```bash
../.venv/bin/python -m pytest -c pytest.ini projects/tests/test_local_roles.py permissions/tests/test_permission_origin.py projects/tests/test_positions_and_history.py permissions/tests/test_roles_api.py /home/hossein/Desktop/projects/building-management/output/a6-requirements-2026-11-04/p2-review-evidence-2026-11-05/test_review_probes.py -q -s --reuse-db
```

پس از اصلاح، این سه آزمون باید واقعاً موفق شوند و آزمون تمام actionهای نقش محلی از مسیر سراسری نیز افزوده شود. موفقیت این زیرمجموعه به معنی پذیرش کارفرما یا کل ماتریس A.6 نیست.
