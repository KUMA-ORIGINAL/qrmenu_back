from django.db import models

from services.model import BaseModel


class ReceiptPrinter(BaseModel):
    name = models.CharField(max_length=100, verbose_name='Название принтера')
    printer_id = models.CharField(max_length=255, verbose_name='ID принтера')
    topic = models.CharField(max_length=255, verbose_name='Топик')
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, related_name='receipt_printers',
                              verbose_name="Заведение")

    class Meta:
        verbose_name = 'Принтер для чека'
        verbose_name_plural = 'Принтеры для чека'

    def __str__(self):
        return self.name
