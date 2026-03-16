from rest_framework import serializers
from .models import Order, OrderService, OrderPart


class OrderServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = OrderService
        fields = ['id', 'service', 'service_name', 'price']


class OrderPartSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='part.name', read_only=True)
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderPart
        fields = ['id', 'part', 'part_name', 'quantity', 'line_total']


class OrderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    car_display = serializers.CharField(source='car.__str__', read_only=True)
    mechanic_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_services = OrderServiceSerializer(many=True, read_only=True)
    order_parts = OrderPartSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'client', 'client_name', 'car', 'car_display',
            'assigned_mechanic', 'mechanic_name', 'status', 'status_display',
            'description', 'repair_notes', 'total_price',
            'order_services', 'order_parts',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']

    def get_mechanic_name(self, obj):
        if obj.assigned_mechanic:
            return obj.assigned_mechanic.get_full_name() or obj.assigned_mechanic.username
        return None


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['client', 'car', 'assigned_mechanic', 'status', 'description']
