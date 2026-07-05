## 2024-06-25 - Django prefetch cache bypassing via querysets
**Learning:** In Django serializers and services, calling `.values_list()` or `.select_related()` directly on a related manager (e.g., `obj.role_permissions.values_list(...)`) bypasses the `prefetch_related` cache that was populated by the parent view's queryset, causing an N+1 query regression.
**Action:** Always iterate over `.all()` in Python when accessing related items in serializers or loops if the parent queryset has already prefetched them (e.g., `[rp.permission_codename for rp in obj.role_permissions.all()]`).
