from django import forms

from menu.forms import AiPhotoWidget
from menu.models import Section


class SectionAdminForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = "__all__"
        widgets = {"photo": AiPhotoWidget()}
    class Media:
        js = ("admin/js/ai_image_buttons.js",)
