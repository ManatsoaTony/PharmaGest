from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from medicaments.models import Categorie, Medicament
from rapports.models import JournalAudit
from stock.models import LotStock, MouvementStock
from datetime import date, timedelta


def utilisateur(nom, groupe=None, superuser=False):
    if superuser:
        return User.objects.create_superuser(nom, password="x")
    u = User.objects.create_user(nom, password="x")
    u.groups.add(Group.objects.get_or_create(name=groupe)[0])
    return u


class ExtensionsTests(TestCase):
    def setUp(self):
        self.pharma = utilisateur("pharma", "Pharmacien")
        self.caissier = utilisateur("caisse", "Caissier")
        cat = Categorie.objects.create(nom="Antalgiques")
        self.med = Medicament.objects.create(
            nom_commercial="Paracetamol", categorie=cat, prix_achat=100, prix_vente=200)
        self.lot = LotStock.objects.create(
            medicament=self.med, numero_lot="L1", quantite_recue=10, quantite=10,
            date_peremption=date.today() + timedelta(days=200))

    def test_pdf_achats_autorise_pharmacien_refuse_caissier(self):
        self.client.force_login(self.pharma)
        r = self.client.get(reverse("rapport_achats"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")
        self.client.force_login(self.caissier)
        self.assertEqual(self.client.get(reverse("rapport_achats")).status_code, 403)

    def test_inventaire_corrige_ecart_et_trace(self):
        self.client.force_login(self.pharma)
        self.client.post(reverse("stock_inventaire"), {f"compte_{self.lot.pk}": "7"})
        self.lot.refresh_from_db()
        self.assertEqual(self.lot.quantite, 7)
        m = MouvementStock.objects.get(lot=self.lot, type="correction")
        self.assertEqual(m.quantite, -3)
        self.assertTrue(JournalAudit.objects.filter(action="Inventaire physique").exists())

    def test_inventaire_refuse_valeur_negative(self):
        self.client.force_login(self.pharma)
        self.client.post(reverse("stock_inventaire"), {f"compte_{self.lot.pk}": "-5"})
        self.lot.refresh_from_db()
        self.assertEqual(self.lot.quantite, 10)
        self.assertFalse(MouvementStock.objects.filter(type="correction").exists())

    def test_inventaire_interdit_au_caissier(self):
        self.client.force_login(self.caissier)
        self.assertEqual(self.client.get(reverse("stock_inventaire")).status_code, 403)

    def test_journal_reserve_au_pharmacien(self):
        self.client.force_login(self.caissier)
        self.assertEqual(self.client.get(reverse("journal")).status_code, 403)
        self.client.force_login(self.pharma)
        self.assertEqual(self.client.get(reverse("journal")).status_code, 200)
