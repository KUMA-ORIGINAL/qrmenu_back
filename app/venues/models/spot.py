from django.db import models


class Spot(models.Model):
    external_id = models.CharField(max_length=100, verbose_name="Внешний ID точки")
    name = models.CharField(max_length=100, verbose_name="Название заведения")
    address = models.CharField(max_length=255, verbose_name="Адрес заведения", blank=True, null=True)
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, related_name='spots')

    def __str__(self):
        return self.name
