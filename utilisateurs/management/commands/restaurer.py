import shutil
import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Restaure la base depuis une sauvegarde (.sqlite3) créée par « sauvegarde »"

    def add_arguments(self, parser):
        parser.add_argument("fichier", help="Chemin du fichier de sauvegarde .sqlite3")

    def handle(self, *args, **options):
        source = Path(options["fichier"])
        if not source.is_file():
            raise CommandError(f"Fichier introuvable : {source}")
        try:
            test = sqlite3.connect(source)
            test.execute("PRAGMA integrity_check").fetchone()
            test.execute("SELECT count(*) FROM django_migrations").fetchone()
            test.close()
        except sqlite3.Error as e:
            raise CommandError(f"Sauvegarde invalide : {e}")

        # Filet de sécurité : copie de la base actuelle avant restauration
        actuelle = Path(settings.DATABASES["default"]["NAME"])
        if actuelle.is_file():
            shutil.copy2(actuelle, actuelle.with_suffix(".avant-restauration"))

        connection.ensure_connection()
        origine = sqlite3.connect(source)
        try:
            origine.backup(connection.connection)
        finally:
            origine.close()
        self.stdout.write(self.style.SUCCESS(f"Base restaurée depuis {source}"))
