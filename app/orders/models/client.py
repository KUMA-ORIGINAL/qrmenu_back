from django.db import models


class Client(models.Model):
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
        max_length=20, unique=True, verbose_name="Телефон"
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
    bonus = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Бонусы"
    )
    total_payed_sum = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Общая сумма платежей"
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
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления"
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
