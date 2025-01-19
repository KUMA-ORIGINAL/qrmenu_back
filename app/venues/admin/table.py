from django.contrib import admin

from unfold.admin import ModelAdmin as UnfoldModelAdmin

from ..models import Table


@admin.register(Table)
class TableAdmin(UnfoldModelAdmin):
    list_display = ('table_num', 'table_title', 'table_shape', 'spot_id', 'venue')
    search_fields = ('table_num', 'table_title')
    list_filter = ('table_shape',)
    fields = ('table_num', 'table_title', 'spot_id', 'table_shape')
