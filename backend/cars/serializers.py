from rest_framework import serializers
from .models import Car


class CarSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'client', 'client_name', 'brand', 'model', 'year', 'vin', 'license_plate', 'color', 'mileage', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']
