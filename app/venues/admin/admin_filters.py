from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

from account.models import ROLE_OWNER
from venues.models import Spot


class SpotFilter(SimpleListFilter):
    title = _('Spot')
    parameter_name = 'spot'

    def lookups(self, request, model_admin):
        if request.user.role in [ROLE_OWNER]:
            spots = Spot.objects.filter(venue=request.user.venue)
        else:
            spots = Spot.objects.all()
        return [(spot.id, spot.name) for spot in spots]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(spot_id=self.value())
        return queryset