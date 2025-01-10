from django.db import models


class Modificator(models.Model):
    external_id = models.CharField(max_length=100, verbose_name="Внешний ID товара")
    modificator_name = models.CharField(max_length=255)
    modificator_selfprice = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.modificator_name
