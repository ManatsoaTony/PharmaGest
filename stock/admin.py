from django.contrib import admin
from .models import LotStock, MouvementStock


@admin.register(LotStock)
class LotStockAdmin(admin.ModelAdmin):
    list_display = ("medicament", "numero_lot", "date_peremption", "quantite", "bloque")
    list_filter = ("bloque",)
    search_fields = ("numero_lot", "medicament__nom_commercial")


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ("date", "type", "quantite", "lot", "utilisateur")
    list_filter = ("type",)