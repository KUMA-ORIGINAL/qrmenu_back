from django.db import models


class Table(models.Model):
    external_id = models.CharField(
        max_length=100, blank=True, verbose_name="Внешний ID стола"
    )
    table_num = models.CharField(
        max_length=255, verbose_name="Номер стола"
    )
    table_title = models.CharField(
        max_length=255, verbose_name="Название стола"
    )
    table_shape = models.CharField(
        max_length=50, choices=[('square', 'Квадратный'), ('circle', 'Круглый')],
        verbose_name="Форма стола"
    )
    venue = models.ForeignKey(
        'Venue', on_delete=models.CASCADE, related_name='tables',
        verbose_name="Заведение"
    )
    spot = models.ForeignKey(
        'Spot', on_delete=models.CASCADE, related_name='tables',
        blank=True, null=True, verbose_name="Точка заведения"
    )

    def __str__(self):
        return f"Стол {self.table_num} ({self.table_title})"

    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"
