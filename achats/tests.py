from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from achats.models import CommandeAchat, LigneAchat
from fournisseurs.models import Fournisseur
from medicaments.models import Categorie, Medicament
from stock.models import LotStock


class AchatTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_superuser("g", password="pass12345")
        self.client.login(username="g", password="pass12345")
        cat = Categorie.objects.create(nom="Vit")
        self.med = Medicament.objects.create(
            nom_commercial="VitC", categorie=cat, prix_achat=100, prix_vente=200)
        f = Fournisseur.objects.create(nom="F1")
        self.c = CommandeAchat.objects.create(fournisseur=f)
        self.ligne = LigneAchat.objects.create(
            commande=self.c, medicament=self.med, quantite=20, prix_achat=100)

    def _recevoir(self, qte, lot="A1", jours=200):
        return self.client.post(reverse("achat_recevoir", args=[self.ligne.pk]), {
            "quantite": qte, "numero_lot": lot,
            "date_peremption": (date.today() + timedelta(days=jours)).isoformat()})

    def test_commande_ne_modifie_pas_le_stock(self):
        self.client.post(reverse("achat_valider", args=[self.c.pk]))
        self.assertEqual(LotStock.objects.count(), 0)

    def test_reception_partielle_puis_complete(self):
        self.client.post(reverse("achat_valider", args=[self.c.pk]))
        self._recevoir(12, "A1")
        self.c.refresh_from_db()
        self.assertEqual(self.c.statut, "partielle")
        self._recevoir(8, "A2")
        self.c.refresh_from_db()
        self.assertEqual(self.c.statut, "complete")
        self.assertEqual(sum(l.quantite for l in LotStock.objects.all()), 20)

    def test_reception_superieure_refusee(self):
        self.client.post(reverse("achat_valider", args=[self.c.pk]))
        self._recevoir(25)
        self.assertEqual(LotStock.objects.count(), 0)

    def test_reception_lot_perime_refusee(self):
        self.client.post(reverse("achat_valider", args=[self.c.pk]))
        self._recevoir(5, jours=-1)
        self.assertEqual(LotStock.objects.count(), 0)

    def test_reception_impossible_sur_brouillon(self):
        self._recevoir(5)
        self.assertEqual(LotStock.objects.count(), 0)