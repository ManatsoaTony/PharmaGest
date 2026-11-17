from django.contrib import admin
from .models import Categorie, Medicament


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    search_fields = ("nom",)


@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):
    list_display = ("nom_commercial", "categorie", "prix_vente", "seuil_alerte", "actif")
    list_filter = ("categorie", "actif", "forme")
    search_fields = ("nom_commercial", "code_barres")