from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse, path
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.decorators import display, action

from deep_translator import GoogleTranslator

from account.models import ROLE_OWNER, ROLE_ADMIN
from services.admin import BaseModelAdmin
from ..forms import CategoryAdminForm
from ..models import Category
from ..services import ai_improve_image, ai_generate_image


@admin.register(Category)
class CategoryAdmin(BaseModelAdmin, TabbedTranslationAdmin):
    form = CategoryAdminForm
    compressed_fields = True
    list_filter = ('venue', 'category_hidden',)
    search_fields = ('category_name',)
    readonly_fields = ('category_photo_preview',)
    list_select_related = ('venue',)
    list_per_page = 20

    mptt_level_indent = 20
    mptt_show_nodedata = True

    actions_detail = ["translate_action"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("ai_improve/<int:pk>/", self.admin_site.admin_view(self.ai_improve_view), name="category_ai_improve"),
            path("ai_generate/<int:pk>/", self.admin_site.admin_view(self.ai_generate_view),
                 name="category_ai_generate"),
        ]
        return my_urls + urls

    def ai_improve_view(self, request, pk):
        obj = get_object_or_404(Category, pk=pk)
        msg = ai_improve_image(obj, field_name='category_photo', prompt=obj.venue.ai_improve_prompt)
        messages.success(request, msg or "Готово ✅")
        return JsonResponse({"ok": True})

    def ai_generate_view(self, request, pk):
        obj = get_object_or_404(Category, pk=pk)
        msg = ai_generate_image(obj, field_name='category_photo', prompt=obj.venue.ai_generate_prompt)
        messages.success(request, msg or "Готово ✅")
        return JsonResponse({"ok": True})

    @action(
        description="Перевести название",
        url_path="translate",
    )
    def translate_action(self, request: HttpRequest, object_id: int):
        category = Category.objects.get(pk=object_id)

        if not category.category_name:
            self.message_user(request, "Поле category_name пустое", messages.WARNING)
            return redirect(
                reverse_lazy("admin:menu_category_change", args=[category.pk])
            )

        try:
            category.category_name_en = GoogleTranslator(source='ru', target='en').translate(category.category_name)
            category.category_name_ky = GoogleTranslator(source='ru', target='ky').translate(category.category_name)
            category.save()

            self.message_user(request, "Перевод выполнен успешно", messages.SUCCESS)

        except Exception as e:
            self.message_user(request, f"Ошибка перевода: {e}", messages.ERROR)

        return redirect(
            reverse_lazy("admin:menu_category_change", args=[category.pk])
        )

    def get_list_filter(self, request):
        list_filter = ()
        if request.user.is_superuser:
            list_filter = ('venue', 'category_hidden',)
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_filter = ('category_hidden',)
        return list_filter

    def get_list_display(self, request):
        list_display = ('id', 'category_name', 'venue', 'display_category_hidden', 'category_photo_preview',
                        'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_display = ('id', 'category_name', 'display_category_hidden', 'category_photo_preview',
                            'detail_link')
        return list_display

    @display(
        description="Скрыт?",
        label={
            'Да': "info",
            'Нет': "secondary"
        }
    )
    def display_category_hidden(self, instance):
        if instance.category_hidden:
            return "Да"
        return "Нет"

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
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            fieldsets[0][1]['fields'] = (
                'category_name_ru', 'category_name_ky', 'category_name_en',
                'category_photo_preview', 'category_photo')
        return fieldsets

    def save_model(self, request, obj, form, change):
        if request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            obj.venue = request.user.venue
        super().save_model(request, obj, form, change)

        if obj.category_hidden:
            count = obj.products.update(hidden=True)
            self.message_user(
                request,
                f"Категория '{obj.category_name}' скрыта. {count} товаров также скрыто.",
                level=messages.WARNING
            )
        else:
            count = obj.products.update(hidden=False)
            self.message_user(
                request,
                f"Категория '{obj.category_name}' снова активна. {count} товаров снова отображаются.",
                level=messages.SUCCESS
            )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return qs.filter(venue=request.user.venue)
