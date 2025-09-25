from django.db import models

from services.model import BaseModel


class Spot(BaseModel):
    external_id = models.CharField(max_length=100, blank=True, verbose_name="Внешний ID точки")
    name = models.CharField(max_length=100, verbose_name="Название заведения")
    address = models.CharField(max_length=255, verbose_name="Адрес заведения",
                               blank=True, null=True)
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, related_name='spots',
                              verbose_name="Заведение")
    is_hidden = models.BooleanField(default=False, verbose_name="Скрыт?")

    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID Telegram-группы")

    class Meta:
        verbose_name = "Точка заведения"
        verbose_name_plural = "Точки заведения"

    def __str__(self):
        return self.name
