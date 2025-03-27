from django.contrib import admin

from account.models import ROLE_OWNER, ROLE_ADMIN
from services.admin import BaseModelAdmin
from ..models import ReceiptPrinter


@admin.register(ReceiptPrinter)
class ReceiptPrinterAdmin(BaseModelAdmin):
    search_fields = ('name',)

    def get_list_filter(self, request):
        list_filter = ()
        if request.user.is_superuser:
            list_filter = ('venue',)
        return list_filter

    def get_list_display(self, request):
        list_display = ('id', 'name', 'venue', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER]:
            list_display = ('name', 'detail_link')
        return list_display

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role == ROLE_OWNER:
            return [field for field in fields if field not in ['venue',]]
        return fields

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_OWNER and not change:
            obj.venue = request.user.venue
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_OWNER:
            return qs.filter(venue=request.user.venue)
        return qs
