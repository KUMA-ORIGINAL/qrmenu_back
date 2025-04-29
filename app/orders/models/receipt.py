from django.db import models

from services.model import BaseModel


class Receipt(BaseModel):
    amount = models.PositiveIntegerField(verbose_name="Сумма")
    order_count = models.PositiveIntegerField(verbose_name="Количество товаров")
    payload = models.JSONField(verbose_name="JSON-данные чека")
    order = models.OneToOneField(
        'Order', on_delete=models.CASCADE, related_name='receipt', verbose_name="Заказ"
    )
    receipt_printer = models.ForeignKey(
        'ReceiptPrinter', on_delete=models.SET_NULL, blank=True, null=True,
        verbose_name="Принтер", related_name="receipts"
    )
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, related_name='receipts',
                              verbose_name="Заведение")

    def __str__(self):
        return f"Чек для заказа #{self.order.id}"

    class Meta:
        verbose_name = "Чек"
        verbose_name_plural = "Чеки"
        ordering = ['-created_at']
