from django.contrib import admin

from unfold.admin import ModelAdmin as UnfoldModelAdmin

from ..models import Spot

@admin.register(Spot)
class SpotAdmin(UnfoldModelAdmin):
    list_display = ('name', 'address', 'venue')

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role == 'owner':
            return [field for field in fields if field != 'venue']
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner':
            return qs.filter(venue__user=request.user)
        return qs