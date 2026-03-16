from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    total_orders = serializers.IntegerField(read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'name', 'phone', 'email', 'address', 'notes', 'total_orders', 'created_at']
        read_only_fields = ['id', 'created_at']
