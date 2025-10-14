import logging

from django import forms
from django.contrib import admin, messages
from django.db import models
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import format_html
from unfold.admin import TabularInline
from unfold.contrib.forms.widgets import WysiwygWidget

from unfold.decorators import action, display
from unfold.widgets import UnfoldAdminTimeWidget

from account.models import ROLE_OWNER
from menu.models import Category, Product
from services.pos_service_factory import POSServiceFactory
from services.admin import BaseModelAdmin

from ..models import Venue, Spot, Table, Hall, WorkSchedule

logger = logging.getLogger(__name__)


class WorkScheduleForm(forms.ModelForm):
    class Meta:
        model = WorkSchedule
        fields = "__all__"
        widgets = {
            "work_start": UnfoldAdminTimeWidget(format='%H:%M', attrs={"placeholder": "чч:мм"}),
            "work_end": UnfoldAdminTimeWidget(format='%H:%M', attrs={"placeholder": "чч:мм"}),
        }


class WorkScheduleInline(TabularInline):
    model = WorkSchedule
    form = WorkScheduleForm
    extra = 0
    max_num = 7
    can_delete = False
    ordering = ("day_of_week",)
    fields = ("day_name", "work_start", "work_end", "is_day_off", 'is_24h')
    readonly_fields = ("day_name",)

    def day_name(self, obj):
        return obj.get_day_of_week_display()
    day_name.short_description = "День недели"

    def has_add_permission(self, request, obj=None):
        return False


class VenueAdminForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = "__all__"
        widgets = {
            "terms": WysiwygWidget,  # только для конкретного поля
        }


