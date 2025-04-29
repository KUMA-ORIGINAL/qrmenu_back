import math
from decimal import Decimal, ROUND_HALF_UP

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
        max_length=100, verbose_name="Внешний ID онлайн-заказа", blank=True, null=True
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
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Адрес"
    )
    total_price = models.PositiveIntegerField(
        default=0,
        verbose_name="Итоговая цена"
    )
    service_price = models.PositiveIntegerField(
        default=0,
        verbose_name="Цена за обслуживание"
    )
    tips_price = models.PositiveIntegerField(
        default=0,
        verbose_name="Чаевые"
    )
    discount = models.PositiveIntegerField(
        default=0, verbose_name="Скидка в %"
    )
    bonus = models.PositiveIntegerField(
        default=0, verbose_name="Бонусы"
    )

    spot = models.ForeignKey(
        'venues.Spot', on_delete=models.SET_NULL, related_name='orders',
        null=True, blank=True,
        verbose_name="Точка заведения"
    )
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
        'Client', on_delete=models.CASCADE, related_name='orders',
        null=True, blank=True,
        verbose_name="Клиент"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.id} for {self.phone}'

    def calculate_total_price(self):
        products_total = sum(
            order_product.total_price for order_product in self.order_products.all()
        )

        service_fee_percent = self.venue.service_fee_percent or 0

        service_price = math.ceil(products_total * service_fee_percent / 100)

        total_price = products_total + service_price

        self.service_price = service_price
        self.total_price = total_price

        self.save()
