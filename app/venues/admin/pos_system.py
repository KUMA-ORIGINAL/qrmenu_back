from django.contrib import admin

from unfold.admin import ModelAdmin as UnfoldModelAdmin

from ..models import POSSystem


@admin.register(POSSystem)
class POSSystemAdmin(UnfoldModelAdmin):
    list_display = ('name',)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role == 'owner':
            return [field for field in fields if field != 'pos_system']
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner':
            return qs.filter(user=request.user)
        return qs
