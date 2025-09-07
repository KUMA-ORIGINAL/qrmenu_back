from django.contrib import admin

from account.models import ROLE_OWNER, ROLE_ADMIN
from services.admin import BaseModelAdmin
from ..models import Client


@admin.register(Client)
class ClientAdmin(BaseModelAdmin):
    compressed_fields = True
    search_fields = ('phone_number', 'phone')

    def get_list_display(self, request, obj=None):
        list_display = ('id', 'firstname', 'phone_number', 'bonus', 'created_at', 'venue', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_display = ('id', 'firstname', 'phone_number', 'bonus', 'created_at', 'detail_link')
        return list_display

    def get_list_filter(self, request, obj=None):
        list_filter = ('venue', 'client_sex',)
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_filter = ('client_sex',)
        return list_filter

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return [field for field in fields if field not in ['venue', 'external_id']]
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return qs.filter(venue=request.user.venue)
