## 2024-06-25 - Resolve N+1 queries in DailyReportListSerializer
**Learning:** Calling `.filter()` or `.count()` on a related manager (e.g., `obj.activities.filter(is_deleted=False).count()`) within a serializer method ignores the prefetch cache entirely, resulting in N+1 queries per report.
**Action:** When evaluating related collections in a serializer (like DRF SerializerMethodField), ensure `.prefetch_related` is called in the viewset, and then use Python's built-in iterator functions over `.all()` (e.g., `sum(1 for x in obj.related.all() if not x.is_deleted)`) instead of `.filter()`.

## 2025-03-01 - Optimizing Django Queries in Loops
**Learning:** Nested loops accessing related fields across Django ORM querysets can easily trigger N+1 query patterns. `prefetch_related` helps when iterating over related records via reverse foreign keys or many-to-many, pulling data into memory.
**Action:** When a loop iterates through a QuerySet to generate records, use `prefetch_related` for nested attributes and `bulk_create` on the output list to collapse all DB queries down to just a few round-trips.

## 2025-03-01 - Avoid N+1 queries when traversing trees
**Learning:** Using tree models (like django-treebeard's MP_Node) recursively with `get_children()` causes an N+1 query problem, fetching nodes one by one.
**Action:** When updating or traversing the entire tree, use an iterative approach with a single query (`WBS.get_annotated_list_qs(queryset)`) and `bulk_update` to batch database updates, resolving the N+1 query bottleneck.