@admin.register(Venue)
class VenueAdmin(BaseModelAdmin):
    form = VenueAdminForm
    inlines = (WorkScheduleInline,)
    compressed_fields = True
    actions_detail = ['pos_action_detail',]

    def get_list_display(self, request):
        list_display = ('id', 'company_name', 'pos_system', 'link_to_venue', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_OWNER:
            list_display = ('id', 'company_name', 'pos_system', 'link_to_venue', 'detail_link')
        return list_display

    @display(
        description="Ссылка на заведение",
        label=True
    )
    def link_to_venue(self, obj):
        if obj.slug:
            url = f"https://imenu.kg/{obj.slug}"
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        return "-"

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        elif request.user.role == ROLE_OWNER:
            return ('pos_system_plain', )
        return ()

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            ("Основная информация", {
                'fields': (
                    'company_name',
                    'color_theme',
                    'logo',
                    'default_delivery_spot',
                    'terms',
                    'description'
                )
            }),
            ("Контактные данные владельца", {
                'fields': (
                    'owner_name', 'owner_id',
                    'owner_email', 'owner_phone',
                )
            }),
            ("Локация", {
                'fields': (
                    'country',
                    'city',
                )
            }),
            ("POS и Сервис", {
                'fields': (
                    'pos_system',
                    'account_number',
                    'access_token',
                )
            }),
            ("Тариф", {
                'fields': (
                    'tariff_key',
                    'tariff_price',
                    'next_pay_date',
                )
            }),
            ("Типы обслуживания", {
                'fields': (
                    'is_delivery_available',
                    'delivery_service_fee_percent',
                    'is_takeout_available',
                    'takeout_service_fee_percent',
                    'is_dinein_available',
                    'dinein_service_fee_percent',
                )
            }),
            ("Доставка", {
                'fields': (
                    'delivery_fixed_fee',
                    'delivery_free_from',
                )
            }),
            ("Бонусы", {
                'fields': (
                    'is_bonus_system_enabled',
                    'bonus_accrual_percent',
                )
            }),
            ("AI генерация изображений", {
                'fields': (
                    'ai_improve_prompt',
                    'ai_generate_prompt',
                ),
                'description': "Промпты для генерации и улучшения изображений через AI. "
                               "Если оставить пустыми — будут использоваться стандартные.",
            }),
        )

        if request.user.is_superuser:
            # для суперпользователя уже всё доступно
            pass
        elif request.user.role == ROLE_OWNER:
            # 🔹 для владельца тоже нужно заменить на новые поля
            fieldsets[3][1]['fields'] = (
                'pos_system_plain',
                'account_number',
                'access_token',
            )

        return fieldsets

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.role == ROLE_OWNER:
            venue = request.user.venue
            if venue:
                if db_field.name == 'default_delivery_spot':
                    kwargs["queryset"] = Spot.objects.filter(venue=venue)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @display(description="POS система")
    def pos_system_plain(self, obj):
        return str(obj.pos_system) if obj.pos_system else "-"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_OWNER:
            return qs.filter(users=request.user)
        return qs

    @action(
        description="Получить информацию из POS системы",
        url_path="spots_and_tables_action_detail-url",
    )
    def pos_action_detail(self, request, object_id):
        logger.info(f"Начало обработки POS данных для заведения ID: {object_id}")

        venue = get_object_or_404(Venue, pk=object_id)

        if not venue.access_token:
            msg = f'Заведение {venue.company_name} не имеет API токена.'
            logger.warning(msg)
            self.message_user(request, msg, level=messages.ERROR)
            return redirect(request.META["HTTP_REFERER"])

        pos_system_name = venue.pos_system.name.lower()
        logger.info(f"POS система: {pos_system_name} для заведения {venue.company_name}")

        pos_service = POSServiceFactory.get_service(pos_system_name, venue.access_token)

        logger.info("Получение spots...")
        spots_data = pos_service.get_spots()
        if not self.process_items(request, venue, spots_data, Spot, 'spot_id', pos_service.create_new_spot):
            return redirect(request.META["HTTP_REFERER"])

        logger.info("Получение halls...")
        halls_data = pos_service.get_halls()
        if not self.process_items(
                request, venue, halls_data, Hall, 'hall_id', pos_service.create_new_hall,
                related_model_class_1=Spot, related_external_id_key_1='spot_id'):
            return redirect(request.META["HTTP_REFERER"])

        logger.info("Получение tables...")
        tables_data = pos_service.get_tables()
        if not self.process_items(
                request, venue, tables_data, Table, 'table_id', pos_service.create_new_table,
                related_model_class_1=Hall, related_external_id_key_1='hall_id',
                related_model_class_2=Spot, related_external_id_key_2='spot_id'):
            return redirect(request.META["HTTP_REFERER"])

        logger.info("Получение categories...")
        categories_data = pos_service.get_categories()
        if not self.process_items(
                request, venue, categories_data, Category, 'category_id', pos_service.create_new_category):
            return redirect(request.META["HTTP_REFERER"])

        logger.info("Получение products...")
        products_data = pos_service.get_products()
        if not products_data:
            msg = 'Ошибка при получении продуктов'
            logger.error(msg)
            self.message_user(request, msg, level=messages.ERROR)
            return redirect(request.META["HTTP_REFERER"])

        created_item_count = 0
        for product_data in products_data:
            existing_product = Product.objects.filter(
                venue=venue,
                external_id=product_data['product_id']
            ).exists()

            if not existing_product:
                category_external_id = product_data.get('menu_category_id')
                related_category = Category.objects.filter(
                    venue=venue,
                    external_id=category_external_id
                ).first()
                if not related_category:
                    # logger.warning(
                    #     f"Не найдена категория для продукта ID={product_data}, "
                    #     f"Не найдена категория для продукта ID={product_data.get('product_id')}, "
                    #     f"menu_category_id={category_external_id}, "
                    #     f"имеющиеся категории: {list(Category.objects.filter(venue=venue).values_list('external_id', flat=True))}"
                    # )
                    msg = f"Связанная категория не найдена для продукта: {product_data.get('product_id')}"
                    logger.warning(msg)
                    self.message_user(
                        request,
                        f"Не удалось найти связанные объекты для Продуктов ({Category._meta.verbose_name_plural}).",
                        level=messages.ERROR,
                    )
                    return redirect(request.META["HTTP_REFERER"])

                related_spots = Spot.objects.filter(venue=venue)

                logger.debug(f"Создание нового продукта: {product_data}")
                pos_service.create_new_product(product_data, venue, related_category, related_spots)
                created_item_count += 1

        if created_item_count > 0:
            msg = f"{created_item_count} продуктов успешно созданы."
            logger.info(msg)
            self.message_user(request, msg, level=messages.SUCCESS)
        else:
            logger.info("Продукты актуальны.")
            self.message_user(request, "Продукты актуальны.", level=messages.SUCCESS)

        logger.info(f"Обработка POS данных завершена для заведения ID: {object_id}")
        return redirect(request.META["HTTP_REFERER"])

    def process_items(self, request, venue, items_data, model_class, external_id_key, create_method,
                      related_model_class_1=None, related_external_id_key_1=None,
                      related_model_class_2=None, related_external_id_key_2=None):
        item_name = model_class._meta.verbose_name_plural
        logger.info(f"Обработка {item_name}...")

        if not items_data:
            msg = f'{item_name} не найдено!'
            logger.warning(msg)
            self.message_user(request, msg)
            return False

        created_item_count = 0
        for item_data in items_data:
            existing_item = model_class.objects.filter(
                venue=venue,
                external_id=item_data[external_id_key]
            ).exists()

            if not existing_item:
                related_instance_1 = None
                if related_model_class_1 and related_external_id_key_1:
                    related_instance_1 = related_model_class_1.objects.filter(
                        venue=venue,
                        external_id=item_data.get(related_external_id_key_1)
                    ).first()

                related_instance_2 = None
                if related_model_class_2 and related_external_id_key_2:
                    related_instance_2 = related_model_class_2.objects.filter(
                        venue=venue,
                        external_id=item_data.get(related_external_id_key_2)
                    ).first()

                logger.debug(f"Создание нового объекта {item_name[:-1]}: {item_data}")
                create_method(item_data, venue, related_instance_1, related_instance_2)
                created_item_count += 1

        if created_item_count > 0:
            msg = f"{created_item_count} {item_name} успешно созданы."
            logger.info(msg)
            self.message_user(request, msg, level=messages.SUCCESS)
        else:
            msg = f"{item_name} актуальны."
            logger.info(msg)
            self.message_user(request, msg, level=messages.SUCCESS)

        return True
