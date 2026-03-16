from rest_framework import serializers
from .models import Part


class PartSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Part
        fields = ['id', 'name', 'part_number', 'description', 'price', 'cost_price', 'quantity', 'minimum_stock', 'supplier', 'supplier_name', 'is_low_stock', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
