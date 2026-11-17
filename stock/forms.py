from django import forms
from django.utils import timezone

from .models import LotStock


class ReceptionForm(forms.ModelForm):
    class Meta:
        model = LotStock
        fields = ["medicament", "fournisseur", "numero_lot",
                  "date_peremption", "quantite_recue"]
        widgets = {"date_peremption": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["medicament"].queryset = self.fields["medicament"].queryset.filter(actif=True)
        self.fields["fournisseur"].queryset = self.fields["fournisseur"].queryset.filter(actif=True)

    def clean_date_peremption(self):
        d = self.cleaned_data["date_peremption"]
        if d < timezone.localdate():
            raise forms.ValidationError("Ce lot est déjà périmé : réception refusée.")
        return d