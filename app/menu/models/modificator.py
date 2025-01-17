from django.db import models


class Modificator(models.Model):
    external_id = models.CharField(max_length=100, verbose_name="Внешний ID товара")
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='modificators',
                              verbose_name="Товар")

    def __str__(self):
        return self.name
