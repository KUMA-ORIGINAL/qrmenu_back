from django.db import models


class WorkSchedule(models.Model):
    class WeekDay(models.IntegerChoices):
        MONDAY = 1, "Понедельник"
        TUESDAY = 2, "Вторник"
        WEDNESDAY = 3, "Среда"
        THURSDAY = 4, "Четверг"
        FRIDAY = 5, "Пятница"
        SATURDAY = 6, "Суббота"
        SUNDAY = 7, "Воскресенье"

    venue = models.ForeignKey(
        "Venue", related_name="schedules", on_delete=models.CASCADE
    )
    day_of_week = models.PositiveSmallIntegerField(
        choices=WeekDay.choices, verbose_name="День недели"
    )
    work_start = models.TimeField(verbose_name="Начало рабочего дня", null=True, blank=True)
    work_end = models.TimeField(verbose_name="Конец рабочего дня", null=True, blank=True)
    is_day_off = models.BooleanField(default=False, verbose_name="Выходной")
    is_24h = models.BooleanField("Круглосуточно", default=False)

    class Meta:
        verbose_name = "График работы"
        verbose_name_plural = "Графики работы"
        unique_together = ("venue", "day_of_week")
        ordering = ("day_of_week",)

    def __str__(self):
        return ''
