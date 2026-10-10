from types import SimpleNamespace

from concrete_operations.serializers import ReadyMixDeliverySerializer


def test_ready_mix_schema_works_without_a_project_and_keeps_supplier_queryset_empty():
    view = SimpleNamespace(swagger_fake_view=True, kwargs={})
    serializer = ReadyMixDeliverySerializer(context={'view': view})
    assert serializer.fields['supplier'].queryset.query.is_empty()
