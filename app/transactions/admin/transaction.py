from django.contrib import admin

from account.models import ROLE_OWNER, ROLE_ADMIN
from orders.models import Order

from services.admin import BaseModelAdmin
from ..models import Transaction


@admin.register(Transaction)
class TransactionAdmin(BaseModelAdmin):
    ordering = ("-created_at",)
    readonly_fields = ("created_at", 'updated_at')
    date_hierarchy = "created_at"
    list_filter_submit = True

    def get_list_display(self, request):
        list_display = ("id",  "total_price", "status", "created_at", 'updated_at', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_display = ("total_price", "status", "created_at", 'updated_at', 'detail_link')
        return list_display

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {
                "fields": ("total_price", "status", 'order', 'json_data',)
            }),
            ('Дополнительная информация', {
                "fields": ("created_at", 'updated_at'),
                "classes": ("collapse",)
            }),
        )
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            pass
        return fieldsets

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            venue = request.user.venue
            if venue:
                if db_field.name == 'order':
                    kwargs["queryset"] = Order.objects.filter(venue=venue)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return qs.filter(order__venue=request.user.venue)
