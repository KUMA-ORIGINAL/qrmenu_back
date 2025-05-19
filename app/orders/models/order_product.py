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

    def get_total_price(self):
        """Рассчитывает общую цену с учетом модификатора, атрибутов и количества."""
        base_price = self.get_price()
        total_price = base_price * self.count
        return total_price

    def get_price(self):
        """
        Рассчитывает цену продукта с учетом модификатора и атрибутов.
        Если есть модификатор, используется его цена, иначе — цена продукта.
        Добавляется цена атрибутов.
        """
        # Определяем базовую цену (либо от модификатора, либо от продукта)
        if self.modificator:
            base_price = self.modificator.price
        else:
            base_price = self.product.product_price
        final_price = base_price

        return final_price

    def save(self, *args, **kwargs):
        """Перед сохранением пересчитываем цену и общую цену."""
        self.price = self.get_price()  # Цена за единицу с учетом атрибутов
        self.total_price = self.get_total_price()  # Общая цена
        super().save(*args, **kwargs)
        self.order.calculate_total_price()  # Пересчитываем цену заказа
