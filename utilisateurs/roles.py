from functools import wraps

from django.core.exceptions import PermissionDenied

PHARMACIEN = "Pharmacien"
CAISSIER = "Caissier"
GESTIONNAIRE = "Gestionnaire de stock"


def roles_requis(*roles):
    """Autorise les superusers et les membres des groupes indiqués."""
    def decorateur(vue):
        @wraps(vue)
        def enveloppe(request, *args, **kwargs):
            u = request.user
            if u.is_superuser or u.groups.filter(name__in=roles).exists():
                return vue(request, *args, **kwargs)
            raise PermissionDenied
        return enveloppe
    return decorateur