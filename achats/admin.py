from django.contrib import admin
from .models import CommandeAchat, LigneAchat, ReceptionAchat


class LigneAchatInline(admin.TabularInline):
    model = LigneAchat
    extra = 0


@admin.register(CommandeAchat)
class CommandeAchatAdmin(admin.ModelAdmin):
    list_display = ("numero", "fournisseur", "statut", "date_creation")
    inlines = [LigneAchatInline]


admin.site.register(ReceptionAchat)