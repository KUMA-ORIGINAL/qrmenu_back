from django.contrib import admin

from unfold.admin import TabularInline
from unfold.contrib.filters.admin import RangeNumericFilter, RangeDateTimeFilter
from unfold.decorators import display

from account.models import ROLE_ADMIN, ROLE_OWNER
from services.admin import BaseModelAdmin
from venues.models import Table, Spot
from ..models import Order, OrderProduct, Client


class OrderProductInline(TabularInline):
    model = OrderProduct
    extra = 0
    fields = ('product', 'count', 'price', 'total_price', 'modificator',)
    readonly_fields = ('product', 'count', 'price', 'total_price', 'modificator',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product').prefetch_related('modificator')


@admin.register(Order)
class OrderAdmin(BaseModelAdmin):
    compressed_fields = True
    search_fields = ('phone',)
    list_select_related = ('venue', 'spot', 'client', 'table')
    inlines = [OrderProductInline]
    list_per_page = 50
    list_before_template = "menu/change_list_before.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['changelist_url'] = 'admin:orders_order_changelist'
        if request.user.role == ROLE_OWNER:
            extra_context['spots'] = Spot.objects.filter(venue=request.user.venue)
            extra_context['filter_key'] = 'spot__id__exact'
        return super(OrderAdmin, self).changelist_view(request, extra_context=extra_context)

    @display(
        description="Статус заказа",
        ordering="status",
        label={
            'Заказ оформлен': "info",  # Новый — синий
            'Ожидает оплату': "secondary",
            'Готовим заказ': "primary",  # Принят — синий (или другой стиль)
            'Заказ готов': "warning",  # Готов — жёлтый
            'Заказ выполнен': "success",  # Выполнен — зелёный
            'Отменён': "danger",  # Отменён — красный
        },
    )
    def display_status(self, obj):
        return obj.get_status_display()

    @display(
        description="Режим обслуживания",
        label=True
    )
    def display_service_mode(self, obj):
        if obj.service_mode == 1:
            return 'На месте'
        elif obj.service_mode == 2:
            return 'Самовывоз'
        elif obj.service_mode == 3:
            return 'Доставка'

    def get_list_filter(self, request):
        list_filter = ('venue', 'status', 'service_mode',
                       ("total_price", RangeNumericFilter),
                       ("created_at", RangeDateTimeFilter),)
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_OWNER:
            list_filter = ('status', 'service_mode',
                           ("total_price", RangeNumericFilter),
                           ("created_at", RangeDateTimeFilter),)
        return list_filter

    def get_list_display(self, request):
        list_display = ()
        if request.user.is_superuser:
            list_display = ('id', 'phone', 'display_status', 'display_service_mode',
                            'total_price', 'tips_price', 'bonus', 'created_at', 'venue', 'detail_link')
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_display = ('id', 'phone', 'display_status', 'display_service_mode',
                            'total_price', 'tips_price', 'bonus', 'created_at', 'detail_link')
        return list_display

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return [field for field in fields if field not in ['venue', 'external_id']]
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            venue = request.user.venue
            if venue:
                if db_field.name == 'client':
                    kwargs["queryset"] = Client.objects.filter(venue=venue)
                elif db_field.name == 'table':
                    kwargs["queryset"] = Table.objects.filter(venue=venue)
                elif db_field.name == 'spot':
                    kwargs["queryset"] = Spot.objects.filter(venue=venue)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_OWNER:
            return qs.filter(venue=request.user.venue)
        elif request.user.role == ROLE_ADMIN:
            return qs.filter(spot=request.user.spot)
