from django.contrib import admin
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.html import format_html
from unfold.admin import TabularInline
from unfold.contrib.filters.admin import RangeNumericFilter
from unfold.decorators import action
from unfold.typing import FieldsetsType

from services.admin import BaseModelAdmin
from venues.models import Venue, Spot
from ..models import Product, Category, Modificator, ProductAttribute


class ModificatorInline(TabularInline):
    model = Modificator
    extra = 1
    fields = ('name', 'price')

#
# class ProductAttributeInline(TabularInline):
#     model = ProductAttribute
#     extra = 1
#     fields = ('name', 'price')


@admin.register(Product)
class ProductAdmin(BaseModelAdmin):
    compressed_fields = True
    readonly_fields = ('photo_preview',)
    search_fields = ('product_name',)
    list_filter = ('venue', 'category', 'hidden', ("product_price", RangeNumericFilter), 'spots')
    inlines = [ModificatorInline]
    filter_horizontal = ('spots',)
    list_before_template = "menu/change_list_before.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        if request.user.role == 'owner' or request.user.role == 'admin':
            extra_context['spots'] = Spot.objects.filter(venue=request.user.venue)
        return super(ProductAdmin, self).changelist_view(request, extra_context=extra_context)

    def get_list_display(self, request):
        list_display = ('id', 'product_name', 'category', 'hidden', 'is_recommended', 'venue',
                        'product_price', 'photo_preview', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == 'owner' or request.user.role == 'admin':
            list_display = ('product_name', 'category', 'hidden', 'is_recommended',
                            'product_price', 'photo_preview', 'detail_link')
        return list_display

    def photo_preview(self, obj):
        if obj.product_photo:
            if (str(obj.product_photo).startswith('http') or
                str(obj.product_photo).startswith('https')):
                return format_html('<img src="{}" style="border-radius:5px; '
                                   'width: 100px; height: auto;" />',
                                   obj.product_photo)
            else:
                return format_html('<img src="{}" style="border-radius:5px; '
                                   'width: 100px; height: auto;" />',
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
                    'venue')
            }),
            ('Photo', {
                'fields': ('photo_preview', 'product_photo',),
            }),
            ('Дополнительная информация', {
                'fields': ('hidden', 'is_recommended', 'spots'),
            }),
        )
        if request.user.is_superuser:
            pass
        elif request.user.role == 'owner' or request.user.role == 'admin':
            fieldsets[0][1]['fields'] = (
                'product_name', 'product_description', 'product_price', 'weight', 'category'
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if request.user.role == 'owner' or request.user.role == 'admin' and not change:
            obj.venue = request.user.venue
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.role == 'owner' or request.user.role == 'admin' and db_field.name == 'category':
            venue = request.user.venue
            if venue:
                kwargs["queryset"] = Category.objects.filter(venue=venue)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if request.user.role == 'owner' or request.user.role == 'admin' and db_field.name == 'spots':
            venue = request.user.venue
            if venue:
                kwargs["queryset"] = Spot.objects.filter(venue=venue)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner' or request.user.role == 'admin':
            return qs.filter(venue=request.user.venue)
