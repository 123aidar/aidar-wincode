from django.db import models
from django.conf import settings
# Import repair report models for migrations and admin
from .models_report import RepairReport, RepairReportPart


class Order(models.Model):
    """Service order — central entity linking client, car, services, and parts."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        DIAGNOSTICS = 'diagnostics', 'Диагностика'
        REPAIRING = 'repairing', 'В ремонте'
        WAITING_PARTS = 'waiting_parts', 'Ожидание запчастей'
        COMPLETED = 'completed', 'Выполнен'
        DELIVERED = 'delivered', 'Выдан'

    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='orders')
    car = models.ForeignKey('cars.Car', on_delete=models.CASCADE, related_name='orders')
    assigned_mechanic = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_orders',
        limit_choices_to={'role': 'mechanic'}
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    description = models.TextField(blank=True, help_text='Initial complaint / description')
    repair_notes = models.TextField(blank=True, help_text='Mechanic repair notes')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.pk} — {self.client.name} — {self.get_status_display()}"

    def recalculate_total(self):
        """Recalculate total from services + parts."""
        services_total = sum(s.price for s in self.order_services.all())
        parts_total = sum(p.part.price * p.quantity for p in self.order_parts.all())
        self.total_price = services_total + parts_total
        self.save(update_fields=['total_price'])


class OrderService(models.Model):
    """Service line-item attached to an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_services')
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.service.name} on Order #{self.order_id}"

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.service.price
        super().save(*args, **kwargs)


class OrderPart(models.Model):
    """Spare part line-item attached to an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_parts')
    part = models.ForeignKey('parts.Part', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.part.name} x{self.quantity} on Order #{self.order_id}"

    @property
    def line_total(self):
        return self.part.price * self.quantity
