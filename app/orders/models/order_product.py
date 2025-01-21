from django.db import models


class OrderProduct(models.Model):
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
        max_digits=10, decimal_places=2, default=0, verbose_name="Цена за единицу"
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Общая цена"
    )
    modificator = models.ForeignKey(
        'menu.Modificator', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Модификатор"
    )

    def __str__(self):
        return f'{self.product.product_name}'

    class Meta:
        verbose_name = "Продукт в заказе"
        verbose_name_plural = "Продукты в заказах"


    def get_total_price(self):
        if self.modificator:
            total_price = self.modificator.price * self.count
        else:
            total_price = self.product.product_price * self.count
        return total_price

    def get_price(self):
        if self.modificator:
            price = self.modificator.price
        else:
            price = self.product.product_price
        return price

    def save(self, *args, **kwargs):
        self.price = self.get_price()
        self.total_price = self.get_total_price()
        super().save(*args, **kwargs)
        self.order.calculate_total_price()
