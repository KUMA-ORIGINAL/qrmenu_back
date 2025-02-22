import logging

from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect

from unfold.decorators import action

from account.models import ROLE_OWNER
from menu.models import Category, Product
from services.pos_service_factory import POSServiceFactory
from services.admin import BaseModelAdmin

from ..models import Venue, Spot, Table, Hall

logger = logging.getLogger(__name__)


@admin.register(Venue)
class VenueAdmin(BaseModelAdmin):
    compressed_fields = True
    list_display = ('id', 'company_name', 'pos_system', 'detail_link')
    actions_detail = ['pos_action_detail',]

    @action(
        description="Получить информацию из POS системы",
        url_path="spots_and_tables_action_detail-url",
    )
    def pos_action_detail(self, request, object_id):
        venue = get_object_or_404(Venue, pk=object_id)

        if not venue.access_token:
            self.message_user(request,
                              f'Заведение {venue.company_name} не имеет API токена.',
                              level=messages.ERROR)
            return redirect(request.META["HTTP_REFERER"])

        pos_system_name = venue.pos_system.name.lower()
        pos_service = POSServiceFactory.get_service(pos_system_name, venue.access_token)

        spots_data = pos_service.get_spots()
        create_method = pos_service.create_new_spot
        if not self.process_items(
                request, venue, spots_data, Spot, 'spot_id', create_method):
            return redirect(request.META["HTTP_REFERER"])

        halls_data = pos_service.get_halls()
        create_method = pos_service.create_new_hall
        if not self.process_items(
                request, venue, halls_data, Hall, 'hall_id', create_method,
                related_model_class_1=Spot, related_external_id_key_1='spot_id'):
            return redirect(request.META["HTTP_REFERER"])

        tables_data = pos_service.get_tables()
        create_method = pos_service.create_new_table
        if not self.process_items(
                request, venue, tables_data, Table, 'table_id', create_method,
                related_model_class_1=Hall, related_external_id_key_1='hall_id',
                related_model_class_2=Spot, related_external_id_key_2='spot_id',):
            return redirect(request.META["HTTP_REFERER"])

        categories_data = pos_service.get_categories()[1:]
        create_method = pos_service.create_new_category
        if not self.process_items(
                request, venue, categories_data, Category, 'category_id', create_method):
            return redirect(request.META["HTTP_REFERER"])

        products_data = pos_service.get_products()
        create_method = pos_service.create_new_product

        if not products_data:
            self.message_user(request, 'Ошибка при получении продуктов', level=messages.ERROR)
            return redirect(request.META["HTTP_REFERER"])

        created_item_count = 0

        for product_data in products_data:
            existing_product = Product.objects.filter(
                venue=venue,
                external_id=product_data['product_id']
            ).exists()

            if not existing_product:
                related_category = Category.objects.filter(
                    venue=venue,
                    external_id=product_data.get('menu_category_id')
                ).first()
                if not related_category:
                    self.message_user(
                        request,
                        f"Не удалось найти связанные объекты для Продуктов "
                        f"({Category._meta.verbose_name_plural}).",
                        level=messages.ERROR,
                    )
                    return redirect(request.META["HTTP_REFERER"])

                related_spots = Spot.objects.filter(venue=venue)

                create_method(product_data, venue, related_category, related_spots)
                created_item_count += 1

        if created_item_count > 0:
            self.message_user(request,
                              f"{created_item_count} продуктов успешно созданы.",
                              level=messages.SUCCESS)
        else:
            self.message_user(request,
                              "Продукты актуальны.",
                              level=messages.SUCCESS)

        return redirect(request.META["HTTP_REFERER"])

    def process_items(self, request, venue, items_data, model_class, external_id_key, create_method,
                      related_model_class_1=None, related_external_id_key_1=None,
                      related_model_class_2=None, related_external_id_key_2=None):
        item_name = model_class._meta.verbose_name_plural
        if not items_data:
            self.message_user(request, f'{item_name} не найдено!')
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

                create_method(item_data, venue, related_instance_1, related_instance_2)
                created_item_count += 1

        if created_item_count > 0:
            self.message_user(request,
                              f"{created_item_count} {item_name} успешно созданы.",
                              level=messages.SUCCESS)
        else:
            self.message_user(request,
                              f"{item_name} актуальны.",
                              level=messages.SUCCESS)
        return True


    def get_list_display(self, request):
        list_display = ('id', 'company_name', 'pos_system', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_OWNER:
            list_display = ('company_name', 'pos_system', 'detail_link')
        return list_display

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role == ROLE_OWNER:
            return [field for field in fields if field not in ('pos_system',)]
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_OWNER:
            return qs.filter(users=request.user)
        return qs
