from django.contrib import admin
from account.models import ROLE_OWNER, ROLE_ADMIN
from services.admin import BaseModelAdmin
from ..models import BonusHistory


@admin.register(BonusHistory)
class BonusHistoryAdmin(BaseModelAdmin):
    compressed_fields = True
    search_fields = ("client__phone_number", "client__firstname", "description")
    list_select_related = ("client", "order")

    def get_list_display(self, request, obj=None):
        list_display = ("id", "client", "order", "amount", "operation", "created_at", "detail_link",)
        return list_display

    def get_list_filter(self, request, obj=None):
        list_filter = ("operation", "created_at")
        if request.user.is_superuser:
            list_filter += ("client__venue",)
        return list_filter

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("client", "order")
        if request.user.is_superuser:
            return qs
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return qs.filter(client__venue=request.user.venue)
        return qs
