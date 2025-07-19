from django.db import models

from services.model import BaseModel


class ServiceMode(models.IntegerChoices):
    ON_SITE = 1, 'На месте'
    PICKUP = 2, 'Самовывоз'
    DELIVERY = 3, 'Доставка'


class OrderStatus(models.IntegerChoices):
    NEW = 0, 'Заказ оформлен'
    ACCEPTED = 1, 'Готовим заказ'
    READY = 2, 'Заказ готов'
    COMPLETED = 3, 'Заказ выполнен'
    WAITING_FOR_PAYMENT = 4, 'Ожидает оплату'
    CANCELLED = 7, 'Отменён'


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
        default=OrderStatus.WAITING_FOR_PAYMENT,
        verbose_name="Статус заказа"
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Адрес"
    )
    total_price = models.DecimalField(
        max_digits=10,  # всего до 10 цифр (включая до и после запятой)
        decimal_places=2,  # 2 знака после запятой (например: 12345.67)
        default=0,
        verbose_name="Итоговая цена"
    )
    service_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
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

    is_tg_bot = models.BooleanField('Из телеграмм бота', default=False)
    tg_redirect_url = models.URLField('Редирект url бота', blank=True, null=True)

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
