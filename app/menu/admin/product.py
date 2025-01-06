from django.contrib import admin

from ..models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'venue', 'price', 'available')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.is_owner():
            return qs.filter(venue__owner=request.user)  # Показываем только продукты заведения владельца
        elif request.user.is_manager():
            return qs.filter(venue__managers=request.user)  # Продукты заведений, где пользователь менеджер
        elif request.user.is_staff():
            return qs.filter(venue__staff=request.user)  # Продукты заведений, где пользователь сотрудник
        return qs.none()  # Другие пользователи не имеют доступа