import calendar
import json
import random
from datetime import timedelta, datetime

from django.db.models import Count, Sum, F
from django.db.models.functions import TruncDay
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from account.models import ROLE_OWNER, ROLE_ADMIN
from orders.models import Order, OrderStatus


def get_current_month_orders_chart(request, chart_type="line"):
    """
    График количества заказов за весь текущий месяц (включая будущие дни).
    """
    now = timezone.now()

    # начало месяца (00:00:00)
    start_date = timezone.make_aware(
        datetime(now.year, now.month, 1, 0, 0, 0), timezone.get_current_timezone()
    )

    # конец месяца (23:59:59)
    last_day = calendar.monthrange(now.year, now.month)[1]
    end_date = timezone.make_aware(
        datetime(now.year, now.month, last_day, 23, 59, 59), timezone.get_current_timezone()
    )

    user = request.user

    # Доступные заказы
    if user.is_superuser:
        orders_queryset = Order.objects
    elif user.role in (ROLE_OWNER, ROLE_ADMIN):
        orders_queryset = Order.objects.filter(venue=user.venue)
    else:
        orders_queryset = Order.objects.none()

    # Фильтруем заказы текущего месяца
    orders_per_day = (
        orders_queryset.filter(created_at__range=(start_date, end_date))
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    orders_dict = {order["day"].date(): order["count"] for order in orders_per_day}

    months_ru = {
        1: "янв", 2: "фев", 3: "мар", 4: "апр", 5: "май",
        6: "июн", 7: "июл", 8: "авг", 9: "сен", 10: "окт", 11: "ноя", 12: "дек",
    }

    labels, order_counts = [], []
    total_days = (end_date.date() - start_date.date()).days + 1

    for i in range(total_days):
        current_day = start_date.date() + timedelta(days=i)
        month_name = months_ru[current_day.month]
        labels.append(f"{current_day.day:02d} {month_name}")
        order_counts.append(orders_dict.get(current_day, 0))

    dataset = {
        "label": str(_("Количество заказов")),
        "data": order_counts,
        "borderColor": "#9333ea",
        "fill": False,
        "tension": 0.3,
    }
    if chart_type == "bar":
        dataset.update({"backgroundColor": "#9333ea", "borderWidth": 2})

    options = {
        "plugins": {
            "datalabels": {
                "anchor": "end",
                "align": "top",
                "color": "#ffffff",
                "font": {"weight": "bold", "size": 10},
                "formatter": "(value) => value",
            },
            "legend": {"display": True},
        },
        "scales": {
            "y": {"beginAtZero": True, "ticks": {"stepSize": 1, "precision": 0}},
            "x": {"ticks": {"maxRotation": 60, "minRotation": 45}},
        },
    }

    chart_data = {"labels": labels, "datasets": [dataset]}

    context = {
        "title": str(_("Количество заказов за текущий месяц")),
        "metric": f"{sum(order_counts)} заказов",
        "footer": mark_safe(
            '<strong class="text-green-600 font-medium">+0.00%</strong>&nbsp;прогресс с прошлым месяцем'
        ),
        "chart": json.dumps(chart_data),
        "options": json.dumps(options),
        "chart_type": chart_type,
    }

    return context

def get_summary_cards(request):
    """
    Возвращает данные только по оплаченных заказам (COMPLETED и NEW):
    - первые 4 карточки — за прошлый месяц
    - последние 4 — за текущий месяц
    """
    now = timezone.now()
    tz = timezone.get_current_timezone()

    # Начало текущего месяца (1 число 00:00:00)
    first_day_current_month = timezone.make_aware(
        datetime(now.year, now.month, 1, 0, 0, 0), tz
    )

    # Конец прошлого месяца = день перед началом текущего
    last_month_end = first_day_current_month - timedelta(seconds=1)

    # Начало прошлого месяца
    first_day_last_month = timezone.make_aware(
        datetime(last_month_end.year, last_month_end.month, 1, 0, 0, 0), tz
    )

    user = request.user

    # --- Фильтр заказов по пользователю ---
    if user.is_superuser:
        orders_queryset = Order.objects.all()
    elif user.role in (ROLE_OWNER, ROLE_ADMIN):
        orders_queryset = Order.objects.filter(venue=user.venue)
    else:
        orders_queryset = Order.objects.none()

    # --- Только COMPLETED и NEW ---
    completed_orders = orders_queryset.filter(
        status__in=[OrderStatus.COMPLETED, OrderStatus.NEW]
    )

    # --- Прошлый месяц (>= 1 числа прошл. месяца, < 1 числа тек. месяца) ---
    last_month_orders = completed_orders.filter(
        created_at__gte=first_day_last_month,
        created_at__lt=first_day_current_month,
    )

    last_month_orders_sum = last_month_orders.aggregate(total=Sum("total_price"))["total"] or 0
    last_month_orders_count = last_month_orders.count()

    # --- Текущий месяц ---
    current_month_orders = completed_orders.filter(
        created_at__gte=first_day_current_month
    )
    current_month_orders_sum = current_month_orders.aggregate(total=Sum("total_price"))["total"] or 0
    current_month_orders_count = current_month_orders.count()

    # --- Карточки ---
    cards = [
        # ---- Прошлый месяц ----
        {
            "title": _("Сумма оплаченных заказов за прошлый месяц"),
            "count": f"{last_month_orders_sum:,.2f}".replace(",", " "),
            "subtitle": _("сом"),
        },
        {
            "title": _("Количество оплаченных заказов за прошлый месяц"),
            "count": str(last_month_orders_count),
            "subtitle": _("шт."),
        },

        # ---- Текущий месяц ----
        {
            "title": _("Сумма оплаченных заказов за текущий месяц"),
            "count": f"{current_month_orders_sum:,.2f}".replace(",", " "),
            "subtitle": _("сом"),
        },
        {
            "title": _("Количество оплаченных заказов за текущий месяц"),
            "count": str(current_month_orders_count),
            "subtitle": _("шт."),
        },
    ]

    return cards


def dashboard_callback(request, context):
    context.update(
        {
            "navigation": [
                {
                    "title": _("Dashboard"),
                    "link": "#",
                    # "active": True
                },
            ],
            "filters": [
                {
                    "title": _("All"),
                    "link": "#",
                    "active": True
                },
            ],
            "orders_performance_bar": get_current_month_orders_chart(request, chart_type="bar"),
            "summary_cards": get_summary_cards(request),
        },
    )

    return context