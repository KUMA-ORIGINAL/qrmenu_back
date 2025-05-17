from django import forms

from .models import Table

class TableAdminForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = '__all__'

    class Media:
        js = ('admin/js/filter_halls_by_spot.js',)
