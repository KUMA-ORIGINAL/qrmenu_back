from django.db import models


class Client(models.Model):
    firstname = models.CharField(max_length=100, blank=True, null=True)
    lastname = models.CharField(max_length=100, blank=True, null=True)
    patronymic = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    client_sex = models.PositiveSmallIntegerField(choices=[(0, 'Male'), (1, 'Female')], default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_payed_sum = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.firstname} {self.lastname} - {self.phone}'
