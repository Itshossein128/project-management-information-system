# مرجع نمونه کد رتبه‌بندی

**مسئولیت:** نگهداری نمونه قابل‌ویرایش و شرح رفتار واقعی رابط آن.

**هدف:** توسعه‌دهنده بداند تابع نمونه چه داده‌ای می‌گیرد، چه نتیجه‌ای می‌دهد و کدام نیازهای محصول را پوشش نمی‌دهد.

## جایگاه نمونه

کد زیر از بخش ۱۰ [سند اصلی](<../document (10).docx>) استخراج شده و بدون تغییر محاسبات یا پیام‌ها نگهداری می‌شود. کد نمونه، صرفاً SAW و TOPSIS را اجرا می‌کند. استقلال روش‌ها و رفتار محصول از [دامنه ماژول](01-module-scope.md) و [چرخه اجرا](08-execution-records.md) پیروی می‌کنند.

## رابط تابع

```python
rank_options(criteria, alternatives, weights, types, matrix)
```

پنج آرگومان از [قرارداد ورودی](02-decision-inputs.md) گرفته می‌شوند. تابع وزن‌ها را نرمال می‌کند و یک نگاشت با کلیدهای `SAW` و `TOPSIS` برمی‌گرداند. هر مقدار، فهرستی از رکوردهای دارای `option`، `SAW` و `TOPSIS` است که بر اساس امتیاز همان روش مرتب شده‌اند. تابع فیلد رتبه عددی تولید نمی‌کند.

## کد قابل‌ویرایش

```python
from math import isfinite, sqrt


def rank_options(criteria, alternatives, weights, types, matrix):
    """رتبه‌بندی گزینه‌ها با SAW و TOPSIS.

    criteria: نام معیارها؛ حداکثر 10
    alternatives: نام گزینه‌ها؛ حداکثر 10
    weights: وزن هر معیار به همان ترتیب
    types: برای هر معیار، 'benefit' یا 'cost'
    matrix: ردیف برای هر گزینه و ستون برای هر معیار
    """
    m, n = len(alternatives), len(criteria)

    if not 1 <= n <= 10 or not 1 <= m <= 10:
        raise ValueError("تعداد معیارها و گزینه‌ها باید بین 1 تا 10 باشد.")
    if len(set(criteria)) != n or len(set(alternatives)) != m:
        raise ValueError("نام معیارها و گزینه‌ها باید یکتا باشد.")
    if any(not str(x).strip() for x in criteria + alternatives):
        raise ValueError("نام معیار یا گزینه نمی‌تواند خالی باشد.")
    if len(weights) != n or len(types) != n or len(matrix) != m:
        raise ValueError("تعداد وزن‌ها، نوع معیارها یا سطرهای ماتریس نادرست است.")
    if any(len(row) != n for row in matrix):
        raise ValueError("هر سطر ماتریس باید دقیقاً به تعداد معیارها مقدار داشته باشد.")
    if any(t not in ("benefit", "cost") for t in types):
        raise ValueError("نوع معیار فقط benefit یا cost است.")
    if any(not isfinite(float(w)) or float(w) < 0 for w in weights):
        raise ValueError("وزن‌ها باید عدد متناهی و نامنفی باشند.")
    if any(not isfinite(float(x)) or float(x) < 0
           for row in matrix for x in row):
        raise ValueError("مقادیر ماتریس باید عدد متناهی و نامنفی باشند.")
    if any(types[j] == "cost" and
           any(float(matrix[i][j]) <= 0 for i in range(m))
           for j in range(n)):
        raise ValueError("مقادیر معیار هزینه باید بزرگ‌تر از صفر باشند.")

    weight_sum = sum(float(w) for w in weights)
    if weight_sum <= 0:
        raise ValueError("حداقل یک وزن باید بزرگ‌تر از صفر باشد.")
    w = [float(x) / weight_sum for x in weights]
    x = [[float(v) for v in row] for row in matrix]

    # SAW: نرمال‌سازی معیارهای سود و هزینه
    saw = [0.0] * m
    for j in range(n):
        col = [x[i][j] for i in range(m)]
        if types[j] == "benefit":
            largest = max(col)
            if largest == 0:
                raise ValueError("ستون معیار سود نمی‌تواند همگی صفر باشد.")
            normalized = [v / largest for v in col]
        else:
            smallest = min(col)
            normalized = [smallest / v for v in col]
        for i in range(m):
            saw[i] += w[j] * normalized[i]

    # TOPSIS: نرمال‌سازی برداری و وزن‌دهی
    norm = []
    for j in range(n):
        denom = sqrt(sum(x[i][j] ** 2 for i in range(m)))
        if denom == 0:
            raise ValueError("ستون ماتریسِ تماماً صفر قابل نرمال‌سازی نیست.")
        norm.append([x[i][j] / denom * w[j] for i in range(m)])

    ideal_best, ideal_worst = [], []
    for j in range(n):
        values = norm[j]
        if types[j] == "benefit":
            ideal_best.append(max(values))
            ideal_worst.append(min(values))
        else:
            ideal_best.append(min(values))
            ideal_worst.append(max(values))

    topsis = []
    for i in range(m):
        d_best = sqrt(sum((norm[j][i] - ideal_best[j]) ** 2
                          for j in range(n)))
        d_worst = sqrt(sum((norm[j][i] - ideal_worst[j]) ** 2
                           for j in range(n)))
        total = d_best + d_worst
        topsis.append(d_worst / total if total else 0.5)

    results = []
    for i, name in enumerate(alternatives):
        results.append({"option": name, "SAW": saw[i], "TOPSIS": topsis[i]})
    return {
        "SAW": sorted(results, key=lambda r: r["SAW"], reverse=True),
        "TOPSIS": sorted(results, key=lambda r: r["TOPSIS"], reverse=True),
    }
```

