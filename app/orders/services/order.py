from datetime import datetime, time


def is_within_schedule(work_start: time, work_end: time, check_time: time = None) -> bool:
    if not work_start or not work_end:
        return False

    now = check_time or datetime.now().time()

    if work_start < work_end:
        return work_start <= now <= work_end
    else:
        # График с переходом через полночь (например, 22:00–06:00)
        return now >= work_start or now <= work_end
