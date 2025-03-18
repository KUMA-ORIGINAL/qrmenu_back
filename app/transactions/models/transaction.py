from django.db import models

from services.model import BaseModel


class Transaction(BaseModel):
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")
    external_id = models.BigIntegerField(null=True, blank=True, verbose_name='ID транзакции от платежного сервиса')
    transaction_link = models.URLField(blank=True, null=True, verbose_name='Ссылка на страницу платежа')
    pay_method = models.CharField(
        max_length=50,
        choices=[('cash', 'Наличные'), ('bakai_bank', 'Bakai Bank')],
        verbose_name="Способ оплаты"
    )
    status = models.CharField(
        max_length=50,
        choices=[('paid', 'Оплачено'), ('pending', 'В ожидании'), ('failed', 'Не удалось')],
        verbose_name="Статус оплаты"
    )
    json_data = models.JSONField(blank=True, null=True, verbose_name='Ответ из платежной системы')

    def __str__(self):
        return f"Транзакция {self.id}"

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        ordering = ['-created_at']  # Упорядочивание по дате транзакции (от новых к старым)