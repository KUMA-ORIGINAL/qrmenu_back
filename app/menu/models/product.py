from django.db import models
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill

from services.model import BaseModel


class Product(BaseModel):
    external_id = models.CharField(max_length=100, blank=True, verbose_name="Внешний ID товара")
    product_name = models.CharField(max_length=255, verbose_name="Название товара")
    product_description = models.TextField(blank=True, null=True, verbose_name="Описание товара")
    product_photo = ProcessedImageField(
        upload_to='menu/products/%Y/%m',
        processors=[ResizeToFill(182, 136)],
        format='JPEG',
        options={'quality': 80},
        blank=True, null=True,
        verbose_name="Фото товара"
    )
    product_price = models.BigIntegerField( blank=True, default=0,
                                        verbose_name="Цена товара")
    weight = models.PositiveSmallIntegerField(default=0, verbose_name='Вес товара')
    is_recommended = models.BooleanField(default=False, verbose_name='Рекомендован?')
    hidden = models.BooleanField(default=False, verbose_name="Скрыт?")

    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products',
                                 verbose_name="Категория")
    spots = models.ManyToManyField('venues.Spot', related_name='products',
                                   verbose_name="Точки заведения")
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, related_name='products',
                              verbose_name="Заведение")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['product_name']

    def __str__(self):
        return self.product_name
