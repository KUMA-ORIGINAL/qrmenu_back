from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from unidecode import unidecode

from services.model import BaseModel

User = get_user_model()


class Venue(BaseModel):
    COLOR_CHOICES = [
        ('#008B68', 'Темно-зеленый'),
        ('#FFB200', 'Янтарный'),
        ('#F80101', 'Алый'),
        ('#FF4800', 'Оранжевый'),
        ('#00BBFF', 'Голубой'),
        ('#0717FF', 'Синий'),
        ('#AF00A3', 'Розовый'),
    ]
    company_name = models.CharField(
        max_length=100, verbose_name="Название компании"
    )
    slug = models.SlugField(unique=True, verbose_name='Название ссылки', blank=True)
    color_theme = models.CharField(
        max_length=7,
        choices=COLOR_CHOICES,
        default='#008B68'
    )
    logo = models.ImageField(
        upload_to='venue_logo', null=True, blank=True, verbose_name='Логотип')
    schedule = models.CharField(
        max_length=255, verbose_name='График работы',
        help_text="Введите график работы, например: 09:00-18:00",
        default='09:00-18:00'
    )
    account_number = models.CharField(
        max_length=100, unique=True, verbose_name="Номер аккаунта"
    )
    access_token = models.CharField(
        max_length=255, verbose_name="Токен доступа для POS-системы"
    )
    owner_id = models.PositiveIntegerField(
        verbose_name="ID владельца"
    )
    owner_name = models.CharField(
        max_length=100, verbose_name="Имя владельца", blank=True
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
    service_fee_percent = models.PositiveIntegerField(default=0, verbose_name="Процент за обслуживание")

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

    def __str__(self):
        return f'{self.company_name} - {self.owner_name}'

    class Meta:
        verbose_name = "Заведение"
        verbose_name_plural = "Заведения"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.company_name)).upper()
        super().save(*args, **kwargs)
