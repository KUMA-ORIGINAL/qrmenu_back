from django import forms
from unfold.contrib.import_export.forms import BaseImportForm
from unfold.widgets import UnfoldAdminFileFieldWidget, SELECT_CLASSES

from menu.models import Category
from venues.models import Spot, Venue


class ImportForm(BaseImportForm):
    venue = forms.ModelChoiceField(
        queryset=Venue.objects.all(),
        required=True,
        label="Заведение",
        widget=forms.Select(attrs={"class": " ".join(SELECT_CLASSES)})
    )
    spot = forms.ModelChoiceField(
        queryset=Spot.objects.all(),
        required=True,
        label="Точка",
        widget=forms.Select(attrs={"class": " ".join(SELECT_CLASSES)})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        label="Категория",
        widget=forms.Select(attrs={"class": " ".join(SELECT_CLASSES)})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resource"].widget.attrs["class"] = " ".join(
            [self.fields["resource"].widget.attrs.get("class", ""), *SELECT_CLASSES]
        )
        self.fields["import_file"].widget = UnfoldAdminFileFieldWidget(
            attrs=self.fields["import_file"].widget.attrs
        )
        self.fields["format"].widget.attrs["class"] = " ".join(
            [self.fields["format"].widget.attrs.get("class", ""), *SELECT_CLASSES]
        )

    class Media:
        js = ('menu/dependent_selects.js',)