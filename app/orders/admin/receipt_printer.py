from django.contrib import admin, messages

from account.models import ROLE_OWNER, ROLE_ADMIN
from services.admin import BaseModelAdmin
from ..models import ReceiptPrinter
from ..services import send_test_receipt


@admin.register(ReceiptPrinter)
class ReceiptPrinterAdmin(BaseModelAdmin):
    search_fields = ('name',)

    actions = ["send_test_receipt_action"]

    def send_test_receipt_action(self, request, queryset):
        """
        Админ-экшен: отправить тестовый чек на выбранные принтеры
        """
        success_count = 0
        fail_count = 0

        for printer in queryset:
            if send_test_receipt(printer):
                success_count += 1
            else:
                fail_count += 1

        if success_count:
            self.message_user(
                request,
                f"Тестовые чеки успешно отправлены на {success_count} принтер(ов).",
                level=messages.SUCCESS,
            )
        if fail_count:
            self.message_user(
                request,
                f"Не удалось отправить чек на {fail_count} принтер(ов).",
                level=messages.ERROR,
            )

    send_test_receipt_action.short_description = "Отправить тестовый чек на принтеры"

    def get_list_filter(self, request):
        list_filter = ()
        if request.user.is_superuser:
            list_filter = ('venue',)
        return list_filter

    def get_list_display(self, request):
        list_display = ('id', 'name', 'venue', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER]:
            list_display = ('name', 'detail_link')
        return list_display

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role == ROLE_OWNER:
            return [field for field in fields if field not in ['venue',]]
        return fields

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_OWNER and not change:
            obj.venue = request.user.venue
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_OWNER:
            return qs.filter(venue=request.user.venue)
        return qs
