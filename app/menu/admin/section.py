from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin

from account.models import ROLE_OWNER, ROLE_ADMIN
from services.admin import BaseModelAdmin
from ..models import Section


@admin.register(Section)
class SectionAdmin(BaseModelAdmin, TabbedTranslationAdmin):
    compressed_fields = True
    list_filter = ('venue',)
    search_fields = ('name',)
    readonly_fields = ('photo_preview',)
    list_select_related = ('venue',)
    list_per_page = 20
    autocomplete_fields = ('categories',)

    # --- Фильтры для разных ролей пользователей ---
    def get_list_filter(self, request):
        list_filter = ()
        if request.user.is_superuser:
            list_filter = ('venue',)
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_filter = ()
        return list_filter

    # --- Колонки в списке ---
    def get_list_display(self, request):
        list_display = ('id', 'name', 'venue', 'photo_preview', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_display = ('id', 'name', 'photo_preview', 'detail_link')
        return list_display

    # --- Превью фотографии ---
    def photo_preview(self, obj):
        if obj.photo:
            url = obj.photo.url if not str(obj.photo).startswith(('http', 'https')) else str(obj.photo)
            return format_html(
                '<img src="{}" style="border-radius:5px; width: 120px; height: auto;" />',
                url
            )
        return "Нет изображения"

    photo_preview.short_description = 'Превью'

    # --- Поля формы и предпросмотр ---
    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {
                'fields': (
                    'name_ru',
                    'name_ky',
                    'name_en',
                    'photo',
                    'venue',
                    'categories',
                )
            }),
        )
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            fieldsets[0][1]['fields'] = (
                'name_ru', 'name_ky', 'name_en', 'photo', 'categories'
            )
        return fieldsets

    # --- Сохранение: проставляем venue для владельца ---
    def save_model(self, request, obj, form, change):
        """Если владелец или админ создают Section — подставляем их venue"""
        if request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            obj.venue = request.user.venue
        super().save_model(request, obj, form, change)

    # --- Фильтрация queryset по ролям ---
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return qs.filter(venue=request.user.venue)
        return qs.none()
