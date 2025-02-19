from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin

from services.admin import BaseModelAdmin
from ..models import Category


@admin.register(Category)
class CategoryAdmin(BaseModelAdmin, TabbedTranslationAdmin):
    compressed_fields = True
    list_filter = ('venue', 'category_hidden',)
    search_fields = ('category_name',)
    readonly_fields = ('category_photo_preview',)
    list_per_page = 20

    mptt_level_indent = 20
    mptt_show_nodedata = True

    def get_list_display(self, request):
        list_display = ('id', 'category_name', 'venue', 'category_hidden', 'category_photo_preview',
                        'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == 'owner' or request.user.role == 'admin':
            list_display = ('category_name', 'category_hidden', 'category_photo_preview',
                            'detail_link')
        return list_display

    def category_photo_preview(self, obj):
        if obj.category_photo:
            if (str(obj.category_photo).startswith('http') or
                str(obj.category_photo).startswith('https')):
                return format_html('<img src="{}" style="border-radius:5px;'
                                   'width: 120px; height: auto;" />',
                                   obj.category_photo)
            else:
                return format_html('<img src="{}" style="border-radius:5px;'
                                   'width: 120px; height: auto;" />',
                                   obj.category_photo.url)
        return "No Image"

    category_photo_preview.short_description = 'Превью'

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {
                'fields': (
                    'external_id',
                    'category_name_ru',
                    'category_name_ky',
                    'category_name_en',
                    'category_photo_preview',
                    'category_photo', 'venue')
            }),
            ('Дополнительная информация', {
                'fields': ('category_hidden',),
                'classes': ('collapse',)
            }),
        )
        if request.user.is_superuser:
            pass
        elif request.user.role == 'owner' or request.user.role == 'admin':
            fieldsets[0][1]['fields'] = ('category_name',
                                         'category_photo_preview',
                                         'category_photo')
        return fieldsets

    def save_model(self, request, obj, form, change):
        if (request.user.role == 'owner' or request.user.role == 'admin') and not change:
            obj.venue = request.user.venue
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner' or request.user.role == 'admin':
            return qs.filter(venue=request.user.venue)
