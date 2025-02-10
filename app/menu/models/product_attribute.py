from django.db import models

from services.model import BaseModel


class ProductAttribute(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Название атрибута')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Цена')
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE, related_name='product_attributes',
        verbose_name="Товар"
    )

    class Meta:
        verbose_name = 'Атрибут продукта'
        verbose_name_plural = 'Атрибуты продукта'

    def __str__(self):
        return self.name
