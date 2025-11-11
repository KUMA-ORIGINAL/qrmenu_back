from django.contrib import admin

from services.admin import BaseModelAdmin
from venues.models import VenueAnalytics


@admin.register(VenueAnalytics)
class VenueAnalyticsAdmin(BaseModelAdmin):
    list_display = (
        'date',
        'venue',
        'table',
        'unique_count',
        'detail_link'
    )
    list_filter = ('venue', 'date', 'table')
    date_hierarchy = 'date'
    ordering = ('-date',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('venue', 'table')
