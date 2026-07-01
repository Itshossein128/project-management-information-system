## 2024-06-26 - Django select_related Replacement Pitfall
**Learning:** Replacing an existing `select_related` argument instead of appending to it (e.g., swapping `select_related('business')` for `select_related('project')`) is dangerous. If the application relies on the removed relation for serialization or permissions, removing it causes an immediate N+1 query regression or a FieldError.
**Action:** When adding query optimizations like `select_related`, always append new fields rather than replacing existing ones unless explicitly verified that the old field is entirely unused in the request lifecycle.
## 2026-07-01 - Django SerializerMethodField N+1 Regression with values_list
**Learning:** Using `.values_list()` inside a `SerializerMethodField` (e.g. `obj.groups.values_list('name', flat=True)`) forces a new database query for each object, completely bypassing the `prefetch_related` cache in Django.
**Action:** When serializing M2M or Reverse FK relationships inside a `SerializerMethodField`, always iterate over `.all()` in Python (e.g. `[item.name for item in obj.related.all()]`) after ensuring the relation is included in the View's `prefetch_related` queryset.
