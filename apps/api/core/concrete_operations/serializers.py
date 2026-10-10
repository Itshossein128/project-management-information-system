from rest_framework import serializers

from concrete_operations.models import ConcreteBatch, ReadyMixDelivery
from resources.models import Supplier


class ConcreteBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConcreteBatch
        fields = ('id', 'date', 'volume_m3', 'cement_kg', 'sand_kg', 'aggregate_kg', 'water_l', 'plasticizer_l')
        read_only_fields = ('id',)


class ReadyMixDeliverySerializer(serializers.ModelSerializer):
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.none())
    supplier_name = serializers.CharField(source='supplier.supplier_name', read_only=True)

    class Meta:
        model = ReadyMixDelivery
        fields = ('id', 'date', 'volume_m3', 'supplier', 'supplier_name', 'ticket_number')
        read_only_fields = ('id', 'supplier_name')

    def get_fields(self):
        fields = super().get_fields()
        if getattr(self.context.get('view'), 'swagger_fake_view', False):
            return fields
        fields['supplier'].queryset = Supplier.objects.filter(project_id=self.context['view'].kwargs['project_pk'])
        return fields
