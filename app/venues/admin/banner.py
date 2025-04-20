from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from unfold.contrib.forms.widgets import WysiwygWidget

from account.models import ROLE_OWNER, ROLE_ADMIN
from services.admin import BaseModelAdmin
from ..models import Banner


@admin.register(Banner)
class BannerAdmin(BaseModelAdmin):
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
    search_fields = ('title', 'text', 'url')
    list_filter = ('status',)

    def banner_preview(self, obj):
        if obj.banner:
            return format_html('<img src="{}" style="border-radius:5px;'
                               'width: 120px; height: auto;" />',
                               obj.banner.url)
        return '(Нет изображения)'
    banner_preview.short_description = 'Превью'

    def get_list_display(self, request):
        list_display = ('id', 'title', 'status', 'venue', 'banner_preview', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_display = ('title', 'status', 'banner_preview', 'detail_link')
        return list_display

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return [f for f in fields if f not in ['venue']]
        return fields

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_OWNER and not change:
            obj.venue = request.user.venue
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == [ROLE_OWNER, ROLE_ADMIN]:
            return qs.filter(venue=request.user.venue)
        return qs
