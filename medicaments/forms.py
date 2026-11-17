from django import forms
from .models import Categorie, Medicament

class MedicamentForm(forms.ModelForm):
    class Meta:
        model = Medicament
        fields = [
            "nom_commercial", "denomination_generique", "categorie", "forme",
            "dosage", "laboratoire", "code_barres", "photo",
            "prix_achat", "prix_vente", "seuil_alerte", "actif",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != "actif":
                field.widget.attrs["class"] = "form-control"
        self.fields["actif"].widget.attrs["class"] = "form-check-input"

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and hasattr(photo, "content_type"):
            if photo.content_type not in ("image/jpeg", "image/png"):
                raise forms.ValidationError("Formats autorisés : JPG et PNG.")
            if photo.size > 2 * 1024 * 1024:
                raise forms.ValidationError("La taille maximale est de 2 Mo.")
        return photo

    def clean_code_barres(self):
        # Évite le doublon "" : un code vide doit être enregistré comme NULL
        return self.cleaned_data.get("code_barres") or None

    def clean(self):
        data = super().clean()
        achat, vente = data.get("prix_achat"), data.get("prix_vente")
        if achat is not None and vente is not None and vente < achat:
            self.add_error("prix_vente", "Le prix de vente est inférieur au prix d'achat.")
        return data
        
class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ["nom", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"