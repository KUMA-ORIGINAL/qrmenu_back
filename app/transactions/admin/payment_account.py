from django.contrib import admin

from services.admin import BaseModelAdmin
from ..models import PaymentAccount


@admin.register(PaymentAccount)
class PaymentAccountAdmin(BaseModelAdmin):
    list_filter = ("service", "venue")
    list_select_related = ("venue",)
    list_display = ("service", "name", "venue",)
    list_filter_submit = True
