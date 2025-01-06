from django.contrib import admin
from ..models import Venue, POSSystem

@admin.register(POSSystem)
class POSSystemAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'pos_system', 'api_token')

    # Переопределяем метод queryset для отображения только заведений текущего пользователя
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:  # Если суперпользователь, показываем все заведения
            return qs
        return qs.filter(owner=request.user)  # Если обычный пользователь, показываем только его заведения

    # Отключаем возможность редактирования полей, если это не владелец заведения
    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.owner != request.user:
            return False
        return super().has_change_permission(request, obj=obj)

    # Отключаем возможность удаления заведений, если это не владелец заведения
    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.owner != request.user:
            return False
        return super().has_delete_permission(request, obj=obj)

