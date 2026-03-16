from django.db import models

class PaymentReceipt(models.Model):
    payment = models.OneToOneField('payments.Payment', on_delete=models.CASCADE, related_name='receipt')
    created_at = models.DateTimeField(auto_now_add=True)
    pdf = models.FileField(upload_to='receipts/', blank=True, null=True)

    def __str__(self):
        return f"Receipt for Payment #{self.payment_id}"
