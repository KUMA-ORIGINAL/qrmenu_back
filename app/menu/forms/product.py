from django import forms

from menu.forms import AiPhotoWidget
from menu.models import Product


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {"product_photo": AiPhotoWidget()}
    class Media:
        js = ("admin/js/ai_image_buttons.js",)