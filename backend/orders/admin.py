from django.contrib import admin
from .models import Order, OrderService, OrderPart
from .models_report import RepairReport, RepairReportPart


class OrderServiceInline(admin.TabularInline):
    model = OrderService
    extra = 0


class OrderPartInline(admin.TabularInline):
    model = OrderPart
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'car', 'status', 'assigned_mechanic', 'total_price', 'created_at')
    list_filter = ('status', 'assigned_mechanic', 'created_at')
    search_fields = ('client__name', 'car__license_plate', 'description')
    raw_id_fields = ('client', 'car', 'assigned_mechanic')
    inlines = [OrderServiceInline, OrderPartInline]


@admin.register(RepairReport)
class RepairReportAdmin(admin.ModelAdmin):
    list_display = ('order', 'started_at', 'finished_at', 'total_price', 'created_at')
    search_fields = ('order__client__name', 'order__car__license_plate')
    filter_horizontal = ('mechanics',)


@admin.register(RepairReportPart)
class RepairReportPartAdmin(admin.ModelAdmin):
    list_display = ('report', 'part', 'quantity', 'price')
    search_fields = ('part__name',)
