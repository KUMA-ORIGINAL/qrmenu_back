from django import forms

from menu.forms.widgets import AiPhotoWidget
from menu.models import Category


class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"
        widgets = {"category_photo": AiPhotoWidget()}

    class Media:
        js = ("admin/js/ai_image_buttons.js",)  # наш JS подключим
