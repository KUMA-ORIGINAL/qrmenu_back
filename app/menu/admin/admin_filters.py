from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

from account.models import ROLE_OWNER
from menu.models import Category


class CategoryFilter(SimpleListFilter):
    title = _('Категории')
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        if request.user.role in [ROLE_OWNER]:
            categories = Category.objects.filter(venue=request.user.venue)
        else:
            categories = Category.objects.all()
        return [(category.id, category.category_name) for category in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category_id=self.value())
        return queryset