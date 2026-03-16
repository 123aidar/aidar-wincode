from django.db import models
from django.conf import settings
from django.utils import timezone


def generate_invoice_number():
    """Generate sequential invoice number like ПОС-20260001."""
    year = timezone.now().year
    prefix = f'ПОС-{year}'
    last = Delivery.objects.filter(invoice_number__startswith=prefix).count()
    return f'{prefix}{(last + 1):04d}'


class Delivery(models.Model):
    """Поставка запчастей от поставщика."""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        CONFIRMED = 'confirmed', 'Подтверждена'
        RECEIVED = 'received', 'Получена'
        CANCELLED = 'cancelled', 'Отменена'

    invoice_number = models.CharField(max_length=30, unique=True, blank=True, verbose_name='Номер накладной')
    supplier = models.ForeignKey(
        'suppliers.Supplier', on_delete=models.PROTECT,
        related_name='deliveries', verbose_name='Поставщик'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name='Статус')
    delivery_date = models.DateField(verbose_name='Дата поставки')
    notes = models.TextField(blank=True, verbose_name='Примечания')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Сумма')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_deliveries', verbose_name='Создал'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Track if stock was already updated
    stock_updated = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Поставка'
        verbose_name_plural = 'Поставки'

    def __str__(self):
        return f'{self.invoice_number} — {self.supplier.name}'

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = generate_invoice_number()
        # Recalculate total
        if self.pk:
            self.total_amount = sum(
                item.line_total for item in self.items.all()
            )
        super().save(*args, **kwargs)

    def recalc_total(self):
        self.total_amount = sum(item.line_total for item in self.items.all())
        Delivery.objects.filter(pk=self.pk).update(total_amount=self.total_amount)

    def apply_to_stock(self):
        """Зачислить запчасти на склад. Вызывается при переводе в статус «Получена»."""
        if self.stock_updated:
            return
        for item in self.items.select_related('part').all():
            item.part.quantity += item.quantity
            item.part.save(update_fields=['quantity'])
        Delivery.objects.filter(pk=self.pk).update(stock_updated=True)
        self.stock_updated = True


class DeliveryItem(models.Model):
    """Позиция в поставке."""
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='items', verbose_name='Поставка')
    part = models.ForeignKey('parts.Part', on_delete=models.PROTECT, related_name='delivery_items', verbose_name='Запчасть')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за ед.')

    class Meta:
        verbose_name = 'Позиция поставки'
        verbose_name_plural = 'Позиции поставки'

    def __str__(self):
        return f'{self.part.name} × {self.quantity}'

    @property
    def line_total(self):
        return self.unit_price * self.quantity
