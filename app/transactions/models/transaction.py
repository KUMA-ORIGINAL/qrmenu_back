from django.db import models

from services.model import BaseModel


class Transaction(BaseModel):
    total_price = models.PositiveIntegerField(verbose_name="Общая сумма", default=0)
    status = models.CharField(
        max_length=50,
        choices=[('success', 'Оплачено'), ('pending', 'В ожидании'), ('failed', 'Не удалось')],
        verbose_name="Статус оплаты"
    )
    json_data = models.JSONField(blank=True, null=True, verbose_name='Ответ из платежной системы')

    order = models.ForeignKey('orders.Order', models.PROTECT, verbose_name='Заказ',
                              related_name='transactions', null=True, blank=True)

    def __str__(self):
        return f"Транзакция {self.id}"

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        ordering = ['-created_at']
