## 2024-06-26 - Django select_related Replacement Pitfall
**Learning:** Replacing an existing `select_related` argument instead of appending to it (e.g., swapping `select_related('business')` for `select_related('project')`) is dangerous. If the application relies on the removed relation for serialization or permissions, removing it causes an immediate N+1 query regression or a FieldError.
**Action:** When adding query optimizations like `select_related`, always append new fields rather than replacing existing ones unless explicitly verified that the old field is entirely unused in the request lifecycle.
## 2024-06-29 - [Django values_list bypasses prefetch cache]
**Learning:** Using `.values_list()` inside a `SerializerMethodField` forces a database query even if the related field is prefetched using `prefetch_related`. This can lead to severe N+1 query problems in DRF lists.
**Action:** Always use Python iteration with `.all()` (e.g., `[g.name for g in obj.groups.all()]`) when reading related fields in serializers, and ensure the field is prefetched in the view's queryset.
