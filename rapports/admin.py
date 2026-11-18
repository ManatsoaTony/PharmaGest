from django.contrib import admin

from .models import JournalAudit


@admin.register(JournalAudit)
class JournalAuditAdmin(admin.ModelAdmin):
    list_display = ("date", "utilisateur", "action", "objet", "detail")
    list_filter = ("action",)
    search_fields = ("objet", "detail")
    # Le journal est en lecture seule : on ne falsifie pas la traçabilité.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
