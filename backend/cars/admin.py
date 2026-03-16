from django.contrib import admin
from .models import Car


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year', 'license_plate', 'client', 'vin')
    search_fields = ('brand', 'model', 'vin', 'license_plate')
    list_filter = ('brand', 'year')
    raw_id_fields = ('client',)
