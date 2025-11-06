from django.db import models
from django.utils.text import slugify
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFit
from unidecode import unidecode

from services.model import BaseModel


class Category(BaseModel):
    external_id = models.CharField(max_length=100, blank=True, verbose_name="Внешний ID товара")
    category_name = models.CharField(max_length=255, verbose_name="Название категории")
    slug = models.SlugField(
        max_length=255,
        verbose_name="URL слаг",
        help_text="Автоматически генерируется из названия категории",
        blank=True,  # ⬅ временно разрешаем
        null=True  # ⬅ чтобы миграция прошла без ошибок
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок сортировки",
        help_text="Меньшее число → выше в списке",
    )
    category_photo = models.ImageField(
        upload_to='menu/category/%Y/%m',
        verbose_name="Оригинальное фото категории",
        null=True, blank=True
    )
    category_photo_small = ImageSpecField(
        source='category_photo',
        processors=[ResizeToFit(200, 200)],
        format='PNG',
        options={'quality': 90}
    )
    category_hidden = models.BooleanField(
        default=False,
        verbose_name="Скрыт?",
        help_text="При скрытии категории будут скрыты все товары в ней"
    )
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, related_name='categories',
                              verbose_name="Заведение")

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['sort_order']
        indexes = [
            models.Index(fields=['venue',]),
        ]

    def save(self, *args, **kwargs):
        # Генерация slug только если он не задан
        if not self.slug:
            base_slug = slugify(unidecode(self.category_name))
            slug = base_slug
            num = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)
