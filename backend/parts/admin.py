from django.contrib import admin
from .models import Part


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('name', 'part_number', 'price', 'cost_price', 'quantity', 'supplier', 'is_low_stock')
    search_fields = ('name', 'part_number')
    list_filter = ('supplier',)
    raw_id_fields = ('supplier',)

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
