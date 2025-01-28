from django.db import models

from services.model import BaseModel


class Hall(BaseModel):
    external_id = models.CharField(max_length=100, blank=True, verbose_name="Внешний ID зала")
    hall_name = models.CharField(max_length=255, verbose_name="Название зала")  # Название зала
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, related_name='halls',
                              verbose_name="Заведение")
    spot = models.ForeignKey('Spot', on_delete=models.CASCADE, related_name='halls',
                             verbose_name="Точка заведения")

    class Meta:
        verbose_name = "Зал"
        verbose_name_plural = "Залы"

    def __str__(self):
        return self.hall_name
