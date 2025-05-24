from django.db import models

from services.model import BaseModel


class OrderProduct(BaseModel):
    order = models.ForeignKey(
        'Order', related_name='order_products', on_delete=models.CASCADE, verbose_name="Заказ"
    )
    product = models.ForeignKey(
        'menu.Product', related_name='order_products', on_delete=models.CASCADE, verbose_name="Продукт"
    )
    count = models.PositiveIntegerField(
        default=1, verbose_name="Количество"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Цена за единицу"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Общая цена"
    )
    modificator = models.ForeignKey(
        'menu.Modificator', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Модификатор"
    )
    product_attributes = models.ManyToManyField(
        'menu.ProductAttribute', blank=True, verbose_name="Атрибуты Продукта"
    )

    def __str__(self):
        return f'{self.product.product_name}'

    class Meta:
        verbose_name = "Продукт в заказе"
        verbose_name_plural = "Продукты в заказах"
