from django.db import models


class Category(models.Model):
    external_id = models.CharField(max_length=100, verbose_name="Внешний ID товара")
    category_name = models.CharField(max_length=255, verbose_name="Название категории")
    category_photo = models.ImageField(upload_to='menu/category/', verbose_name="Фото категории",
                                       null=True, blank=True)
    category_hidden = models.BooleanField(default=False, verbose_name="Скрыта ли категория",)
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, related_name='categories',
                              verbose_name="Заведение")
    pos_system = models.ForeignKey('venues.POSSystem', on_delete=models.CASCADE,
                                   verbose_name="POS система")


    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        indexes = [
            models.Index(fields=['venue',]),
        ]
