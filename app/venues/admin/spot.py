from django.contrib import admin
from django import forms
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from unfold.decorators import action

from account.models import ROLE_OWNER, ROLE_ADMIN
from services.admin import BaseModelAdmin
from services.qr_service import add_qr_and_text_to_pdf_in_memory
from ..models import Spot


class SpotAdminForm(forms.ModelForm):
    class Meta:
        model = Spot
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['address'].widget.attrs.update({
            'placeholder': 'г. Бишкек, Пушкина 12'
        })
        self.fields['name'].widget.attrs.update({
            'placeholder': 'Например: Центральная точка'
        })


@admin.register(Spot)
class SpotAdmin(BaseModelAdmin):
    form = SpotAdminForm
    search_fields = ('name',)
    list_select_related = ('venue',)
    actions_detail = ('download_qr_actions_detail',)
    # change_form_before_template = 'venues/spot_change_form_before.html'

    @action(
        description="Cкачать qr-code (На вынос)",
        url_path="download_qr_actions_detail-url",
    )
    def download_qr_actions_detail(self, request, object_id):
        spot = get_object_or_404(Spot, pk=object_id)
        venue = spot.venue

        qr_url = f"https://imenu.kg/I/{venue.slug}/{spot.id}/s/"
        text_top = f"На вынос"

        output_pdf_stream = add_qr_and_text_to_pdf_in_memory(qr_url, text_top)

        response = HttpResponse(output_pdf_stream, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="qr_codes_spot_{spot.name}.pdf"'

        return response

    def get_list_filter(self, request):
        list_display = ('venue',)
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_display = ()
        return list_display

    def get_list_display(self, request):
        list_display = ('id', 'name', 'address', 'venue', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            list_display = ('name', 'address', 'detail_link')
        return list_display

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        elif request.user.role in [ROLE_OWNER, ROLE_ADMIN]:
            return [field for field in fields if field not in ['venue', 'external_id']]
        return fields

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_OWNER and not change:
            obj.venue = request.user.venue  # Заполняем venue владельца
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_OWNER:
            return qs.filter(venue=request.user.venue)
        elif request.user.role == ROLE_ADMIN:
            return qs.filter(users=request.user)
        return qs
