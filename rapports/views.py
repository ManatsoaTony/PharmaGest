from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils import timezone

from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from utilisateurs.roles import GESTIONNAIRE, PHARMACIEN, roles_requis

from medicaments.models import Medicament
from stock.models import LotStock
from ventes.models import LigneVente, Vente


def dashboard(request):
    today = timezone.localdate()

    # Ventes du jour
    jour = Vente.objects.filter(date__date=today).aggregate(
        total=Coalesce(Sum("total"), Value(Decimal("0")), output_field=DecimalField()),
        nb=Count("id"),
    )

    # Ventes des 7 derniers jours
    debut = today - timedelta(days=6)
    semaine = Vente.objects.filter(date__date__gte=debut).aggregate(
        total=Coalesce(Sum("total"), Value(Decimal("0")), output_field=DecimalField()),
        nb=Count("id"),
    )

    # Stocks (lots valides uniquement)
    meds = Medicament.objects.filter(actif=True).annotate(
        stock=Coalesce(
            Sum("lots__quantite",
                filter=Q(lots__bloque=False, lots__date_peremption__gte=today)),
            0,
        )
    )
    nb_actifs = meds.count()
    ruptures = [m for m in meds if m.stock == 0]
    faibles = [m for m in meds if 0 < m.stock <= m.seuil_alerte]

    # Péremptions
    lots = LotStock.objects.filter(quantite__gt=0).select_related("medicament")
    perimes = lots.filter(date_peremption__lt=today)
    proches = lots.filter(date_peremption__gte=today,
                          date_peremption__lte=today + timedelta(days=30))

    # Produits les plus vendus
    top = (LigneVente.objects
           .values("medicament__nom_commercial")
           .annotate(qte=Sum("quantite"))
           .order_by("-qte")[:5])

    dernieres = Vente.objects.select_related("utilisateur")[:5]

    return render(request, "rapports/dashboard.html", {
        "jour": jour, "semaine": semaine, "nb_actifs": nb_actifs,
        "ruptures": ruptures, "faibles": faibles,
        "perimes": perimes, "proches": proches,
        "top": top, "dernieres": dernieres,
    })

def _pdf(titre, entetes, lignes, nom_fichier, positions):
    """Génère un tableau PDF simple avec pagination."""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{nom_fichier}"'
    p = canvas.Canvas(response, pagesize=A4)
    largeur, hauteur = A4

    def entete(y):
        p.setFont("Helvetica-Bold", 14)
        p.drawString(40, y, f"PharmaGest - {titre}")
        p.setFont("Helvetica", 9)
        p.drawString(40, y - 14, timezone.localtime().strftime("Édité le %d/%m/%Y %H:%M"))
        y -= 38
        p.setFont("Helvetica-Bold", 9)
        for x, texte in zip(positions, entetes):
            p.drawString(x, y, texte)
        p.line(40, y - 4, largeur - 40, y - 4)
        p.setFont("Helvetica", 9)
        return y - 18

    y = entete(hauteur - 40)
    for ligne in lignes:
        if y < 50:
            p.showPage()
            y = entete(hauteur - 40)
        for x, valeur in zip(positions, ligne):
            p.drawString(x, y, str(valeur)[:34])
        y -= 14
    if not lignes:
        p.drawString(40, y, "Aucune donnée.")
    p.showPage()
    p.save()
    return response


@roles_requis(GESTIONNAIRE, PHARMACIEN)
def rapport_stock(request):
    today = timezone.localdate()
    meds = Medicament.objects.filter(actif=True).annotate(
        stock=Coalesce(
            Sum("lots__quantite",
                filter=Q(lots__bloque=False, lots__date_peremption__gte=today)), 0)
    ).order_by("nom_commercial")
    lignes = []
    for m in meds:
        etat = "Rupture" if m.stock == 0 else ("Faible" if m.stock <= m.seuil_alerte else "OK")
        lignes.append((str(m), m.stock, m.seuil_alerte, etat))
    return _pdf("Rapport de stock", ["Médicament", "Stock", "Seuil", "État"],
                lignes, "rapport-stock.pdf", [40, 300, 370, 440])


@roles_requis(GESTIONNAIRE, PHARMACIEN)
def rapport_peremption(request):
    today = timezone.localdate()
    lots = (LotStock.objects.filter(quantite__gt=0,
                                    date_peremption__lte=today + timedelta(days=90))
            .select_related("medicament").order_by("date_peremption"))
    lignes = []
    for l in lots:
        etat = "PÉRIMÉ" if l.date_peremption < today else "Proche"
        lignes.append((str(l.medicament), l.numero_lot,
                       l.date_peremption.strftime("%d/%m/%Y"), l.quantite, etat))
    return _pdf("Produits périmés ou proches de la péremption (90 j)",
                ["Médicament", "Lot", "Péremption", "Qté", "État"],
                lignes, "rapport-peremption.pdf", [40, 240, 320, 400, 450])


@roles_requis(PHARMACIEN)
def rapport_ventes(request):
    ventes = Vente.objects.select_related("utilisateur").order_by("-date")[:300]
    lignes = [(v.numero, timezone.localtime(v.date).strftime("%d/%m/%Y %H:%M"),
               v.get_mode_paiement_display(), v.utilisateur or "-", f"{v.total:.0f} Ar")
              for v in ventes]
    return _pdf("Rapport des ventes", ["N°", "Date", "Paiement", "Caissier", "Total"],
                lignes, "rapport-ventes.pdf", [40, 120, 240, 340, 460])