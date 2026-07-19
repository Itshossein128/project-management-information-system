## 2024-06-25 - Resolve N+1 queries in DailyReportListSerializer
**Learning:** Calling `.filter()` or `.count()` on a related manager (e.g., `obj.activities.filter(is_deleted=False).count()`) within a serializer method ignores the prefetch cache entirely, resulting in N+1 queries per report.
**Action:** When evaluating related collections in a serializer (like DRF SerializerMethodField), ensure `.prefetch_related` is called in the viewset, and then use Python's built-in iterator functions over `.all()` (e.g., `sum(1 for x in obj.related.all() if not x.is_deleted)`) instead of `.filter()`.

## 2025-03-01 - Optimizing Django Queries in Loops
**Learning:** Nested loops accessing related fields across Django ORM querysets can easily trigger N+1 query patterns. `prefetch_related` helps when iterating over related records via reverse foreign keys or many-to-many, pulling data into memory.
**Action:** When a loop iterates through a QuerySet to generate records, use `prefetch_related` for nested attributes and `bulk_create` on the output list to collapse all DB queries down to just a few round-trips.

## 2025-03-01 - Avoid N+1 queries when traversing trees
**Learning:** Using tree models (like django-treebeard's MP_Node) recursively with `get_children()` causes an N+1 query problem, fetching nodes one by one.
**Action:** When updating or traversing the entire tree, use an iterative approach with a single query (`WBS.get_annotated_list_qs(queryset)`) and `bulk_update` to batch database updates, resolving the N+1 query bottleneck.

## 2026-07-14 - Resolve N+1 query in SubReportSerializer
**Learning:** Calling `.filter()` or `.count()` on a related manager (e.g. `obj.activities.filter(is_deleted=False).count()`) in a DRF `SerializerMethodField` bypasses Django's `prefetch_related` cache entirely, causing a severe N+1 query issue when serializing lists.
**Action:** When a queryset in the view uses `prefetch_related`, serializer methods should retrieve the related collection via `.all()` and iterate over it in python (e.g. `sum(1 for activity in obj.activities.all() if not activity.is_deleted)`) to maintain optimal performance.

## 2025-03-01 - Avoid N+1 query loop when fetching latest related record
**Learning:** Looping over a queryset and using `.filter(...).order_by('date').first()` on a related model creates severe N+1 queries.
**Action:** When needing the "latest" related record for multiple parent records, use `.distinct('parent_id')` with `.order_by('parent_id', '-date')` to fetch them all in a single query, map them in Python by `parent_id`, and pull from the map during iteration.

## 2026-07-17 - Resolve N+1 query in Subcontractor API
**Learning:** Using `.filter()`, `.count()`, or `.exists()` on related objects (e.g., `obj.warnings.filter(...)`) within a serializer or looped service function completely bypasses Django's `prefetch_related` cache, leading to severe N+1 query performance degradation.
**Action:** Always prefetch related collections in the viewset (`.prefetch_related('scores', 'warnings')`), and strictly iterate over `.all()` in Python (using list comprehensions, `max()`, `sum()`, or `any()`) when serializing or computing logic for lists of objects.

## 2024-07-23 - Python iteration over prefetched collections to avoid N+1 queries
**Learning:** Using `.filter()` on related object managers (e.g., `obj.activities.filter(is_deleted=False)`) bypasses the `prefetch_related` cache and triggers a new database query for every item, leading to N+1 query problems in DRF serializers.
**Action:** When a queryset is prefetched, iterate over `.all()` and apply the filtering condition in Python (e.g., `[item for item in manager.all() if not item.is_deleted]`).
