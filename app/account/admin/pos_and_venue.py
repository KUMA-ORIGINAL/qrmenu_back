from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import path

from menu.models import Category
from ..models import Venue, POSSystem
from ..services.pos_service_factory import POSServiceFactory


@admin.register(POSSystem)
class POSSystemAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    change_form_template = 'admin/account/venue/category_change_form.html'
    list_display = ('name', 'pos_system', 'api_token')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:venue_id>/get_categories/', self.admin_site.admin_view(self.get_categories),
                 name='get_categories'),
        ]
        return custom_urls + urls

    def get_categories(self, request, venue_id):
        venue = get_object_or_404(Venue, pk=venue_id)
        if not venue.api_token:
            self.message_user(request, f'Заведение {venue.name} не имеет API токена.',
                              level=messages.ERROR)
            return redirect(f'/admin/account/venue/{venue_id}/change/')
        try:
            pos_service = POSServiceFactory.get_service(venue.pos_system, venue.api_token)
            data = pos_service.get_categories()
            if data:
                if self.update_categories(request, venue, data, pos_service):
                    pass
                else:
                    self.message_user(request, f'Данные для {venue.name} не изменились.',
                                      level=messages.WARNING)
            else:
                self.message_user(request, f'Не удалось получить данные для {venue.name}.',
                                  level=messages.ERROR)
        except Exception as e:
            self.message_user(request, f'Ошибка при получении данных для {venue.name}: {e}',
                              level='error')
        return redirect(f'/admin/account/venue/{venue_id}/change/')

    def update_categories(self, request, venue, data, pos_service):
        pos_url = pos_service.BASE_URL
        created_count = 0
        updated_count = 0
        for poster_category in data:
            existing_category = Category.objects.filter(
                category_id=poster_category['category_id']
            ).first()
            if existing_category:
                updated_count += 1
            else:
                # Если категория не найдена, создаём новую
                Category.objects.create(
                    category_id=poster_category['category_id'],
                    category_name=poster_category['category_name'],
                    category_photo=pos_url + poster_category['category_photo'],
                    category_hidden=poster_category['category_hidden'],
                    venue=venue,
                )
                created_count += 1
        if updated_count > 0:
            self.message_user(request, "Категории актуальны.",
                              level='success')
        if created_count > 0:
            self.message_user(request, f"{created_count} категорий успешно созданы.",
                              level='success')
        return created_count > 0 or updated_count > 0
