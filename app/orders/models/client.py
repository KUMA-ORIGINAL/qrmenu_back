from django.db import models

from services.model import BaseModel


class Client(BaseModel):
    external_id = models.CharField(
        max_length=100, blank=True, verbose_name="Внешний ID клиента"
    )
    firstname = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Имя"
    )
    lastname = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Фамилия"
    )
    patronymic = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Отчество"
    )
    phone = models.CharField(
        max_length=20, verbose_name="Телефон"
    )
    phone_number = models.CharField(
        max_length=20, verbose_name="Номер телефона"
    )
    email = models.EmailField(
        blank=True, null=True, verbose_name="Электронная почта"
    )
    birthday = models.DateField(
        blank=True, null=True, verbose_name="Дата рождения"
    )
    client_sex = models.PositiveSmallIntegerField(
        choices=[(0, 'Мужской'), (1, 'Женский')], default=0, verbose_name="Пол"
    )
    bonus = models.PositiveIntegerField(default=0, verbose_name='Бонусы')
    total_payed_sum = models.PositiveIntegerField(
        default=0, verbose_name="Общая сумма платежей"
    )
    country = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Страна"
    )
    city = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Город"
    )
    address = models.TextField(
        blank=True, null=True, verbose_name="Адрес"
    )
    venue = models.ForeignKey(
        'venues.Venue', on_delete=models.CASCADE, related_name='clients',
        verbose_name="Заведение"
    )

    def __str__(self):
        return f'{self.firstname} {self.lastname} - {self.phone}'

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        unique_together = ('venue', 'phone')
