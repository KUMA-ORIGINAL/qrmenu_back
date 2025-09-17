from django.contrib import admin
from django.db import models
from unfold.admin import TabularInline

from account.models import ROLE_OWNER, ROLE_ADMIN
from services.admin import BaseModelAdmin
from ..models import Client, ClientVenueProfile


class ClientVenueProfileInline(TabularInline):
    model = ClientVenueProfile
    extra = 0
    fields = ('venue', 'bonus', 'total_payed_sum', 'created_at')
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return qs.filter(venue=request.user.venue)
        return qs.none()


@admin.register(Client)
class ClientAdmin(BaseModelAdmin):
    compressed_fields = True
    search_fields = ('phone_number', 'firstname', 'lastname')

    inlines = [ClientVenueProfileInline]

    def get_list_display(self, request, obj=None):
        list_display = ('id', 'firstname', 'lastname', 'phone_number', 'email', 'bonus_amount', 'detail_link')
        return list_display

    def get_list_filter(self, request, obj=None):
        list_filter = ('client_sex', 'city')
        return list_filter

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        # владельцам/админам нельзя менять venue напрямую (оно будет через профили)
        if request.user.is_superuser:
            return fields
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return [field for field in fields if field not in ['external_id']]
        return fields

    def bonus_amount(self, obj):
        request = self.request_cache  # сохраним request в get_queryset
        venue = getattr(request.user, "venue", None)
        if venue:
            profile = obj.venue_profiles.filter(venue=venue).first()
            return profile.bonus if profile else 0
        else:
            # для суперпользователя показываем сумму всех бонусов
            return obj.venue_profiles.aggregate(total=models.Sum('bonus')).get('total') or 0

    bonus_amount.short_description = "Бонусы"

    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related("venue_profiles")
        # сохраним request в админ для использования в bonus_amount
        self.request_cache = request
        if request.user.is_superuser:
            return qs
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return qs.filter(venue_profiles__venue=request.user.venue).distinct()
        return qs.none()
