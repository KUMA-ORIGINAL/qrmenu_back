from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html
from unfold.admin import TabularInline
from unfold.contrib.filters.admin import RangeNumericFilter
from unfold.typing import FieldsetsType

from services.admin import BaseModelAdmin
from venues.models import Venue
from ..models import Product, Category, Modificator


class ModificatorInline(TabularInline):
    model = Modificator
    extra = 1
    fields = ('name', 'price')


@admin.register(Product)
class ProductAdmin(BaseModelAdmin):
    compressed_fields = True
    list_display = ('id', 'product_name', 'category', 'hidden', 'is_recommended', 'venue',
                    'product_price', 'photo_preview', 'detail_link')
    readonly_fields = ('photo_preview',)
    search_fields = ('product_name',)
    list_filter = ('venue', 'category', 'hidden', ("product_price", RangeNumericFilter),)
    list_editable = ('hidden', 'is_recommended',)
    inlines = [ModificatorInline]

    def get_list_display(self, request):
        list_display = ('id', 'product_name', 'category', 'hidden', 'is_recommended', 'venue',
                        'product_price', 'photo_preview', 'detail_link')
        if request.user.is_superuser:
            return list_display
        elif request.user.role == 'owner':
            list_display = (item for item in list_display if item not in ('venue',))
            return list_display
        return list_display

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
                    'external_id',
                    'product_name',
                    'product_description', 'product_price', 'weight',
                    'category',
                    'venue',
                    'pos_system')
            }),
            ('Photo', {
                'fields': ('photo_preview', 'product_photo',),
            }),
            ('Дополнительная информация', {
                'fields': ('hidden', 'is_recommended'),
            }),
        )
        if request.user.is_superuser:
            pass
        elif request.user.role == 'owner':
            fieldsets[0][1]['fields'] = (
                'product_name', 'product_description', 'product_price', 'weight', 'category'
            )
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