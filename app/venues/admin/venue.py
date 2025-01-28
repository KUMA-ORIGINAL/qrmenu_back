from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import path
from django.views.generic import TemplateView

from unfold.decorators import action
from unfold.views import UnfoldModelAdminViewMixin

from menu.models import Category, Product
from services.admin import BaseModelAdmin
from ..models import Venue, Spot, Table, Hall
from services.pos_service_factory import POSServiceFactory


class MyClassBasedView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Гнерация qr-code"
    permission_required = ()
    template_name = 'venues/qr.html'


@admin.register(Venue)
class VenueAdmin(BaseModelAdmin):
    compressed_fields = True
    list_display = ('id', 'company_name', 'pos_system', 'detail_link')

    actions_detail = ['products_actions_detail',
                      'spots_and_tables_action_detail',]

    def get_urls(self):
        return super().get_urls() + [
            path(
                "qr",
                MyClassBasedView.as_view(model_admin=self),  # IMPORTANT: model_admin is required
                name="qr"
            ),
        ]

    @action(
        description="Получить меню",
        url_path="products_actions_detail-url",
    )
    def products_actions_detail(self, request, object_id):
        venue = get_object_or_404(Venue, pk=object_id)

        if not venue.access_token:
            self.message_user(request, f'Заведение {venue.company_name} не имеет API токена.',
                              level=messages.ERROR)
            return redirect(request.META["HTTP_REFERER"])

        pos_system_name = venue.pos_system.name.lower()
        pos_service = POSServiceFactory.get_service(pos_system_name, venue.access_token)

        categories_data = pos_service.get_categories()[1:]
        create_method = pos_service.create_new_category
        if not self.process_items(request, venue, categories_data, Category,
                                  'category_id', create_method, 'категорий'):
            return redirect(request.META["HTTP_REFERER"])

        products_data = pos_service.get_products()
        create_method = pos_service.create_new_product
        if not self.process_items(
                request, venue, products_data, Product, 'product_id',
                create_method, 'продуктов',
                related_model_class_1=Category, related_external_id_key_1='menu_category_id'):
            return redirect(request.META["HTTP_REFERER"])

        return redirect(request.META["HTTP_REFERER"])

    @action(
        description="Получить точки, залы и столы заведения",
        url_path="spots_and_tables_action_detail-url",
    )
    def spots_and_tables_action_detail(self, request, object_id):
        venue = get_object_or_404(Venue, pk=object_id)

        if not venue.access_token:
            self.message_user(request,
                              f'Заведение {venue.company_name} не имеет API токена.',
                              level=messages.ERROR)
            return redirect(request.META["HTTP_REFERER"])

        pos_system_name = venue.pos_system.name.lower()
        pos_service = POSServiceFactory.get_service(pos_system_name, venue.access_token)

        # Получаем и обрабатываем точки
        spots_data = pos_service.get_spots()
        create_method = pos_service.create_new_spot
        if not self.process_items(
                request, venue, spots_data, Spot,
                'spot_id', create_method, 'точек'):
            return redirect(request.META["HTTP_REFERER"])

        halls_data = pos_service.get_halls()
        create_method = pos_service.create_new_hall
        if not self.process_items(
                request, venue, halls_data, Hall,
                'hall_id', create_method, 'залов',
                related_model_class_1=Spot, related_external_id_key_1='spot_id'):
            return redirect(request.META["HTTP_REFERER"])

        tables_data = pos_service.get_tables()
        create_method = pos_service.create_new_table
        if not self.process_items(
                request, venue, tables_data, Table,
                'table_id', create_method, 'столов',
                related_model_class_1=Hall, related_external_id_key_1='hall_id',
                related_model_class_2=Spot, related_external_id_key_2='spot_id',):
            return redirect(request.META["HTTP_REFERER"])

        return redirect(request.META["HTTP_REFERER"])

    def process_items(self, request, venue, items_data, model_class, external_id_key, create_method,
                      item_name, related_model_class_1=None, related_external_id_key_1=None,
                      related_model_class_2=None, related_external_id_key_2=None):
        if not items_data:
            self.message_user(request, f'Ошибка при получении {item_name}')
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
                create_method(item_data, venue, related_instance_1, related_instance_2)  # Передаем связанный объект
                created_item_count += 1

        if created_item_count > 0:
            self.message_user(request,
                              f"{created_item_count} {item_name} успешно созданы.",
                              level=messages.SUCCESS)
        else:
            self.message_user(request,
                              f"{item_name.capitalize()} актуальны.",
                              level=messages.SUCCESS)
        return True

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role == 'owner':
            return [field for field in fields if field != 'pos_system']
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner':
            return qs.filter(user=request.user)
        return qs
