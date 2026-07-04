## 2024-06-26 - Django select_related Replacement Pitfall
**Learning:** Replacing an existing `select_related` argument instead of appending to it (e.g., swapping `select_related('business')` for `select_related('project')`) is dangerous. If the application relies on the removed relation for serialization or permissions, removing it causes an immediate N+1 query regression or a FieldError.
**Action:** When adding query optimizations like `select_related`, always append new fields rather than replacing existing ones unless explicitly verified that the old field is entirely unused in the request lifecycle.

## 2024-06-27 - SerializerMethodField N+1 Regression
**Learning:** In Django REST Framework, using `.values_list()` inside a `SerializerMethodField` (e.g. `obj.groups.values_list('name', flat=True)`) bypasses the prefetch cache and triggers an N+1 query regression, even if `prefetch_related` is properly set on the View's QuerySet.
**Action:** When serializing related fields, iterate over the prefetched relation in Python using `.all()` (e.g., `[item.name for item in obj.groups.all()]`) to safely utilize the prefetch cache.
