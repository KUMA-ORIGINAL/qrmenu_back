from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from ..models import Product


@admin.register(Product)
class ProductAdmin(UnfoldModelAdmin):
    list_display = ('product_name', 'category', 'venue', 'product_price', 'photo_preview')
    filter_horizontal = ('modificators',)
    readonly_fields = ('photo_preview',)

    fieldsets = (
        (None, {
            'fields': ('product_name', 'product_description', 'product_price', 'category', 'venue',
                       'pos_system')
        }),
        ('Modificators', {
            'fields': ('modificators',),
        }),
        ('Photo', {
            'fields': ('product_photo', 'photo_preview'),
        }),
        ('Дополнительная информация', {
            'fields': ('hidden', 'external_id'),
        }),
    )

    def photo_preview(self, obj):
        if obj.product_photo:
            if (str(obj.product_photo).startswith('http') or
                str(obj.product_photo).startswith('https')):
                return format_html('<img src="{}" style="width: 100px; height: auto;" />',
                                   obj.product_photo)
            else:
                return format_html('<img src="{}" style="width: 100px; height: auto;" />',
                                   obj.product_photo.url)
        return "No Image"

    photo_preview.short_description = 'Превью'

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