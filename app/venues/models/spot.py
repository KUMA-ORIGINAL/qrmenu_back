from django.db import models

from services.model import BaseModel


class Spot(BaseModel):
    external_id = models.CharField(max_length=100, blank=True, verbose_name="Внешний ID точки")
    name = models.CharField(max_length=100, verbose_name="Название заведения")
    address = models.CharField(max_length=255, verbose_name="Адрес заведения",
                               blank=True, null=True)
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, related_name='spots',
                              verbose_name="Заведение")

    def __str__(self):
        return self.name
