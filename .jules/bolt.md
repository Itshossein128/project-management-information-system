## 2024-06-25 - Django prefetch cache bypassing via querysets
**Learning:** In Django serializers and services, calling `.values_list()` or `.select_related()` directly on a related manager (e.g., `obj.role_permissions.values_list(...)`) bypasses the `prefetch_related` cache that was populated by the parent view's queryset, causing an N+1 query regression.
**Action:** Always iterate over `.all()` in Python when accessing related items in serializers or loops if the parent queryset has already prefetched them (e.g., `[rp.permission_codename for rp in obj.role_permissions.all()]`).
## 2024-07-07 - Django prefetch cache bypassing via .filter()
**Learning:** In Django serializers and services, calling `.filter(...)` directly on a related manager (e.g., `member.permission_overrides.filter(...)`) executes a new database query, even if the related objects have been prefetched using `prefetch_related()`. This bypasses the prefetch cache and causes N+1 database queries.
**Action:** Always iterate over `.all()` in Python using generator expressions (e.g., `next((o for o in member.permission_overrides.all() if ...), None)`) to utilize the prefetch cache when finding specific items in a prefetched collection.

## 2026-07-10 - Prevent QuerySet Re-evaluation in WBS sibling checks
**Learning:** In Django, iterating over a QuerySet multiple times (e.g., in a loop over different fields) evaluates the database query each time if the QuerySet isn't already fully evaluated and cached in memory. In `check_weight_warnings`, calling `parent.get_children()` returned a lazy QuerySet that was iterated over twice (for `weight_physical` and `weight_financial`), resulting in identical sequential database queries.
**Action:** Always evaluate a QuerySet to a `list()` first when iterating over it multiple times for different calculations, or compute all needed aggregations in a single pass over the list.
