class ProjectNestedViewSetMixin:
    """
    Mixin for DRF ViewSets nested under a parent object in the URL route
    (e.g., urls have `(?P<project_pk>[^/.]+)/...`).

    Provides get_project_id(), and overrides get_queryset() and perform_create()
    to automatically scope querysets and create operations to the parent object.
    """
    nested_url_kwarg = 'project_pk'
    nested_model_field = 'project_id'

    def get_project_id(self):
        return self.kwargs.get(self.nested_url_kwarg)

    def get_queryset(self):
        parent_id = self.get_project_id()
        qs = super().get_queryset()
        if parent_id is not None:
            return qs.filter(**{self.nested_model_field: parent_id})
        return qs

    def perform_create(self, serializer):
        parent_id = self.get_project_id()
        if parent_id is not None:
            serializer.save(**{self.nested_model_field: parent_id})
        else:
            super().perform_create(serializer)
