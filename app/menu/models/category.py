from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    category_id = models.CharField(max_length=100, verbose_name="ID категории",
                                   blank=True)
    category_name = models.CharField(max_length=255, verbose_name="Название категории")
    category_photo = models.ImageField(upload_to='menu/category/', verbose_name="Фото категории",
                                       null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='subcategories',
                                     verbose_name="Родительская категория")
    category_hidden = models.BooleanField(default=False, verbose_name="Скрыта ли категория")
    level = models.PositiveIntegerField(default=1, verbose_name="Уровень категории")
    visible = models.JSONField(default=list, verbose_name="Видимость категории на точках", blank=True)
    venue = models.ForeignKey('account.Venue', on_delete=models.CASCADE, related_name='categories',
                              verbose_name="Заведение")


    def __str__(self):
        return self.category_name

    def get_children_categories(self):
        """
        Возвращает подкатегории текущей категории.
        """
        return self.get_children()

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        indexes = [
            models.Index(fields=['venue',]),
        ]

