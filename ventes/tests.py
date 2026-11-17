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
        return self.client.post(reverse("vente_valider"),
                                {"mode_paiement": "especes"})

    def test_vente_diminue_le_stock_une_seule_fois(self):
        lot = self._lot(20)
        self._vendre(3)
        lot.refresh_from_db()
        self.assertEqual(lot.quantite, 17)
        self.assertEqual(Vente.objects.count(), 1)
        self.assertEqual(Vente.objects.first().total, Decimal("1500"))

    def test_vente_superieure_au_stock_refusee(self):
        lot = self._lot(5)
        self._vendre(10)
        lot.refresh_from_db()
        self.assertEqual(lot.quantite, 5)
        self.assertEqual(Vente.objects.count(), 0)

    def test_lot_perime_non_vendable(self):
        lot = self._lot(20, jours=-5)
        self._vendre(1)
        lot.refresh_from_db()
        self.assertEqual(lot.quantite, 20)
        self.assertEqual(Vente.objects.count(), 0)

    def test_lot_bloque_non_vendable(self):
        self._lot(20, bloque=True)
        self._vendre(1)
        self.assertEqual(Vente.objects.count(), 0)

    def test_fefo_lot_le_plus_proche_en_premier(self):
        proche = self._lot(10, jours=30, numero="L-PROCHE")
        loin = self._lot(10, jours=300, numero="L-LOIN")
        self._vendre(4)
        proche.refresh_from_db()
        loin.refresh_from_db()
        self.assertEqual(proche.quantite, 6)
        self.assertEqual(loin.quantite, 10)

    def test_quantite_nulle_refusee(self):
        self._lot(20)
        self.client.post(reverse("panier_ajouter"),
                         {"medicament": self.med.pk, "quantite": 0})
        self.assertEqual(self.client.session.get("panier", {}), {})

    def test_double_validation_impossible(self):
        lot = self._lot(20)
        self._vendre(3)
        self.client.post(reverse("vente_valider"), {"mode_paiement": "especes"})
        lot.refresh_from_db()
        self.assertEqual(lot.quantite, 17)
        self.assertEqual(Vente.objects.count(), 1)

    def test_vente_cree_un_mouvement_de_sortie(self):
        lot = self._lot(20)
        self._vendre(3)
        m = MouvementStock.objects.get(lot=lot, type="sortie")
        self.assertEqual(m.quantite, -3)
        self.assertEqual(m.utilisateur, self.user)

    def test_prix_fige_dans_la_ligne_de_vente(self):
        self._lot(20)
        self._vendre(2)
        self.med.prix_vente = Decimal("999")
        self.med.save()
        ligne = Vente.objects.first().lignes.first()
        self.assertEqual(ligne.prix_unitaire, Decimal("500"))

    def test_acces_sans_connexion_redirige(self):
        self.client.logout()
        r = self.client.get(reverse("caisse"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login/", r.url)