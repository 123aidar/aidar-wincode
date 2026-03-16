from django.db import models


class Client(models.Model):
    """Client / vehicle owner."""
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.phone})"

    @property
    def total_orders(self):
        return self.orders.count()

    @property
    def total_spent(self):
        return sum(o.total_price for o in self.orders.filter(status='completed')) or 0
