from django.contrib import admin


from services.admin import BaseModelAdmin
from ..models import Hall, Venue, Spot


@admin.register(Hall)
class HallAdmin(BaseModelAdmin):
    list_display = ('id', 'hall_name', 'spot', 'venue', 'detail_link')
    search_fields = ('hall_name',)

    def get_list_display(self, request):
        list_display = ('id', 'hall_name', 'spot', 'venue', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == 'owner':
            list_display = ('hall_name', 'spot', 'detail_link')
        return list_display

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
