from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import path
from django.views.generic import TemplateView

from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.decorators import action
from unfold.views import UnfoldModelAdminViewMixin

from menu.models import Category, Product
from ..models import Venue, Spot, Table
from services.pos_service_factory import POSServiceFactory


class MyClassBasedView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Гнерация qr-code"
    permission_required = ()
    template_name = 'venues/qr.html'


@admin.register(Venue)
class VenueAdmin(UnfoldModelAdmin):
    compressed_fields = True
    list_display = ('id', 'company_name', 'pos_system',)
    list_display_links = ('id', 'company_name')

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
            self.message_user(request,
                              f'Заведение {venue.company_name} не имеет API токена.',
                              level=messages.ERROR)
            return redirect(request.META["HTTP_REFERER"])

        pos_system_name = venue.pos_system.name.lower()
        pos_service = POSServiceFactory.get_service(pos_system_name, venue.access_token)

        # Шаг 1: Получаем категории
        categories_data = pos_service.get_categories()
        if not categories_data:
            self.message_user(request, 'Ошибка при получении категорий', level=messages.ERROR)
            return redirect(request.META["HTTP_REFERER"])

        categories_data = categories_data[1:]  # Пропускаем первую строку, если она не нужна

        created_category_count = 0
        for category_data in categories_data:
            existing_category = Category.objects.filter(
                venue=venue,
                external_id=category_data['category_id']
            ).exists()

            if not existing_category:
                pos_service.create_new_category(venue, category_data)
                created_category_count += 1

        if created_category_count > 0:
            self.message_user(request,
                              f"{created_category_count} категорий успешно созданы.",
                              level='success')
        else:
            self.message_user(request,
                              "Категории актуальны.",
                              level='success')

        # Шаг 2: Получаем продукты
        products_data = pos_service.get_products()
        if not products_data:
            self.message_user(request, 'Ошибка при получении товаров', level=messages.ERROR)
            return redirect(request.META["HTTP_REFERER"])

        created_product_count = 0
        for product_data in products_data:
            existing_product = Product.objects.filter(
                venue=venue,
                external_id=product_data['product_id']
            ).exists()
            category = Category.objects.filter(
                venue=venue,
                external_id=product_data.get('menu_category_id')
            ).first()

            if not existing_product and category:
                pos_service.create_new_product(product_data, venue, category)
                created_product_count += 1

        if created_product_count > 0:
            self.message_user(request,
                              f"{created_product_count} продуктов успешно созданы.",
                              level='success')
        else:
            self.message_user(request,
                              "Продукты актуальны.",
                              level='success')

        return redirect(request.META["HTTP_REFERER"])

    @action(
        description="Получить точки и столы заведения",
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

        # Сначала получаем точки
        spots_data = pos_service.get_spots()
        if not spots_data:
            self.message_user(request, 'Ошибка при получении точек заведения')
            return redirect(request.META["HTTP_REFERER"])

        created_spot_count = 0
        for spot_data in spots_data:
            existing_spot = Spot.objects.filter(
                venue=venue,
                external_id=spot_data['spot_id']
            ).exists()

            if not existing_spot:
                pos_service.create_new_spot(venue, spot_data)
                created_spot_count += 1

        if created_spot_count > 0:
            self.message_user(request,
                              f"{created_spot_count} точек заведения успешно созданы.",
                              level='success')
        else:
            self.message_user(request,
                              "Точки заведения актуальны.",
                              level='success')

        # Затем получаем столы
        tables_data = pos_service.get_tables()
        if not tables_data:
            self.message_user(request, 'Ошибка при получении столов')
            return redirect(request.META["HTTP_REFERER"])

        created_table_count = 0
        for table_data in tables_data:
            existing_table = Table.objects.filter(
                venue=venue,
                external_id=table_data['table_id']
            ).exists()
            spot = (Spot.objects.filter(
                venue=venue,
                external_id=table_data.get('spot_id'))
            ).first()

            if not existing_table:
                pos_service.create_new_table(table_data, venue, spot)
                created_table_count += 1

        if created_table_count > 0:
            self.message_user(request,
                              f"{created_table_count} столы успешно созданы.",
                              level='success')
        else:
            self.message_user(request,
                              "Столы актуальны.",
                              level='success')

        return redirect(request.META["HTTP_REFERER"])

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
