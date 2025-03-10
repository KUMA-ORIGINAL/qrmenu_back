import json
import random
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from account.models import ROLE_OWNER, ROLE_ADMIN
from orders.models import Order
from venues.models import Venue


def get_last_week_orders_chart(request):
    end_date = timezone.now()
    start_date = end_date - timedelta(days=5)  # Берем последние 7 дней включая сегодняшний

    user = request.user
    if request.user.is_superuser:
        orders_queryset = Order.objects
    elif user.role in (ROLE_OWNER, ROLE_ADMIN):
        orders_queryset = Order.objects.filter(venue=user.venue)

    orders_per_day = (
        orders_queryset.filter(
            created_at__range=(start_date, end_date))
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    # Переводим дни недели на русский
    weekdays_ru = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье"
    }

    # Инициализируем списки для дней недели и количества заказов
    labels = []
    order_counts = []

    # Создаем словарь заказов, чтобы было легче сопоставить даты
    orders_dict = {order['day'].date(): order['count'] for order in orders_per_day}

    # Проходим по последним 7 дням, начиная с сегодняшнего
    for i in range(7):
        current_day = (start_date + timedelta(
            days=i)).date()  # Дни идут от старта до конца (включительно)
        weekday_index = current_day.weekday()  # Получаем индекс дня недели

        labels.append(weekdays_ru[weekday_index])  # День недели на русском
        order_counts.append(
            orders_dict.get(current_day, 0))  # Количество заказов или 0, если данных нет

    # Подготавливаем данные для графика
    chart_data = {
        "labels": labels,  # Дни недели
        "datasets": [{
            "data": order_counts,  # Количество заказов за каждый день
            "borderColor": "#9333ea"
        }]
    }

    # Преобразуем данные в JSON-формат
    chart_json = json.dumps(chart_data)

    # Формируем метрику и футер
    context = {
        "title": _("Количество заказов за последнюю неделю"),  # Заголовок на русском
        "metric": f"{sum(order_counts)} заказов",
        # Общая метрика: общее количество заказов за неделю
        "footer": mark_safe(
            f'<strong class="text-green-600 font-medium">0.00%</strong>&nbsp;прогресс с прошлой недели'
        ),
        "chart": chart_json  # График
    }

    return context


def dashboard_callback(request, context):
    WEEKDAYS = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
    ]

    positive = [[1, random.randrange(8, 28)] for i in range(1, 28)]
    negative = [[-1, -random.randrange(8, 28)] for i in range(1, 28)]
    average = [r[1] - random.randint(3, 5) for r in positive]
    performance_positive = [[1, random.randrange(8, 28)] for i in range(1, 28)]
    performance_negative = [[-1, -random.randrange(8, 28)] for i in range(1, 28)]

    context.update(
        {
            "navigation": [
                {
                    "title": _("Dashboard"),
                    "link": "#",
                    # "active": True
                },
                # {
                #     "title": _("Analytics"),
                #     "link": "#"
                # },
                # {
                #     "title": _("Settings"),
                #     "link": "#"
                # },
            ],
            "filters": [
                {
                    "title": _("All"),
                    "link": "#",
                    "active": True
                },
                # {
                #     "title": _("New"),
                #     "link": "#",
                # },
            ],
            "orders_performance": get_last_week_orders_chart(request)
            # "performance": [
            #     {
            #         "title": ("Last week revenue"),
            #         "metric": "$0.00",  # Устанавливаем метрику на 0
            #         "footer": mark_safe(
            #             '<strong class="text-green-600 font-medium">0.00%</strong>&nbsp;progress from last week'
            #             # Прогресс 0%
            #         ),
            #         "chart": json.dumps({
            #             "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
            #             # Оставляем дни недели
            #             "datasets": [{
            #                 "data": [0 for _ in range(28)],  # Устанавливаем все значения данных в 0
            #                 "borderColor": "#9333ea"
            #             }]
            #         }),
            #     }

                # {
                #     "title": _("Last week revenue"),
                #     "metric": "$1,234.56",
                #     "footer": mark_safe(
                #         '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                #     ),
                #     "chart": json.dumps({"labels": [WEEKDAYS[day % 7] for day in range(1, 28)], "datasets": [{"data": performance_positive, "borderColor": "#9333ea"}]}),
                # },
                # {
                #     "title": _("Last week expenses"),
                #     "metric": "$1,234.56",
                #     "footer": mark_safe(
                #         '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                #     ),
                #     "chart": json.dumps({"labels": [WEEKDAYS[day % 7] for day in range(1, 28)], "datasets": [{"data": performance_negative, "borderColor": "#f43f5e"}]}),
                # },
            # ]
        },
    )

    return context