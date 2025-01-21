from django.contrib import admin

from unfold.admin import ModelAdmin as UnfoldModelAdmin, TabularInline
from unfold.contrib.filters.admin import RangeNumericFilter, RangeDateTimeFilter

from venues.models import Venue, Table
from ..models import Order, OrderProduct, Client


class OrderProductInline(TabularInline):
    model = OrderProduct
    extra = 0
    fields = ('product', 'count', 'price', 'total_price')
    readonly_fields = ('product', 'count', 'price', 'total_price')


@admin.register(Order)
class OrderAdmin(UnfoldModelAdmin):
    compressed_fields = True
    list_display = ('id', 'phone', 'status', 'service_mode', 'total_price', 'created_at')
    list_display_links = ('id', 'phone')
    search_fields = ('phone',)
    list_filter = ('venue', 'status', 'service_mode',
                   ("total_price", RangeNumericFilter),
                   ("created_at", RangeDateTimeFilter),)
    inlines = [OrderProductInline]

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
