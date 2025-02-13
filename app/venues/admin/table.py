from io import BytesIO

from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from unfold.decorators import action

from services.admin import BaseModelAdmin
from services.qr_service import create_pdf_with_qr
from ..models import Table, Venue, Spot


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

        data1 = f"https://imenu.kg/{venue.company_name}/{spot.id}/{hall.id}/{table.table_num}"
        data2 = f"https://imenu.kg/{venue.company_name}/{spot.id}/{hall.id}/{table.table_num}"
        logo_path = 'static/logo.jpg'  # Путь к логотипу
        text_top1 = "Отсканируйте код 1"
        text_bottom1 = "Текст для кода 1"
        text_top2 = "Отсканируйте код 2"
        text_bottom2 = "Текст для кода 2"

        # Создаем PDF
        pdf_buffer = BytesIO()
        create_pdf_with_qr(pdf_buffer, data1, data2, logo_path, text_top1, text_bottom1, text_top2,
                           text_bottom2)

        pdf_buffer.seek(0)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="qr_codes_table_{table.table_num}.pdf"'

        return response

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role == 'owner':
            return [field for field in fields if field not in ['venue', 'external_id']]
        return fields

    def save_model(self, request, obj, form, change):
        if request.user.role == 'owner' and not change:
            obj.venue = Venue.objects.filter(user=request.user).first()  # Заполняем venue владельца
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'spot' and request.user.role == 'owner':
            venue = Venue.objects.filter(user=request.user).first()
            kwargs["queryset"] = Spot.objects.filter(venue=venue)  # Ограничиваем категории
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner':
            return qs.filter(venue__user=request.user)
        return qs
