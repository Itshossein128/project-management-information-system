## 2024-06-26 - Django select_related Replacement Pitfall
**Learning:** Replacing an existing `select_related` argument instead of appending to it (e.g., swapping `select_related('business')` for `select_related('project')`) is dangerous. If the application relies on the removed relation for serialization or permissions, removing it causes an immediate N+1 query regression or a FieldError.
**Action:** When adding query optimizations like `select_related`, always append new fields rather than replacing existing ones unless explicitly verified that the old field is entirely unused in the request lifecycle.
## 2024-05-19 - Django values_list() vs all() N+1
**Learning:** Using `.values_list()` inside a DRF `SerializerMethodField` completely bypasses prefetch caches and triggers N+1 queries. Iterating over `.all()` in Python evaluates against the already fetched data.
**Action:** Always prefetch related fields in views, and use list comprehensions over `.all()` instead of `.values_list()` in serializers to maintain performance.
