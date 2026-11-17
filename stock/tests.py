from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from medicaments.models import Categorie, Medicament
from stock.models import LotStock, MouvementStock


class ReceptionTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user("gest", password="pass12345")
        self.client.login(username="gest", password="pass12345")
        cat = Categorie.objects.create(nom="Vitamines")
        self.med = Medicament.objects.create(
            nom_commercial="Vit C", categorie=cat, prix_achat=100, prix_vente=200)

    def _post(self, jours):
        return self.client.post(reverse("stock_reception"), {
            "medicament": self.med.pk, "numero_lot": "L100",
            "date_peremption": (date.today() + timedelta(days=jours)).isoformat(),
            "quantite_recue": 20,
        })

    def test_reception_augmente_le_stock_une_fois(self):
        self._post(200)
        lot = LotStock.objects.get(numero_lot="L100")
        self.assertEqual(lot.quantite, 20)
        self.assertEqual(MouvementStock.objects.filter(lot=lot, type="entree").count(), 1)

    def test_reception_lot_perime_refusee(self):
        self._post(-1)
        self.assertEqual(LotStock.objects.count(), 0)