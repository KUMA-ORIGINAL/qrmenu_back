from datetime import datetime, time


def is_within_schedule(venue) -> bool:
    """
    Проверяем доступность заведения.
    - Если venue.is_24h == True → работает всегда.
    - Если расписания для сегодняшнего дня нет → работает с 09:00 до 18:00.
    - Если is_day_off=True → не работает.
    - Поддержка смен, которые переходят через полночь (например, 22:00–06:00).
    """

    now = datetime.now().time()
    weekday = datetime.now().isoweekday()  # 1=Пн ... 7=Вс

    # 2. Ищем расписание
    schedule = venue.schedules.filter(day_of_week=weekday).first()

    if getattr(schedule, "is_24h", False):
        return True

    if not schedule:
        work_start, work_end = time(9, 0), time(18, 0)
    else:
        if schedule.is_day_off:
            return False
        work_start, work_end = schedule.work_start, schedule.work_end

    # 3. Проверяем диапазон времени
    if work_start < work_end:
        # обычный промежуток в рамках одного дня
        return work_start <= now <= work_end
    else:
        # ночная смена (например, 22:00–06:00)
        return now >= work_start or now <= work_end