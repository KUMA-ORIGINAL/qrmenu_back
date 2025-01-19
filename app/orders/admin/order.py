from django.contrib import admin

from unfold.admin import ModelAdmin as UnfoldModelAdmin, TabularInline

from ..models import Order, OrderProduct


class OrderProductInline(TabularInline):
    model = OrderProduct
    extra = 0
    fields = ('product', 'count', 'price', 'total_price')


@admin.register(Order)
class OrderAdmin(UnfoldModelAdmin):
    list_display = ('id', 'phone', 'status', 'service_mode', 'total_price', 'created_at')
    list_display_links = ('id', 'phone')
    inlines = [OrderProductInline]
