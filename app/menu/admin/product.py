from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html
from unfold.admin import ModelAdmin as UnfoldModelAdmin, TabularInline
from unfold.typing import FieldsetsType

from venues.models import Venue
from ..models import Product, Category, Modificator


class ModificatorInline(TabularInline):
    model = Modificator
    extra = 1
    fields = ('name', 'price')


@admin.register(Product)
class ProductAdmin(UnfoldModelAdmin):
    list_display = ('id', 'product_name', 'category', 'venue', 'product_price', 'photo_preview')
    readonly_fields = ('photo_preview',)
    inlines = [ModificatorInline]

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

    def get_fieldsets(self, request: HttpRequest, obj=None) -> FieldsetsType:
        fieldsets = (
            (None, {
                'fields': (
                    'product_name', 'product_description', 'product_price', 'category', 'venue',
                    'pos_system')
            }),
            ('Photo', {
                'fields': ('product_photo', 'photo_preview'),
            }),
            ('Дополнительная информация', {
                'fields': ('hidden', 'external_id'),
            }),
        )
        if request.user.is_superuser:
            pass
        elif request.user.role == 'owner':
            fieldsets[0][1]['fields'] = (
                'product_name', 'product_description', 'product_price', 'category'
            )
            fieldsets[-1][1]['fields'] = ('hidden',)
        return fieldsets

    def save_model(self, request, obj, form, change):
        if request.user.role == 'owner' and not change:
            obj.venue = Venue.objects.filter(user=request.user).first()  # Заполняем venue владельца
            obj.pos_system = obj.venue.pos_system  # Заполняем pos_system автоматически
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category' and request.user.role == 'owner':
            venue = Venue.objects.filter(user=request.user).first()
            kwargs["queryset"] = Category.objects.filter(venue=venue)  # Ограничиваем категории
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner':
            return qs.filter(venue__user=request.user)  # Показываем только продукты заведения владельца