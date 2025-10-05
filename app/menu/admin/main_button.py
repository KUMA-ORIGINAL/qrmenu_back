from django.contrib import admin
from django import forms

from account.models import ROLE_ADMIN, ROLE_OWNER
from services.admin import BaseModelAdmin
from ..models import MainButton


class MainButtonForm(forms.ModelForm):
    """Форма для динамического скрытия полей в зависимости от button_type"""

    class Meta:
        model = MainButton
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        button_type = cleaned_data.get("button_type")
        section = cleaned_data.get("section")
        category = cleaned_data.get("category")

        # Разрешаем только то, что соответствует выбранному типу
        if button_type == "section" and not section:
            raise forms.ValidationError("Выберите раздел для кнопки типа 'Раздел'")
        if button_type == "category" and not category:
            raise forms.ValidationError("Выберите категорию для кнопки типа 'Категория'")

        # Не разрешаем заполнять оба
        if section and category:
            raise forms.ValidationError("Можно указать либо раздел, либо категорию, но не оба одновременно")

        return cleaned_data


@admin.register(MainButton)
class MainButtonAdmin(BaseModelAdmin):
    form = MainButtonForm
    list_display = ("venue", "order", "button_type", "linked_object_display", "detail_link")
    list_filter = ("venue", "button_type")
    ordering = ("venue", "order")
    autocomplete_fields = ("section", "category")

    class Media:
        js = ("menu/mainbutton_visibility.js",)

    def linked_object_display(self, obj):
        if obj.button_type == "section" and obj.section:
            return f"Раздел: {obj.section}"
        elif obj.button_type == "category" and obj.category:
            return f"Категория: {obj.category}"
        return "-"
    linked_object_display.short_description = "Привязка"

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {
                "fields": ("venue", "order", "button_type", "section", "category"),
            }),
        )

        if not request.user.is_superuser and request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            fieldsets = (
                (None, {
                    "fields": ("order", "button_type", "section", "category"),
                }),
            )
        return fieldsets

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("venue", "section", "category")
        if request.user.is_superuser:
            return qs
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return qs.filter(venue=request.user.venue)
        return qs.none()

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ("venue", "button_type")
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return ("button_type",)
        return ()

    def save_model(self, request, obj, form, change):
        """Присваиваем venue владельца или админа автоматически"""
        if not request.user.is_superuser and request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            obj.venue = request.user.venue
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        """Нельзя добавлять кнопки вручную"""
        # superuser может, если нужно, можно убрать
        if request.user.is_superuser:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        """Нельзя удалять кнопки"""
        if request.user.is_superuser:
            return True
        return False