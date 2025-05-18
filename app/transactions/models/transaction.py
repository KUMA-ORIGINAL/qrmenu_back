from django.db import models

from services.model import BaseModel


class Transaction(BaseModel):
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Итоговая цена"
    )
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
