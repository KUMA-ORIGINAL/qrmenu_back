from django.db import models

from services.model import BaseModel


class Modificator(BaseModel):
    external_id = models.CharField(
        max_length=100, verbose_name="Внешний ID модификатора"
    )
    name = models.CharField(
        max_length=255, verbose_name="Название модификатора"
    )
    price = models.BigIntegerField(
        default=0, verbose_name="Цена"
    )
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE, related_name='modificators',
        verbose_name="Товар"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Модификатор"
        verbose_name_plural = "Модификаторы"

