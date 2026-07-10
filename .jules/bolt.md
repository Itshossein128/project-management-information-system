## 2024-06-25 - Django prefetch cache bypassing via querysets
**Learning:** In Django serializers and services, calling `.values_list()` or `.select_related()` directly on a related manager (e.g., `obj.role_permissions.values_list(...)`) bypasses the `prefetch_related` cache that was populated by the parent view's queryset, causing an N+1 query regression.
**Action:** Always iterate over `.all()` in Python when accessing related items in serializers or loops if the parent queryset has already prefetched them (e.g., `[rp.permission_codename for rp in obj.role_permissions.all()]`).
## 2024-07-07 - Django prefetch cache bypassing via .filter()
**Learning:** In Django serializers and services, calling `.filter(...)` directly on a related manager (e.g., `member.permission_overrides.filter(...)`) executes a new database query, even if the related objects have been prefetched using `prefetch_related()`. This bypasses the prefetch cache and causes N+1 database queries.
**Action:** Always iterate over `.all()` in Python using generator expressions (e.g., `next((o for o in member.permission_overrides.all() if ...), None)`) to utilize the prefetch cache when finding specific items in a prefetched collection.
## 2024-07-24 - ProjectNestedViewSetMixin implementation
 **Learning:** There were multiple ViewSets repeating URL kwarg `project_pk` retrieval, nested `get_queryset` filtering, and nested `perform_create` id assignment.
 **Action:** We implemented a `ProjectNestedViewSetMixin` in `apps/api/core/common/mixins.py` that abstracts away nested DRF ViewSet filtering and creation mapping. Use this mixin for ViewSets nested under an entity in DRF urls instead of manually pulling `.kwargs.get('project_pk')`.
