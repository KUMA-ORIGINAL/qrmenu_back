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
    list_display = ('id', 'company_name', 'pos_system',)
    list_display_links = ('id', 'company_name')

    actions_detail = ["categories_actions_detail",
                      'products_actions_detail',
                      'spots_action_detail',
                      'tables_action_detail']

    def get_urls(self):
        return super().get_urls() + [
            path(
                "qr",
                MyClassBasedView.as_view(model_admin=self),  # IMPORTANT: model_admin is required
                name="qr"
            ),
        ]

    @action(
        description="Получить категории",
        url_path="categories_actions_detail-url",
    )
    def categories_actions_detail(self, request, object_id):
        venue = get_object_or_404(Venue, pk=object_id)
        if not venue.access_token:
            self.message_user(request,
                              f'Заведение {venue.company_name} не имеет API токена.',
                              level=messages.ERROR)
            return redirect(request.META["HTTP_REFERER"])

        pos_system_name = venue.pos_system.name.lower()
        pos_service = POSServiceFactory.get_service(pos_system_name, venue.access_token)
        categories_data = pos_service.get_categories()
        if not categories_data:
            self.message_user(request, 'Ошибка при получении данных', level=messages.ERROR)
            return redirect(request.META["HTTP_REFERER"])
        categories_data = categories_data[1:]

        created_count = 0
        for category_data in categories_data:
            existing_category = Category.objects.filter(
                venue=venue,
                external_id=category_data['category_id']
            ).exists()

            if not existing_category:
                pos_service.create_new_category(venue, category_data)
                created_count += 1

        if created_count > 0:
            self.message_user(request,
                              f"{created_count} категорий успешно созданы.",
                              level='success')
        else:
            self.message_user(request,
                              "Категории актуальны.",
                              level='success')
        return redirect(request.META["HTTP_REFERER"])

    @action(
        description="Получить товары",
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
        products_data = pos_service.get_products()
        if not products_data:
            self.message_user(request, 'Ошибка при получении данных')
            return redirect(request.META["HTTP_REFERER"])

        created_count = 0
        for product_data in products_data:
            existing_product = Product.objects.filter(
                venue=venue,
                external_id=product_data['product_id']
            ).exists()

            if not existing_product:
                pos_service.create_new_product(venue, product_data)
                created_count += 1

        if created_count > 0:
            self.message_user(request,
                              f"{created_count} продуктов успешно созданы.",
                              level='success')
        else:
            self.message_user(request,
                              "Продукты актуальны.",
                              level='success')

        return redirect(request.META["HTTP_REFERER"])

    @action(
        description="Получить точки заведения",
        url_path="spots_action_detail-url",
    )
    def spots_action_detail(self, request, object_id):
        venue = get_object_or_404(Venue, pk=object_id)
        if not venue.access_token:
            self.message_user(request,
                              f'Заведение {venue.company_name} не имеет API токена.',
                              level=messages.ERROR)
            return redirect(request.META["HTTP_REFERER"])

        pos_system_name = venue.pos_system.name.lower()
        pos_service = POSServiceFactory.get_service(pos_system_name, venue.access_token)
        spots_data = pos_service.get_spots()
        if not spots_data:
            self.message_user(request, 'Ошибка при получении данных')
            return redirect(request.META["HTTP_REFERER"])

        created_count = 0
        for spot_data in spots_data:
            existing_product = Spot.objects.filter(
                venue=venue,
                external_id=spot_data['spot_id']
            ).exists()

            if not existing_product:
                pos_service.create_new_spot(venue, spot_data)
                created_count += 1

        if created_count > 0:
            self.message_user(request,
                              f"{created_count} точек заведения успешно созданы.",
                              level='success')
        else:
            self.message_user(request,
                              "точки заведения актуальны.",
                              level='success')

        return redirect(request.META["HTTP_REFERER"])

    @action(
        description="Получить столы",
        url_path="tables_action_detail-url",
    )
    def tables_action_detail(self, request, object_id):
        venue = get_object_or_404(Venue, pk=object_id)
        if not venue.access_token:
            self.message_user(request,
                              f'Заведение {venue.company_name} не имеет API токена.',
                              level=messages.ERROR)
            return redirect(request.META["HTTP_REFERER"])

        pos_system_name = venue.pos_system.name.lower()
        pos_service = POSServiceFactory.get_service(pos_system_name, venue.access_token)
        tables_data = pos_service.get_tables()
        if not tables_data:
            self.message_user(request, 'Ошибка при получении данных')
            return redirect(request.META["HTTP_REFERER"])

        created_count = 0
        for table_data in tables_data:
            existing_product = Table.objects.filter(
                venue=venue,
                external_id=table_data['table_id']
            ).exists()

            if not existing_product:
                pos_service.create_new_table(venue, table_data)
                created_count += 1

        if created_count > 0:
            self.message_user(request,
                              f"{created_count} столы успешно созданы.",
                              level='success')
        else:
            self.message_user(request,
                              "столы актуальны.",
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
