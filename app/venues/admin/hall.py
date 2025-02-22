from django.contrib import admin

from account.models import ROLE_OWNER, ROLE_ADMIN
from services.admin import BaseModelAdmin
from ..models import Hall, Spot


@admin.register(Hall)
class HallAdmin(BaseModelAdmin):
    search_fields = ('hall_name',)
    list_before_template = "menu/change_list_before.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['changelist_url'] = 'admin:venues_hall_changelist'
        if request.user.role == ROLE_OWNER:
            extra_context['spots'] = Spot.objects.filter(venue=request.user.venue)
            extra_context['filter_key'] = 'spot__id__exact'
        return super(HallAdmin, self).changelist_view(request, extra_context=extra_context)

    def get_list_filter(self, request):
        list_filter = ()
        if request.user.is_superuser:
            list_filter = ('venue',)
        return list_filter

    def get_list_display(self, request):
        list_display = ('id', 'hall_name', 'spot', 'venue', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_display = ('hall_name', 'spot', 'detail_link')
        return list_display

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role == ROLE_OWNER:
            return [field for field in fields if field not in ['venue', 'external_id']]
        elif request.user.role == ROLE_ADMIN:
            return [field for field in fields if field not in ['venue', 'spot', 'external_id']]
        return fields

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_OWNER and not change:
            obj.venue = request.user.venue
        elif request.user.role == ROLE_ADMIN and not change:
            obj.venue = request.user.venue
            obj.spot = request.user.spot
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.role in [ROLE_OWNER, ROLE_ADMIN] and db_field.name == 'spot':
            venue = request.user.venue
            kwargs["queryset"] = Spot.objects.filter(venue=venue)  # Ограничиваем категории
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_OWNER:
            return qs.filter(venue=request.user.venue)
        elif request.user.role == ROLE_ADMIN:
            return qs.filter(spot=request.user.spot)
        return qs
