## 2024-06-25 - Resolve N+1 queries in DailyReportListSerializer
**Learning:** Calling `.filter()` or `.count()` on a related manager (e.g., `obj.activities.filter(is_deleted=False).count()`) within a serializer method ignores the prefetch cache entirely, resulting in N+1 queries per report.
**Action:** When evaluating related collections in a serializer (like DRF SerializerMethodField), ensure `.prefetch_related` is called in the viewset, and then use Python's built-in iterator functions over `.all()` (e.g., `sum(1 for x in obj.related.all() if not x.is_deleted)`) instead of `.filter()`.
