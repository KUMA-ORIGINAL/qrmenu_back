from django.db import models

from services.model import BaseModel


class ServiceMode(models.IntegerChoices):
    ON_SITE = 1, 'На месте'
    PICKUP = 2, 'Самовывоз'
    DELIVERY = 3, 'Доставка'


class OrderStatus(models.IntegerChoices):
    NEW = 0, 'Новый'  # Новый заказ
    ACCEPTED = 1, 'Принят'  # Принят
    CANCELLED = 7, 'Отменён'  # Отменён


class Order(BaseModel):
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
    total_price = models.BigIntegerField(
        default=0, verbose_name="Итоговая цена"
    )
    service_price = models.BigIntegerField(
        default=0, verbose_name="Цена за обслуживание"
    )
    tips_price = models.BigIntegerField(
        default=0, verbose_name="Чаевые"
    )
    discount = models.PositiveIntegerField(
        default=0, verbose_name="скидка в %"
    )
    bonus = models.PositiveIntegerField(
        default=0, verbose_name='Бонусы'
    )
    spot = models.ForeignKey(
        'venues.Spot', on_delete=models.SET_NULL, related_name='orders',
        null=True, blank=True,
        verbose_name="Точка заведения")
    table = models.ForeignKey(
        'venues.Table', on_delete=models.SET_NULL, related_name='orders',
        null=True, blank=True,
        verbose_name="Стол"
    )
    venue = models.ForeignKey(
        'venues.Venue', on_delete=models.CASCADE, related_name='orders',
        verbose_name="Заведение"
    )
    client = models.ForeignKey(
        'Client', on_delete=models.CASCADE, related_name='orders', null=True,
        verbose_name="Клиент"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f'Order {self.id} for {self.phone}'

    def calculate_total_price(self):
        """Подсчитывает общую стоимость заказа и сохраняет ее."""
        total = sum(order_product.total_price for order_product in self.order_products.all())
        total += self.service_price
        self.total_price = total
        self.save()
