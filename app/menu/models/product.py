from django.db import models
from imagekit.models import ProcessedImageField, ImageSpecField
from pilkit.processors import ResizeToFill

from services.model import BaseModel


class Product(BaseModel):
    external_id = models.CharField(max_length=100, blank=True, verbose_name="Внешний ID товара")
    product_name = models.CharField(max_length=255, verbose_name="Название товара")
    product_description = models.TextField(blank=True, null=True, verbose_name="Описание товара")
    product_photo = models.ImageField(
        upload_to='menu/products/%Y/%m',
        blank=True, null=True,
        verbose_name="Оригинальное фото товара"
    )
    product_photo_small = ImageSpecField(
        source='product_photo',
        processors=[ResizeToFill(182, 136)],
        format='JPEG',
        options={'quality': 80}
    )
    product_photo_large = ImageSpecField(
        source='product_photo',
        processors=[ResizeToFill(600, 450)],
        format='JPEG',
        options={'quality': 85}
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
