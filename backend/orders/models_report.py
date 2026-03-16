from django.db import models
from django.conf import settings

class RepairReport(models.Model):
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='repair_report')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    mechanics = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='repair_reports')
    parts = models.ManyToManyField('parts.Part', through='RepairReportPart')
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    pdf = models.FileField(upload_to='repair_reports/', blank=True, null=True)

    def __str__(self):
        return f"Repair Report for Order #{self.order_id}"

class RepairReportPart(models.Model):
    report = models.ForeignKey(RepairReport, on_delete=models.CASCADE)
    part = models.ForeignKey('parts.Part', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def line_total(self):
        return self.price * self.quantity
