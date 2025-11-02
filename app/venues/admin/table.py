from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from unfold.decorators import action

from account.models import ROLE_OWNER, ROLE_ADMIN
from services.admin import BaseModelAdmin
from services.qr_service import add_qr_and_text_to_pdf_in_memory
from ..forms import TableAdminForm
from ..models import Table, Spot, Hall


@admin.register(Table)
class TableAdmin(BaseModelAdmin):
    form = TableAdminForm
    search_fields = ('table_num', 'table_title')
    list_select_related = ('spot', 'hall', 'venue')

    actions_detail = ('download_qr_actions_detail',)
    list_before_template = "menu/change_list_before.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['changelist_url'] = 'admin:venues_table_changelist'
        if request.user.role == ROLE_OWNER:
            extra_context['spots'] = Spot.objects.filter(venue=request.user.venue)
            extra_context['filter_key'] = 'spot__id__exact'
        return super(TableAdmin, self).changelist_view(request, extra_context=extra_context)

    @action(
        description="Cкачать qr-code",
        url_path="download_table_qr_actions_detail-url",
    )
    def download_qr_actions_detail(self, request, object_id):
        table = get_object_or_404(Table, pk=object_id)
        venue = table.venue
        spot = table.spot

        qr_url = f"https://imenu.kg/{venue.slug}/{spot.id}/{table.id}/"

        text_top_ru = venue.table_qr_text_ru
        text_top_kg = venue.table_qr_text_ky

        color = venue.color_theme

        output_pdf_stream = add_qr_and_text_to_pdf_in_memory(
            qr_url, text_top_ru, text_top_kg,
            table_num=table.table_num,
            input_pdf_color=color,
            is_table=True
        )

        response = HttpResponse(output_pdf_stream, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="qr_codes_table_{table.table_num}.pdf"'

        return response

    def get_list_filter(self, request):
        list_filter = ()
        if request.user.is_superuser:
            list_filter = ('venue',)
        elif request.user.role in [ROLE_ADMIN]:
            list_filter = ('table_shape',)
        return list_filter

    def get_list_display(self, request):
        list_display = ('id', 'table_num', 'table_title', 'table_shape', 'hall', 'spot', 'venue',
                        'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_display = ('table_num', 'table_title', 'table_shape', 'hall', 'spot', 'detail_link')
        return list_display

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role == ROLE_OWNER:
            return [field for field in fields if field not in ['venue', 'external_id']]
        elif request.user.role == ROLE_ADMIN:
            return [field for field in fields if field not in ['venue', 'spot', 'external_id']]
        return fields

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_OWNER and not change:
            obj.venue = request.user.venue
        elif request.user.role == ROLE_ADMIN and not change:
            obj.venue = request.user.venue
            obj.spot = request.user.spot
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.role == ROLE_OWNER:
            venue = request.user.venue
            if venue:
                if db_field.name == 'spot':
                    kwargs["queryset"] = Spot.objects.filter(venue=venue)
                elif db_field.name == 'hall':
                    kwargs["queryset"] = Hall.objects.filter(venue=venue)
        if request.user.role == ROLE_ADMIN:
            spot = request.user.spot
            if spot:
                if db_field.name == 'hall':
                    kwargs["queryset"] = Hall.objects.filter(spot=spot)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_OWNER:
            return qs.filter(venue=request.user.venue)
        elif request.user.role == ROLE_ADMIN:
            return qs.filter(spot=request.user.spot)
        return qs
