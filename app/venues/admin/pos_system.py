from django.contrib import admin


from services.admin import BaseModelAdmin
from ..models import POSSystem


@admin.register(POSSystem)
class POSSystemAdmin(BaseModelAdmin):
    list_display = ('name', 'detail_link')

