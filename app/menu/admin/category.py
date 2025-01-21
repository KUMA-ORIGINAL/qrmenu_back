from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from venues.models import Venue
from ..models import Category


@admin.register(Category)
class CategoryAdmin(UnfoldModelAdmin):
    compressed_fields = True
    list_display = ('category_name', 'venue', 'category_hidden', 'category_photo_preview')
    list_filter = ('venue', 'category_hidden',)
    search_fields = ('category_name',)
    readonly_fields = ('category_photo_preview',)
    list_per_page = 20

    mptt_level_indent = 20
    mptt_show_nodedata = True

    def category_photo_preview(self, obj):
        if obj.category_photo:
            if (str(obj.category_photo).startswith('http') or
                str(obj.category_photo).startswith('https')):
                return format_html('<img src="{}" style="width: 150px; height: auto;" />',
                                   obj.category_photo)
            else:
                return format_html('<img src="{}" style="width: 150px; height: auto;" />',
                                   obj.category_photo.url)
        return "No Image"

    category_photo_preview.short_description = 'Превью'

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {
                'fields': (
                    'external_id',
                    'category_name',
                    'category_photo_preview',
                    'category_photo', 'venue', 'pos_system')
            }),
            ('Дополнительная информация', {
                'fields': ('category_hidden',),
                'classes': ('collapse',)
            }),
        )
        if request.user.is_superuser:
            pass
        elif request.user.role == 'owner':
            fieldsets[0][1]['fields'] = ('category_name',
                                         'category_photo_preview',
                                         'category_photo')
        return fieldsets

    def save_model(self, request, obj, form, change):
        if request.user.role == 'owner' and not change:
            obj.venue = Venue.objects.filter(user=request.user).first()  # Заполняем venue владельца
            obj.pos_system = obj.venue.pos_system  # Заполняем pos_system автоматически
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner':
            return qs.filter(venue__user=request.user)
