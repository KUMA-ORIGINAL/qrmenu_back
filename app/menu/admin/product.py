from deep_translator import GoogleTranslator
from django.contrib import admin, messages
from django.core.files.storage import default_storage
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
from unfold.admin import TabularInline, StackedInline
from unfold.contrib.filters.admin import RangeNumericFilter
from unfold.decorators import display, action
from unfold.typing import FieldsetsType

from account.models import ROLE_OWNER, ROLE_ADMIN
from services.admin import BaseModelAdmin
from venues.models import Spot
from .admin_filters import CategoryFilter
from ..models import Product, Category, Modificator


class ModificatorInline(StackedInline, TranslationTabularInline):
    model = Modificator
    extra = 1
    fields = ('name', 'price')


@admin.register(Product)
class ProductAdmin(BaseModelAdmin, TabbedTranslationAdmin):
    compressed_fields = True
    readonly_fields = ('photo_preview',)
    search_fields = ('product_name',)
    list_select_related = ('category', 'venue')
    inlines = [ModificatorInline]
    autocomplete_fields = ('spots',)
    list_before_template = "menu/change_list_before.html"

    actions_detail = ['translate_product_fields']

    @action(
        description="Перевести название и описание",
        url_path="translate",
    )
    def translate_product_fields(self, request: HttpRequest, object_id: int):
        product = Product.objects.get(pk=object_id)

        if not product.product_name and not product.product_description:
            self.message_user(
                request,
                "Поля product_name и product_description пустые",
                messages.WARNING
            )
            return redirect(reverse_lazy("admin:menu_product_change", args=[product.pk]))

        try:
            if product.product_name:
                product.product_name_en = GoogleTranslator(source='ru', target='en').translate(product.product_name)
                product.product_name_ky = GoogleTranslator(source='ru', target='ky').translate(product.product_name)

            if product.product_description:
                product.product_description_en = GoogleTranslator(source='ru', target='en').translate(
                    product.product_description)
                product.product_description_ky = GoogleTranslator(source='ru', target='ky').translate(
                    product.product_description)

            product.save()

            self.message_user(request, "Перевод выполнен успешно", messages.SUCCESS)

        except Exception as e:
            self.message_user(request, f"Ошибка перевода: {e}", messages.ERROR)

        return redirect(reverse_lazy("admin:menu_product_change", args=[product.pk]))

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['changelist_url'] = 'admin:menu_product_changelist'
        if request.user.role == ROLE_OWNER:
            extra_context['spots'] = Spot.objects.filter(venue=request.user.venue)
            extra_context['filter_key'] = 'spots__id__exact'
        return super(ProductAdmin, self).changelist_view(request, extra_context=extra_context)

    def get_list_filter(self, request):
        list_filter = ()
        if request.user.is_superuser:
            list_filter = ('venue', 'category', 'hidden', ("product_price", RangeNumericFilter), 'spots')
        elif request.user.role == ROLE_OWNER:
            list_filter = (CategoryFilter, 'hidden', ("product_price", RangeNumericFilter))
        elif request.user.role == ROLE_ADMIN:
            list_filter = (CategoryFilter, 'hidden', ("product_price", RangeNumericFilter))
        return list_filter

    def get_list_display(self, request):
        list_display = ('id', 'product_name', 'category', 'display_hidden', 'display_is_recommended', 'venue',
                        'product_price', 'photo_preview', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_display = ('product_name', 'category', 'display_hidden', 'display_is_recommended',
                            'product_price', 'photo_preview', 'detail_link')
        return list_display

    @display(
        description="Рекомендован?",
        label={
            'Да': "info",
            'Нет': "secondary"
        }
    )
    def display_is_recommended(self, instance):
        if instance.is_recommended:
            return "Да"
        return "Нет"

    @display(
        description="Скрыт?",
        label={
            'Да': "info",
            'Нет': "secondary"
        }
    )
    def display_hidden(self, instance):
        if instance.hidden:
            return "Да"
        return "Нет"

    def photo_preview(self, obj):
        if not obj.product_photo:
            return "No Image"

        photo = str(obj.product_photo)

        if photo.startswith('http://') or photo.startswith('https://'):
            return format_html('<img src="{}" style="border-radius:5px; width:100px; height:auto;" />', photo)

        try:
            url = default_storage.url(obj.product_photo.name)
            return format_html('<img src="{}" style="border-radius:5px; width:100px; height:auto;" />', url)
        except Exception:
            return "Image not available"

    photo_preview.short_description = "Превью"

    def get_fieldsets(self, request: HttpRequest, obj=None) -> FieldsetsType:
        fieldsets = (
            (None, {
                'fields': (
                    'external_id',
                    'product_name_ru',
                    'product_name_ky',
                    'product_name_en',
                    'product_description_ru',
                    'product_description_ky',
                    'product_description_en',
                    'product_price', 'weight',
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
        elif request.user.role == ROLE_OWNER:
            fieldsets[0][1]['fields'] = (
                'product_name_ru',
                'product_name_ky',
                'product_name_en',
                'product_description_ru',
                'product_description_ky',
                'product_description_en',
                'product_price', 'weight', 'category'
            )
        elif request.user.role == ROLE_ADMIN:
            fieldsets[0][1]['fields'] = (
                'product_name_ru',
                'product_name_ky',
                'product_name_en',
                'product_description_ru',
                'product_description_ky',
                'product_description_en',
                'product_price', 'weight', 'category'
            )
            fieldsets[2][1]['fields'] = (
                'hidden', 'is_recommended',
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if request.user.role in [ROLE_OWNER, ROLE_ADMIN] and not change:
            obj.venue = request.user.venue
        super().save_model(request, obj, form, change)
        if request.user.role == ROLE_ADMIN and not change:
            obj.spots.add(request.user.spot)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.role in [ROLE_OWNER, ROLE_ADMIN] and db_field.name == 'category':
            venue = request.user.venue
            if venue:
                kwargs["queryset"] = Category.objects.filter(venue=venue)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if request.user.role in [ROLE_OWNER, ROLE_ADMIN] and db_field.name == 'spots':
            venue = request.user.venue
            if venue:
                kwargs["queryset"] = Spot.objects.filter(venue=venue)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_OWNER:
            return qs.filter(venue=request.user.venue)
        elif request.user.role == ROLE_ADMIN:
            return qs.filter(spots=request.user.spot)
