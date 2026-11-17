from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from fournisseurs.models import Fournisseur
from medicaments.models import Categorie, Medicament
from stock.models import LotStock, MouvementStock


class Command(BaseCommand):
    help = "Charge des données fictives pour tester PharmaGest"

    @transaction.atomic
    def handle(self, *args, **options):
        cats = {n: Categorie.objects.get_or_create(nom=n)[0]
                for n in ["Antalgiques", "Vitamines", "Antiseptiques", "Antibiotiques"]}

        f1, _ = Fournisseur.objects.get_or_create(
            nom="MediSupply Madagascar", defaults={"telephone": "0341100000"})
        f2, _ = Fournisseur.objects.get_or_create(
            nom="PharmaDistrib", defaults={"telephone": "0321100000"})

        meds = [
            ("Paracétamol", "500 mg", "Antalgiques", 300, 500, 20),
            ("Ibuprofène", "400 mg", "Antalgiques", 400, 700, 15),
            ("Vitamine C", "1000 mg", "Vitamines", 800, 1200, 10),
            ("Bétadine", "10 %", "Antiseptiques", 2500, 3500, 5),
            ("Amoxicilline", "500 mg", "Antibiotiques", 1500, 2200, 10),
        ]
        today = date.today()
        for i, (nom, dosage, cat, achat, vente, seuil) in enumerate(meds):
            m, _ = Medicament.objects.get_or_create(
                nom_commercial=nom, dosage=dosage,
                defaults={"categorie": cats[cat], "prix_achat": achat,
                          "prix_vente": vente, "seuil_alerte": seuil})
            if not m.lots.exists():
                lot = LotStock.objects.create(
                    medicament=m, fournisseur=f1 if i % 2 else f2,
                    numero_lot=f"L{i + 1:03d}",
                    date_peremption=today + timedelta(days=[400, 300, 200, 100, 20][i]),
                    quantite_recue=50, quantite=50)
                MouvementStock.objects.create(
                    lot=lot, type="entree", quantite=50, motif="Données fictives")

        self.stdout.write(self.style.SUCCESS("Données fictives chargées."))
