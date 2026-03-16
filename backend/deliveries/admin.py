from django.contrib import admin
from .models import Delivery, DeliveryItem


class DeliveryItemInline(admin.TabularInline):
    model = DeliveryItem
    extra = 1
    readonly_fields = ('line_total',)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'supplier', 'status', 'delivery_date', 'total_amount', 'stock_updated', 'created_at')
    list_filter = ('status', 'supplier', 'delivery_date')
    search_fields = ('invoice_number', 'supplier__name')
    readonly_fields = ('invoice_number', 'total_amount', 'stock_updated', 'created_at', 'updated_at')
    inlines = [DeliveryItemInline]


@admin.register(DeliveryItem)
class DeliveryItemAdmin(admin.ModelAdmin):
    list_display = ('delivery', 'part', 'quantity', 'unit_price')
    search_fields = ('part__name', 'delivery__invoice_number')
