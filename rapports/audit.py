from .models import JournalAudit


def journaliser(user, action, objet="", detail=""):
    """Enregistre une opération sensible dans le journal d'audit."""
    JournalAudit.objects.create(
        utilisateur=user if getattr(user, "is_authenticated", False) else None,
        action=action, objet=str(objet)[:100], detail=str(detail)[:255],
    )
