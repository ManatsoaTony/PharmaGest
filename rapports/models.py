from django.conf import settings
from django.db import models


class JournalAudit(models.Model):
    """Trace des opérations sensibles (qui, quoi, quand)."""
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=60)
    objet = models.CharField(max_length=100, blank=True)
    detail = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "entrée du journal d'audit"
        verbose_name_plural = "journal d'audit"

    def __str__(self):
        return f"{self.date:%d/%m/%Y %H:%M} {self.action} {self.objet}".strip()
