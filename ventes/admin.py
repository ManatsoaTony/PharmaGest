from django.contrib import admin
from .models import LigneVente, RetourVente, Vente


class LigneInline(admin.TabularInline):
    model = LigneVente
    extra = 0
    readonly_fields = ("medicament", "lot", "quantite", "prix_unitaire")
    can_delete = False


@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ("numero", "date", "total", "mode_paiement", "utilisateur")
    inlines = [LigneInline]

@admin.register(RetourVente)
class RetourVenteAdmin(admin.ModelAdmin):
    list_display = ("date", "ligne", "quantite", "remis_en_stock", "utilisateur")