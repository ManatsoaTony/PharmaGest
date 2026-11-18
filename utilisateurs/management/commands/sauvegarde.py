import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Sauvegarde la base SQLite (et les photos) dans le dossier backups/"

    def add_arguments(self, parser):
        parser.add_argument("--garder", type=int, default=10,
                            help="Nombre de sauvegardes conservées (défaut : 10)")
        parser.add_argument("--dossier", default=None, help="Dossier de destination")

    def handle(self, *args, **options):
        if connection.vendor != "sqlite":
            raise CommandError("Cette commande ne gère que SQLite.")
        dossier = Path(options["dossier"]) if options["dossier"] else settings.BASE_DIR / "backups"
        dossier.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Copie cohérente via l'API de sauvegarde de SQLite (sûre même serveur allumé)
        dest = dossier / f"pharmagest-{stamp}.sqlite3"
        connection.ensure_connection()
        cible = sqlite3.connect(dest)
        try:
            connection.connection.backup(cible)
        finally:
            cible.close()
        self.stdout.write(self.style.SUCCESS(f"Base sauvegardée : {dest}"))

        media = settings.MEDIA_ROOT
        if media and Path(media).is_dir():
            archive = dossier / f"pharmagest-{stamp}-media.zip"
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
                for f in Path(media).rglob("*"):
                    if f.is_file():
                        z.write(f, f.relative_to(media))
            self.stdout.write(self.style.SUCCESS(f"Photos sauvegardées : {archive}"))

        # Rotation : on ne garde que les N dernières sauvegardes
        for motif in ("pharmagest-*.sqlite3", "pharmagest-*-media.zip"):
            anciennes = sorted(dossier.glob(motif))
            for f in anciennes[:-options["garder"]] if options["garder"] > 0 else []:
                f.unlink()
