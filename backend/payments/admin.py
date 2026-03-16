from django.contrib import admin
from .models import Payment
from .models_receipt import PaymentReceipt


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'payment_method', 'created_at')
    list_filter = ('payment_method', 'created_at')
    search_fields = ('order__client__name',)
    raw_id_fields = ('order',)


@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ('payment', 'created_at')
    search_fields = ('payment__order__client__name',)
