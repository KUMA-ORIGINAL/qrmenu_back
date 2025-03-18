from django.contrib import admin

from account.models import ROLE_OWNER, ROLE_ADMIN
from services.admin import BaseModelAdmin
from ..models import Spot


@admin.register(Spot)
class SpotAdmin(BaseModelAdmin):
    change_form_before_template = 'venues/spot_change_form_before.html'

    def get_list_display(self, request):
        list_display = ('id', 'name', 'address', 'venue', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_display = ('name', 'address', 'detail_link')
        return list_display

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return [field for field in fields if field not in ['venue', 'external_id']]
        return fields

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_OWNER and not change:
            obj.venue = request.user.venue  # Заполняем venue владельца
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_OWNER:
            return qs.filter(venue=request.user.venue)
        elif request.user.role == ROLE_ADMIN:
            return qs.filter(users=request.user)
        return qs
