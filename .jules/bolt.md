## 2024-06-26 - Django select_related Replacement Pitfall
**Learning:** Replacing an existing `select_related` argument instead of appending to it (e.g., swapping `select_related('business')` for `select_related('project')`) is dangerous. If the application relies on the removed relation for serialization or permissions, removing it causes an immediate N+1 query regression or a FieldError.
**Action:** When adding query optimizations like `select_related`, always append new fields rather than replacing existing ones unless explicitly verified that the old field is entirely unused in the request lifecycle.
## 2024-07-28 - Django values_list in SerializerMethodField Pitfall
**Learning:** Using `.values_list()` inside a Django Rest Framework `SerializerMethodField` to extract related fields bypasses the prefetch cache populated by `prefetch_related`. This results in N+1 queries, even if the queryset correctly prefetches the relation.
**Action:** When extracting data from a related field in a serializer method, use list comprehension iterating over `.all()` (e.g., `[item.name for item in obj.related.all()]`) to allow Django to utilize the prefetched data.
