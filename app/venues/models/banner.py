from django.db import models

from services.model import BaseModel


class Banner(BaseModel):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('inactive', 'Неактивен'),
        ('draft', 'Черновик'),
    ]

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    banner = models.ImageField(upload_to='banners/%Y/%m/', verbose_name='Баннер')
    image = models.ImageField(upload_to='banner-images/%Y/%m/', verbose_name='Картинка')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    url = models.URLField(verbose_name='Ссылка', blank=True, null=True)
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, related_name='banners',
                              verbose_name="Заведение")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Рекламный баннер'
        verbose_name_plural = 'Рекламные баннеры'
