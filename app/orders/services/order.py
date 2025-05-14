from datetime import datetime, time


def is_within_schedule(schedule_str: str) -> bool:
    """Проверяет, входит ли текущее время в график работы."""
    try:
        start_str, end_str = schedule_str.split('-')
        start_time = datetime.strptime(start_str.strip(), "%H:%M").time()
        end_time = datetime.strptime(end_str.strip(), "%H:%M").time()
        now = datetime.now().time()

        if start_time < end_time:
            return start_time <= now <= end_time
        else:
            # Обработка случая, если график пересекает полночь (например, 22:00-06:00)
            return now >= start_time or now <= end_time
    except Exception as e:
        # В случае ошибки считаем, что график некорректен
        return False
