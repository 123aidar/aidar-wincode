from django.db import models


class Car(models.Model):
    """Vehicle registered in the system."""
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='cars')
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    vin = models.CharField(max_length=17, unique=True, blank=True, verbose_name='VIN')
    license_plate = models.CharField(max_length=20, unique=True)
    color = models.CharField(max_length=50, blank=True)
    mileage = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand} {self.model} ({self.license_plate})"
