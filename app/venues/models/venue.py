from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Venue(models.Model):
    account_number = models.CharField(
        max_length=100, unique=True, verbose_name="Номер аккаунта"
    )
    access_token = models.CharField(
        max_length=255, verbose_name="Токен доступа"
    )
    owner_id = models.PositiveIntegerField(
        verbose_name="ID владельца"
    )
    owner_name = models.CharField(
        max_length=100, verbose_name="Имя владельца"
    )
    owner_email = models.EmailField(
        verbose_name="Электронная почта владельца"
    )
    owner_phone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Телефон владельца"
    )

    city = models.CharField(
        max_length=100, blank=True, verbose_name="Город"
    )
    country = models.CharField(
        max_length=100, verbose_name="Страна"
    )
    company_name = models.CharField(
        max_length=100, verbose_name="Название компании"
    )
    tip_amount = models.PositiveIntegerField(default=0, verbose_name="Процент за обслуживание")

    tariff_key = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Ключ тарифа"
    )
    tariff_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Цена тарифа"
    )
    next_pay_date = models.DateTimeField(
        blank=True, null=True, verbose_name="Дата следующей оплаты"
    )

    pos_system = models.ForeignKey(
        'POSSystem', on_delete=models.CASCADE, blank=True, null=True, verbose_name="POS система"
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Пользователь"
    )

    def __str__(self):
        return f'{self.company_name} - {self.owner_name}'

    class Meta:
        verbose_name = "Заведение"
        verbose_name_plural = "Заведения"

