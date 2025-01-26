from django.contrib import admin


from services.admin import BaseModelAdmin
from ..models import Table, Venue, Spot


@admin.register(Table)
class TableAdmin(BaseModelAdmin):
    list_display = ('id', 'table_num', 'table_title', 'table_shape', 'spot', 'venue', 'detail_link')
    search_fields = ('table_num', 'table_title')
    list_filter = ('table_shape',)


    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role == 'owner':
            return [field for field in fields if field not in ['venue', 'external_id']]
        return fields

    def save_model(self, request, obj, form, change):
        if request.user.role == 'owner' and not change:
            obj.venue = Venue.objects.filter(user=request.user).first()  # Заполняем venue владельца
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'spot' and request.user.role == 'owner':
            venue = Venue.objects.filter(user=request.user).first()
            kwargs["queryset"] = Spot.objects.filter(venue=venue)  # Ограничиваем категории
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner':
            return qs.filter(venue__user=request.user)
        return qs