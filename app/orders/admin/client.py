from django.contrib import admin

from services.admin import BaseModelAdmin
from ..models import Client


@admin.register(Client)
class ClientAdmin(BaseModelAdmin):
    compressed_fields = True
    list_display = ('id', 'firstname', 'phone', 'created_at', 'detail_link')
    search_fields = ('firstname', 'lastname')
    list_filter = ('client_sex',)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role == 'owner':
            return [field for field in fields if field not in ['venue', 'external_id']]
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner':
            return qs.filter(venue__user=request.user)
