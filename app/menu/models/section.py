from django.db import models
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill, ResizeToFit

from services.model import BaseModel


class Section(BaseModel):
    name = models.CharField(
        'Название',
        max_length=255
    )
    photo = models.ImageField(
        upload_to='menu/section/%Y/%m',
        verbose_name="Фото",
        null=True, blank=True
    )
    photo_small = ImageSpecField(
        source='photo',
        processors=[ResizeToFit(400, 400)],
        format='PNG',
        options={'quality': 50}
    )
    venue = models.ForeignKey(
        'venues.Venue',
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name="Заведение",
        db_index=True
    )
    categories = models.ManyToManyField(
        'Category',
        related_name='sections',
        verbose_name='Категории'
    )

    def __str__(self):
        return f"{self.venue} — {self.name}"
