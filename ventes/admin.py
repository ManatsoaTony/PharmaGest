from django.contrib import admin
from .models import LigneVente, Vente


class LigneInline(admin.TabularInline):
    model = LigneVente
    extra = 0
    readonly_fields = ("medicament", "lot", "quantite", "prix_unitaire")
    can_delete = False


@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ("numero", "date", "total", "mode_paiement", "utilisateur")
    inlines = [LigneInline]