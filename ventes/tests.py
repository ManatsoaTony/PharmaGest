from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from medicaments.models import Categorie, Medicament
from stock.models import LotStock, MouvementStock
from ventes.models import Vente


class VenteTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("caissier", password="pass12345")
        self.client.login(username="caissier", password="pass12345")
        cat = Categorie.objects.create(nom="Antalgiques")
        self.med = Medicament.objects.create(
            nom_commercial="Paracetamol", categorie=cat,
            prix_achat=Decimal("300"), prix_vente=Decimal("500"), seuil_alerte=5)

    def _lot(self, qte=20, jours=365, numero="L001", bloque=False):
        return LotStock.objects.create(
            medicament=self.med, numero_lot=numero,
            date_peremption=date.today() + timedelta(days=jours),
            quantite_recue=qte, quantite=qte, bloque=bloque)

    def _vendre(self, qte):
        self.client.post(reverse("panier_ajouter"),
                         {"medicament": self.med.pk, "quantite": qte})
        return