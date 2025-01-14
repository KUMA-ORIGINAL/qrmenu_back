from typing import Union

from django.contrib import admin, messages
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse_lazy
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.decorators import action

from menu.models import Category, Product
from ..models import Venue, POSSystem
from ..services.pos_service_factory import POSServiceFactory


@admin.register(POSSystem)
class POSSystemAdmin(UnfoldModelAdmin):
    list_display = ('name',)


@admin.register(Venue)
class VenueAdmin(UnfoldModelAdmin):
    # change_form_template = 'admin/account/venue/category_change_form.html'
    list_display = ('company_name', 'pos_system',)

    actions_detail = ["categories_actions_detail", 'products_actions_detail']

    @action(
        description="Получить категории из POS-системы",
        url_path="categories_actions_detail-url",
        permissions=["categories_actions_detail"],
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
        categories_data = pos_service.get_categories()[1:]

        created_count = 0
        for category_data in categories_data:
            existing_category = Category.objects.filter(
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

    def has_categories_actions_detail_permission(self, request, object_id):
        return True

    @action(
        description="Получить товары из POS-системы",
        url_path="products_actions_detail-url",
        permissions=["products_actions_detail"],
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

        created_count = 0
        for product_data in products_data:
            existing_product = Product.objects.filter(
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

    def has_products_actions_detail_permission(self, request, object_id):
        return True

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        # Если пользователь — owner, делаем поле pos_system только для чтения
        if request.user.role == 'owner':
            # Убираем поле из редактируемых
            return [field for field in fields if field != 'pos_system']
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner':
            return qs.filter(user=request.user)

    # def get_urls(self):
    #     urls = super().get_urls()
    #     custom_urls = [
    #         path('<int:venue_id>/update_categories/',
    #              self.admin_site.admin_view(self.update_categories),
    #              name='update_categories'),
    #         path('<int:venue_id>/update_products/',
    #              self.admin_site.admin_view(self.update_products),
    #              name='update_products'),
    #     ]
    #     return custom_urls + urls
    #
    # def update_categories(self, request, venue_id):
    #     venue = get_object_or_404(Venue, pk=venue_id)
    #     if not venue.access_token:
    #         self.message_user(request,
    #                           f'Заведение {venue.company_name} не имеет API токена.',
    #                           level=messages.ERROR)
    #         return redirect(f'/admin/account/venue/{venue_id}/change/')
    #
    #     pos_system_name = venue.pos_system.name.lower()
    #     pos_service = POSServiceFactory.get_service(pos_system_name, venue.access_token)
    #     categories_data = pos_service.get_categories()[1:]
    #
    #     created_count = 0
    #     for category_data in categories_data:
    #         existing_category = Category.objects.filter(
    #             external_id=category_data['category_id']
    #         ).exists()
    #
    #         if not existing_category:
    #             pos_service.create_new_category(venue, category_data)
    #             created_count += 1
    #
    #     if created_count > 0:
    #         self.message_user(request,
    #                           f"{created_count} категорий успешно созданы.",
    #                           level='success')
    #     else:
    #         self.message_user(request,
    #                           "Категории актуальны.",
    #                           level='success')
    #     return redirect(f'/admin/account/venue/{venue_id}/change/')

    # def update_products(self, request, venue_id):
    #     venue = get_object_or_404(Venue, pk=venue_id)
    #     if not venue.access_token:
    #         self.message_user(request,
    #                           f'Заведение {venue.company_name} не имеет API токена.',
    #                           level=messages.ERROR)
    #         return redirect(f'/admin/account/venue/{venue_id}/change/')
    #
    #     pos_system_name = venue.pos_system.name.lower()
    #     pos_service = POSServiceFactory.get_service(pos_system_name, venue.access_token)
    #     products_data = pos_service.get_products()
    #
    #     created_count = 0
    #     for product_data in products_data:
    #         existing_product = Product.objects.filter(
    #             external_id=product_data['product_id']
    #         ).exists()
    #
    #         if not existing_product:
    #             pos_service.create_new_product(venue, product_data)
    #             created_count += 1
    #
    #     if created_count > 0:
    #         self.message_user(request,
    #                           f"{created_count} продуктов успешно созданы.",
    #                           level='success')
    #     else:
    #         self.message_user(request,
    #                           "Продукты актуальны.",
    #                           level='success')
    #
    #     return redirect(f'/admin/account/venue/{venue_id}/change/')
