from django.contrib import admin
from django.urls import reverse
from mptt.admin import MPTTModelAdmin

from ..models import Category
from ..services.poster import PosterMenuService


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('category_name', 'venue',
                    'parent', 'category_hidden', 'level')
    list_filter = ('venue', 'category_hidden', 'level')
    search_fields = ('category_name',)
    list_per_page = 20

    mptt_level_indent = 20
    mptt_show_nodedata = True

    fieldsets = (
        (None, {
            'fields': ('category_name', 'category_photo', 'parent', 'venue')
        }),
        ('Дополнительная информация', {
            'fields': ('category_hidden', 'level', 'visible',),
            'classes': ('collapse',)
        }),
    )

    actions = ['get_data_from_poster']

    def get_data_from_poster(self, request, queryset):
        """Метод для получения данных из Poster и обновления/создания категорий."""
        # Получаем токен из какого-то источника или настроек
        api_token = '937308:61056601e15495b60c8305295a55da92'  # Ваш токен
        poster_service = PosterMenuService(api_token)
        poster_url = 'https://joinposter.com'

        updated_count = 0
        created_count = 0

        try:
            # Получаем все категории с Poster
            poster_categories = poster_service.get_categories()

            # Пробегаем по всем категориям из Poster
            for poster_category in poster_categories:
                # Проверяем, существует ли категория в базе данных
                existing_category = Category.objects.filter(
                    category_id=poster_category['category_id']).first()

                if existing_category:
                    updated_count += 1
                else:
                    # Если категория не найдена, создаём новую
                    Category.objects.create(
                        category_id=poster_category['category_id'],
                        category_name=poster_category['category_name'],
                        category_photo=poster_url+poster_category['category_photo'],
                        category_hidden=poster_category['category_hidden'],
                        venue=queryset.first().venue,
                        # Используем первое заведение из выбранных, или определите логику по-другому
                    )
                    created_count += 1

            # Выводим сообщения о количестве обновленных и созданных категорий
            if updated_count > 0:
                self.message_user(request,  "Категории актуальны.",
                                  level='success')
            if created_count > 0:
                self.message_user(request, f"{created_count} категорий успешно созданы.",
                                  level='success')

        except Exception as e:
            self.message_user(request, f"Ошибка при получении данных из Poster: {e}", level='error')

    get_data_from_poster.short_description = "Получить данные из Poster и обновить/создать категории"

