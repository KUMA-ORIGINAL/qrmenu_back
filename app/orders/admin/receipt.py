from django.contrib import admin

from account.models import ROLE_OWNER  # Импортируем роли пользователей
from services.admin import BaseModelAdmin  # Наследуем от базового админа
from orders.models import Receipt  # Модель чеков


@admin.register(Receipt)
class ReceiptAdmin(BaseModelAdmin):
    search_fields = ('order__id', 'printer_name')

    def get_list_filter(self, request):
        """Фильтры в админке: суперюзер видит все, владелец только свои"""
        list_filter = ()
        if request.user.is_superuser:
            list_filter = ('receipt_printer', 'created_at')
        return list_filter

    def get_list_display(self, request):
        """Отображаемые колонки в списке чеков"""
        list_display = ('id', 'order', 'receipt_printer', 'amount', 'created_at')
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_OWNER:
            list_display = ('order', 'receipt_printer', 'amount', 'created_at')
        return list_display

    def get_fields(self, request, obj=None):
        """Какие поля показывать в форме редактирования"""
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role == ROLE_OWNER:
            return [field for field in fields if field not in ['payload', 'receipt_printer']]
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_OWNER:
            return qs.filter(order__venue=request.user.venue)
        return qs
