class ProjectNestedViewSetMixin:
    """
    Mixin to automatically scope querysets and perform_create operations
    for DRF ViewSets nested under a parent object in the URL route.
    """
    nested_url_kwarg = 'project_pk'
    nested_model_field = 'project_id'

    def get_queryset(self):
        qs = super().get_queryset()
        nested_val = self.kwargs.get(self.nested_url_kwarg)
        if nested_val is not None:
            filter_kwargs = {self.nested_model_field: nested_val}
            qs = qs.filter(**filter_kwargs)
        return qs

    def perform_create(self, serializer):
        nested_val = self.kwargs.get(self.nested_url_kwarg)
        kwargs = {}
        if nested_val is not None:
            kwargs[self.nested_model_field] = nested_val
        serializer.save(**kwargs)
