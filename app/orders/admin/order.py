from django.contrib import admin

from unfold.admin import TabularInline
from unfold.contrib.filters.admin import RangeNumericFilter, RangeDateTimeFilter
from unfold.decorators import display

from services.admin import BaseModelAdmin
from venues.models import Venue, Table
from ..models import Order, OrderProduct, Client


class OrderProductInline(TabularInline):
    model = OrderProduct
    extra = 0
    fields = ('product', 'count', 'price', 'total_price')
    readonly_fields = ('product', 'count', 'price', 'total_price')


@admin.register(Order)
class OrderAdmin(BaseModelAdmin):
    compressed_fields = True
    list_display = ('id', 'phone', 'display_status', 'display_service_mode',
                    'total_price', 'created_at', 'detail_link')
    search_fields = ('phone',)
    list_filter = ('venue', 'status', 'service_mode',
                   ("total_price", RangeNumericFilter),
                   ("created_at", RangeDateTimeFilter),)
    inlines = [OrderProductInline]

    @display(
        description=("Статус заказа"),
        ordering="status",
        label={
            'Принят': "success",  # green
            'Новый': "info",  # blue
            'Отменён': "danger",  # red
        },
    )
    def display_status(self, obj):
        if obj.status == 0:
            return 'Новый'
        elif obj.status == 1:
            return 'Принят'
        elif obj.status == 7:
            return 'Отменён'

    @display(
        description=("Режим обслуживания"),
        label=True
    )
    def display_service_mode(self, obj):
        if obj.service_mode == 1:
            return 'На месте'
        elif obj.service_mode == 2:
            return 'Самовывоз'
        elif obj.service_mode == 3:
            return 'Доставка'

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role == 'owner':
            return [field for field in fields if field not in ['venue', 'external_id']]
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        venue = Venue.objects.filter(
            user=request.user).first() if request.user.role == 'owner' else None

        if venue:
            if db_field.name == 'client':
                kwargs["queryset"] = Client.objects.filter(venue=venue)
            elif db_field.name == 'table':
                kwargs["queryset"] = Table.objects.filter(venue=venue)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner':
            return qs.filter(venue__user=request.user)

