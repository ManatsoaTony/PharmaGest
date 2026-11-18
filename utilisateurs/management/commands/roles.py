from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from utilisateurs.roles import CAISSIER, GESTIONNAIRE, PHARMACIEN


class Command(BaseCommand):
    help = "Crée les groupes et 3 comptes de démonstration"

    def handle(self, *args, **options):
        for nom in (PHARMACIEN, CAISSIER, GESTIONNAIRE):
            Group.objects.get_or_create(name=nom)

        demo = [("pharmacien", PHARMACIEN), ("caissier", CAISSIER),
                ("gestionnaire", GESTIONNAIRE)]
        for username, groupe in demo:
            u, cree = User.objects.get_or_create(username=username)
            if cree:
                u.set_password("Pharma2026!")
                u.save()
            u.groups.add(Group.objects.get(name=groupe))
        self.stdout.write(self.style.SUCCESS(
            "Groupes créés. Comptes demo : pharmacien / caissier / gestionnaire (mdp : Pharma2026!)"))