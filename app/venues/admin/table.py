from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from unfold.decorators import action

from services.admin import BaseModelAdmin
from services.qr_service import add_qr_and_text_to_pdf_in_memory
from ..models import Table, Spot, Hall


@admin.register(Table)
class TableAdmin(BaseModelAdmin):
    list_display = ('id', 'table_num', 'table_title', 'table_shape', 'hall', 'spot', 'venue',
                    'detail_link')
    search_fields = ('table_num', 'table_title')
    list_filter = ('table_shape',)

    actions_detail = ('download_qr_actions_detail',)

    @action(
        description="Cкачать qr-code",
        url_path="download_qr_actions_detail-url",
    )
    def download_qr_actions_detail(self, request, object_id):
        table = get_object_or_404(Table, pk=object_id)
        venue = table.venue
        spot = table.spot
        hall = table.hall

        qr_url = f"https://imenu.kg/{venue.company_name}/{spot.name}/{hall.id}/{table.table_num}"
        text_top = f"{table.table_num} стол"

        output_pdf_stream = add_qr_and_text_to_pdf_in_memory(qr_url, text_top)

        response = HttpResponse(output_pdf_stream, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="qr_codes_table_{table.table_num}.pdf"'

        return response

    def get_list_display(self, request):
        list_display = ('id', 'table_num', 'table_title', 'table_shape', 'hall', 'spot', 'venue',
                        'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == 'owner' or request.user.role == 'admin':
            list_display = ('table_num', 'table_title', 'table_shape', 'hall', 'spot', 'detail_link')
        return list_display

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role == 'owner':
            return [field for field in fields if field not in ['venue', 'external_id']]
        elif request.user.role == 'admin':
            return [field for field in fields if field not in ['venue', 'spot', 'external_id']]
        return fields

    def save_model(self, request, obj, form, change):
        if request.user.role == 'owner' and not change:
            obj.venue = request.user.venue
        elif request.user.role == 'admin' and not change:
            obj.venue = request.user.venue
            obj.spot = request.user.spot
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.role == 'owner':
            venue = request.user.venue
            if venue:
                if db_field.name == 'spot':
                    kwargs["queryset"] = Spot.objects.filter(venue=venue)
                elif db_field.name == 'hall':
                    kwargs["queryset"] = Hall.objects.filter(venue=venue)
        if request.user.role == 'admin':
            spot = request.user.spot
            if spot:
                if db_field.name == 'hall':
                    kwargs["queryset"] = Hall.objects.filter(spot=spot)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner':
            return qs.filter(venue=request.user.venue)
        elif request.user.role == 'admin':
            return qs.filter(spot=request.user.spot)
        return qs
