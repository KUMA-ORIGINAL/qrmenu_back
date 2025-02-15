from django.db import models

from services.model import BaseModel


class Category(BaseModel):
    external_id = models.CharField(max_length=100, blank=True, verbose_name="Внешний ID товара")
    category_name = models.CharField(max_length=255, verbose_name="Название категории")
    category_photo = models.ImageField(upload_to='menu/category/%Y/%m', verbose_name="Фото категории",
                                       null=True, blank=True)
    category_hidden = models.BooleanField(default=False, verbose_name="Скрыт?",)
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, related_name='categories',
                              verbose_name="Заведение")

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        indexes = [
            models.Index(fields=['venue',]),
        ]
