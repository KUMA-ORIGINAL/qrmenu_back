from django.db import models

from app.account.models import Venue
from . import Category


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='products')
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
