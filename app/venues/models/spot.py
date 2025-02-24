from django.db import models
from django.utils.text import slugify
from unidecode import unidecode

from services.model import BaseModel


class Spot(BaseModel):
    external_id = models.CharField(max_length=100, blank=True, verbose_name="Внешний ID точки")
    name = models.CharField(max_length=100, verbose_name="Название заведения")
    slug = models.SlugField(verbose_name='Название ссылки', blank=True)
    address = models.CharField(max_length=255, verbose_name="Адрес заведения",
                               blank=True, null=True)
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, related_name='spots',
                              verbose_name="Заведение")

    class Meta:
        verbose_name = "Точка заведения"
        verbose_name_plural = "Точки заведения"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)
