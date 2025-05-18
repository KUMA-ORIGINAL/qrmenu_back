from django.db import models


class PaymentAccount(models.Model):
    PAYMENT_SERVICE_CHOICES = [
        ('bakai', 'Bakai bank'),
    ]

    service = models.CharField('Сервис', max_length=50, choices=PAYMENT_SERVICE_CHOICES)
    name = models.CharField(max_length=100, help_text="Название или описание аккаунта", blank=True, null=True)
    token = models.TextField(help_text="Секретный платёжный токен/API ключ")
    venue = models.ForeignKey(
        'venues.Venue', on_delete=models.CASCADE, related_name='payment_accounts',
        verbose_name="Заведение"
    )

    class Meta:
        verbose_name = "Платёжный аккаунт"
        verbose_name_plural = "Платёжные аккаунты"

    def __str__(self):
        return f"{self.service.upper()} — {self.name}"
