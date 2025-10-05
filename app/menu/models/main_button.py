from django.core.exceptions import ValidationError
from django.db import models


class MainButton(models.Model):
    BUTTON_TYPE_CHOICES = (
        ('section', 'Раздел'),
        ('category', 'Категория'),
    )

    button_type = models.CharField('Тип кнопки', max_length=20, choices=BUTTON_TYPE_CHOICES)
    order = models.PositiveSmallIntegerField(
        verbose_name="Порядок кнопки",
        help_text="Номер кнопки от 1 до 5",
        choices=[(i, f"Кнопка {i}") for i in range(1, 6)],
        unique=False
    )
    section = models.ForeignKey(
        'Section',
        verbose_name='Связанный раздел',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='main_buttons'
    )
    category = models.ForeignKey(
        'Category',
        verbose_name='Связанная категория',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='main_buttons'
    )
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, related_name='main_buttons')

    class Meta:
        ordering = ['order']
        unique_together = ('venue', 'order')
        verbose_name = "Главная кнопка"
        verbose_name_plural = "Главные кнопки"

    def __str__(self):
        return f"{self.order} ({self.venue})"

    def clean(self):
        # Проверяем, чтобы не было больше 5 кнопок для одного заведения
        existing_count = MainButton.objects.filter(venue=self.venue).exclude(pk=self.pk).count()
        if existing_count >= 5 and not self.pk:
            raise ValidationError("Нельзя добавить больше 5 кнопок для одного заведения!")

    def save(self, *args, **kwargs):
        self.full_clean()  # Валидация перед сохранением
        super().save(*args, **kwargs)