## محدودیت‌های نمونه

- هر فراخوانی هر دو روش را اجرا می‌کند؛ آرگومان انتخاب روش ندارد. تفکیک موتورهای مستقل یا تغییر رابط، کار اتصال به محصول است و در این بازآرایی انجام نشده است.
- AHP، DEMATEL و ISM در نمونه وجود ندارند.
- فاصله‌های TOPSIS در داخل تابع محاسبه می‌شوند ولی در خروجی بازگردانده نمی‌شوند.
- خطاها به‌صورت استثنا مطرح می‌شوند و اشاره ساختاریافته به فیلد یا خانه ندارند؛ خطاهای تبدیل عدد نیز لزوماً پیام اختصاصی فارسی ندارند.
- مرتب‌سازی امتیازهای مساوی، ترتیب ورودی را حفظ می‌کند؛ این رفتار رتبه مشترک یا برتری یک گزینه را تعریف نمی‌کند.
- شرط `total == 0` در TOPSIS امتیاز `0.5` می‌دهد. ستون تماماً صفر پیش از این مرحله رد می‌شود.
- فرم ورود داده، انتخاب روش، ذخیره نسخه ورودی، سابقه مستقل و نمایش نتیجه در نمونه پیاده‌سازی نشده‌اند.
- تبدیل `float` و محاسبات ساده، تضمین پایداری برای همه اعداد متناهی بسیار بزرگ نیستند؛ بازه قابل قبول و سیاست عددی نهایی در [موارد باز](11-source-review.md) مشخص شده است.

## اسناد مرتبط

تعریف ریاضی در [SAW](03-saw.md) و [TOPSIS](04-topsis.md) آمده است. نیازهای اتصال در [چرخه اجرا](08-execution-records.md)، بررسی خروجی در [معیارهای پذیرش](10-acceptance-checks.md)، و مستندات Python در [منابع](12-references.md) قرار دارند.
