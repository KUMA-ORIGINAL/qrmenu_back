from django.db import models

class ServiceMode(models.IntegerChoices):
    ON_SITE = 1, 'На месте'
    PICKUP = 2, 'Самовывоз'
    DELIVERY = 3, 'Доставка'

class OrderStatus(models.IntegerChoices):
    NEW = 0, 'Новый'  # Новый заказ
    ACCEPTED = 1, 'Принят'  # Принят
    CANCELLED = 7, 'Отменён'  # Отменён


class Order(models.Model):
    external_id = models.CharField(
        max_length=100, verbose_name="Внешний ID онлайн-заказа"
    )
    phone = models.CharField(
        max_length=20, verbose_name="Телефон клиента"
    )
    comment = models.TextField(
        blank=True, null=True, verbose_name="Комментарий"
    )
    service_mode = models.PositiveSmallIntegerField(
        choices=ServiceMode.choices,
        default=ServiceMode.ON_SITE,
        verbose_name="Режим обслуживания"
    )
    status = models.PositiveSmallIntegerField(
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        verbose_name="Статус заказа"
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Итоговая цена"
    )
    service_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Цена за обслуживание"
    )
    tips_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Чаевые"
    )
    discount = models.PositiveIntegerField(
        default=0, verbose_name="скидка в %"
    )
    bonus = models.PositiveIntegerField(
        default=0, verbose_name='Бонусы'
    )
    venue = models.ForeignKey(
        'venues.Venue', on_delete=models.CASCADE, related_name='orders',
        verbose_name="Заведение"
    )
    table = models.ForeignKey(
        'venues.Table', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders',
        verbose_name="Стол"
    )
    client = models.ForeignKey(
        'Client', on_delete=models.CASCADE, related_name='orders', null=True,
        verbose_name="Клиент"
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f'Order {self.id} for {self.phone}'

    def calculate_total_price(self):
        """Подсчитывает общую стоимость заказа и сохраняет ее."""
        total = sum(order_product.total_price for order_product in self.order_products.all())
        self.total_price = total
        self.save()