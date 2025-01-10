from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from ..models import Category


@admin.register(Category)
class CategoryAdmin(UnfoldModelAdmin):
    list_display = ('category_name', 'venue', 'category_hidden', 'category_photo_preview')
    list_filter = ('venue', 'category_hidden', 'level')
    search_fields = ('category_name',)
    readonly_fields = ('category_photo_preview',)
    list_per_page = 20

    mptt_level_indent = 20
    mptt_show_nodedata = True

    fieldsets = (
        (None, {
            'fields': ('category_name',
                       'category_photo_preview',
                       'category_photo', 'venue', 'pos_system')
        }),
        ('Дополнительная информация', {
            'fields': ('category_hidden', 'level', 'visible',),
            'classes': ('collapse',)
        }),
    )

    def category_photo_preview(self, obj):
        if obj.category_photo:
            if (str(obj.category_photo).startswith('http') or
                str(obj.category_photo).startswith('https')):
                return format_html('<img src="{}" style="width: 100px; height: auto;" />',
                                   obj.category_photo)
            else:
                return format_html('<img src="{}" style="width: 100px; height: auto;" />',
                                   obj.category_photo.url)
        return "No Image"

    category_photo_preview.short_description = 'Превью'
