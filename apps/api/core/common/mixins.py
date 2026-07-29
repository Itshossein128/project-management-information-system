from rest_framework.decorators import action


class WorkflowViewSetMixin:
    """
    Mixin to provide standard workflow actions (submit, approve, reject) for DRF ViewSets.
    Subclasses must implement the corresponding template methods: _submit, _approve, _reject.
    """

    @action(detail=True, methods=['post'])
    def submit(self, request, *args, **kwargs):
        return self._submit(self.get_object(), request)

    @action(detail=True, methods=['post'])
    def approve(self, request, *args, **kwargs):
        return self._approve(self.get_object(), request)

    @action(detail=True, methods=['post'])
    def reject(self, request, *args, **kwargs):
        return self._reject(self.get_object(), request)

    def _submit(self, instance, request):
        raise NotImplementedError("Subclasses must implement _submit()")

    def _approve(self, instance, request):
        raise NotImplementedError("Subclasses must implement _approve()")

    def _reject(self, instance, request):
        raise NotImplementedError("Subclasses must implement _reject()")


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
