from django.db import models
from django.utils.translation import gettext_lazy as _


class BonusHistory(models.Model):
    class Operation(models.TextChoices):
        ACCRUAL = "accrual", _("Начисление")
        WRITE_OFF = "write_off", _("Списание")

    client = models.ForeignKey(
        "Client",
        on_delete=models.CASCADE,
        related_name="bonus_history",
        verbose_name=_("Клиент")
    )
    order = models.ForeignKey(
        "Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Заказ")
    )
    amount = models.IntegerField(
        verbose_name=_("Сумма бонусов"),
        help_text=_("Положительное = начисление, отрицательное = списание")
    )
    operation = models.CharField(
        max_length=20,
        choices=Operation.choices,
        verbose_name=_("Операция")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата и время")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Описание"),
        help_text=_("Причина начисления или списания")
    )

    class Meta:
        verbose_name = _("История бонуса")
        verbose_name_plural = _("История бонусов")
        ordering = ["-created_at"]

    def __str__(self):
        sign = "+" if self.amount > 0 else ""
        return f"{self.client.phone_number}: {sign}{self.amount} ({self.get_operation_display()})"