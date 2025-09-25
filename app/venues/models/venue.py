from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill
from unidecode import unidecode

from services.model import BaseModel
from .work_schedule import WorkSchedule

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
        ('#000000', 'Черный'),
        ('#00BFB2', 'Бирюзовый')
    ]

    company_name = models.CharField(max_length=100, verbose_name="Название компании")
    slug = models.SlugField(unique=True, verbose_name='Название ссылки', blank=True)
    color_theme = models.CharField(
        'Тема',
        max_length=7,
        choices=COLOR_CHOICES,
        default='#008B68',
        blank=True,
    )
    logo = ProcessedImageField(
        upload_to='venue_logo',
        processors=[ResizeToFill(44, 44)],
        format='PNG',
        options={'quality': 80},
        null=True,
        blank=True,
        verbose_name='Логотип',
    )
    account_number = models.CharField(max_length=100, verbose_name="Номер аккаунта", blank=True)
    access_token = models.CharField(max_length=255, verbose_name="Токен доступа для POS-системы", blank=True, null=True)

    # Владельцы
    owner_id = models.PositiveIntegerField(verbose_name="ID владельца", blank=True, null=True)
    owner_name = models.CharField(max_length=100, verbose_name="Имя владельца", blank=True)
    owner_email = models.EmailField(verbose_name="Электронная почта владельца")
    owner_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон владельца")

    # Местоположение
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    country = models.CharField(max_length=100, verbose_name="Страна")

    # 🔹 Разные проценты обслуживания по режимам
    delivery_service_fee_percent = models.PositiveIntegerField(
        default=0, verbose_name="Процент за обслуживание (доставка)"
    )
    takeout_service_fee_percent = models.PositiveIntegerField(
        default=0, verbose_name="Процент за обслуживание (самовывоз)"
    )
    dinein_service_fee_percent = models.PositiveIntegerField(
        default=0, verbose_name="Процент за обслуживание (на месте)"
    )

    # Тарифы
    tariff_key = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ключ тарифа")
    tariff_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Цена тарифа")
    next_pay_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата следующей оплаты")
    pos_system = models.ForeignKey('POSSystem', on_delete=models.CASCADE, blank=True, null=True, verbose_name="POS система")

    # Режимы доступности
    is_delivery_available = models.BooleanField(default=True, verbose_name="Доставка доступна")
    is_takeout_available = models.BooleanField(default=True, verbose_name="Самовывоз доступен")
    is_dinein_available = models.BooleanField(default=True, verbose_name="Обслуживание на месте доступно")

    # Доставка
    default_delivery_spot = models.ForeignKey(
        'Spot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_for_venue',
        verbose_name="Точка доставки по умолчанию"
    )
    delivery_fixed_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                             verbose_name="Стоимость доставки (фиксированная)")
    delivery_free_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                             verbose_name="Бесплатная доставка от суммы")

    # Бонусная система
    is_bonus_system_enabled = models.BooleanField(default=False, verbose_name="Бонусная система включена")
    bonus_accrual_percent = models.PositiveIntegerField(default=0, verbose_name="Процент начисления бонусов")

    # Описание
    terms = models.TextField(blank=True, null=True, verbose_name="Условия заведения")
    description = models.TextField(blank=True, null=True, verbose_name="Описание заведения")

    def __str__(self):
        return f'{self.company_name}'

    class Meta:
        verbose_name = "Заведение"
        verbose_name_plural = "Заведения"

    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(self.company_name)).lower()
        super().save(*args, **kwargs)

        # Автогенерация расписания
        existing_days = set(self.schedules.values_list("day_of_week", flat=True))
        all_days = set(val for val, _ in WorkSchedule.WeekDay.choices)

        missing_days = all_days - existing_days
        for day_val in missing_days:
            WorkSchedule.objects.create(
                venue=self,
                day_of_week=day_val,
                is_day_off=True,
            )
