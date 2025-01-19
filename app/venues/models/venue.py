from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Venue(models.Model):
    account_number = models.CharField(max_length=100, unique=True)
    access_token = models.CharField(max_length=255)
    owner_id = models.PositiveIntegerField()
    owner_name = models.CharField(max_length=100)
    owner_email = models.EmailField()
    owner_phone = models.CharField(max_length=20, blank=True, null=True)

    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)

    tariff_key = models.CharField(max_length=100, blank=True, null=True)
    tariff_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    next_pay_date = models.DateTimeField(blank=True, null=True)

    pos_system = models.ForeignKey('POSSystem', on_delete=models.CASCADE, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.company_name} - {self.owner_name}'
