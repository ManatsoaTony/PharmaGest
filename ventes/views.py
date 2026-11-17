from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from medicaments.models import Medicament
from stock.models import LotStock, MouvementStock
from .models import LigneVente, Vente


class StockInsuffisant(Exception):
    pass


def _lots_vendables(med):
    """Lots non bloqués, non périmés, avec du stock, triés FEFO."""
    return LotStock.objects.filter(
        medicament=med, bloque=False,
        date_peremption__gte=date.today(), quantite__gt=0,
    ).order_by("date_peremption")


def _dispo(med):
    return _lots_vendables(med).aggregate(t=Coalesce(Sum("quantite"), 0))["t"]


def caisse(request):
    panier = request.session.get("panier", {})
    lignes, total = [], Decimal("0")
    for med_id, qte in panier.items():
        med = Medicament.objects.get(pk=med_id)
        sous_total = med.prix_vente * qte
        total += sous_total
        lignes.append({"med": med, "qte": qte, "sous_total": sous_total})

    today = date.today()
    medicaments = Medicament.objects.filter(actif=True).annotate(
        stock=Coalesce(Sum(
            "lots__quantite",
            filter=Q(lots__bloque=False, lots__date_peremption__gte=today),
        ), 0)
    ).filter(stock__gt=0).order_by("nom_commercial")

    return render(request, "ventes/caisse.html", {
        "lignes": lignes, "total": total,
        "medicaments": medicaments, "modes": Vente.MODES,
    })


@require_POST
def panier_ajouter(request):
    med = get_object_or_404(Medicament, pk=request.POST.get("medicament"), actif=True)
    try:
        qte = int(request.POST.get("quantite", "0"))
    except ValueError:
        qte = 0
    if qte <= 0:
        messages.error(request, "La quantité doit être supérieure à zéro.")
        return redirect("caisse")

    panier = request.session.setdefault("panier", {})
    deja = panier.get(str(med.pk), 0)
    if qte + deja > _dispo(med):
        messages.error(request, f"Stock insuffisant pour {med} (disponible : {_dispo(med)}).")
        return redirect("caisse")

    panier[str(med.pk)] = deja + qte
    request.session.modified = True
    return redirect("caisse")


@require_POST
def panier_retirer(request, pk):
    panier = request.session.get("panier", {})
    panier.pop(str(pk), None)
    request.session.modified = True
    return redirect("caisse")


@require_POST
def valider(request):
    panier = request.session.get("panier")
    if not panier:  # empêche aussi la double validation
        messages.error(request, "Le panier est vide.")
        return redirect("caisse")

    mode = request.POST.get("mode_paiement", "especes")
    if mode not in dict(Vente.MODES):
        mode = "especes"
    user = request.user if request.user.is_authenticated else None

    try:
        with transaction.atomic():
            vente = Vente.objects.create(utilisateur=user, mode_paiement=mode)
            total = Decimal("0")
            for med_id, qte in panier.items():
                med = Medicament.objects.get(pk=med_id)
                restant = qte
                for lot in _lots_vendables(med).select_for_update():
                    if restant == 0:
                        break
                    prise = min(lot.quantite, restant)
                    lot.quantite -= prise
                    lot.save(update_fields=["quantite"])
                    LigneVente.objects.create(
                        vente=vente, medicament=med, lot=lot,
                        quantite=prise, prix_unitaire=med.prix_vente,
                    )
                    MouvementStock.objects.create(
                        lot=lot, type="sortie", quantite=-prise,
                        motif=f"Vente {vente.numero}", utilisateur=user,
                    )
                    total += prise * med.prix_vente
                    restant -= prise
                if restant > 0:
                    raise StockInsuffisant(f"Stock insuffisant pour {med}.")
            vente.total = total
            vente.save(update_fields=["total"])
    except StockInsuffisant as e:
        messages.error(request, str(e))
        return redirect("caisse")

    request.session["panier"] = {}
    messages.success(request, f"Vente {vente.numero} enregistrée.")
    return redirect("vente_detail", pk=vente.pk)


def liste_ventes(request):
    ventes = Vente.objects.select_related("utilisateur")[:100]
    return render(request, "ventes/liste.html", {"ventes": ventes})


def vente_detail(request, pk):
    vente = get_object_or_404(
        Vente.objects.prefetch_related("lignes__medicament", "lignes__lot"), pk=pk
    )
    return render(request, "ventes/detail.html", {"vente": vente})

def recu_pdf(request, pk):
    vente = get_object_or_404(
        Vente.objects.prefetch_related("lignes__medicament", "lignes__lot"), pk=pk
    )
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="recu-{vente.numero}.pdf"'

    p = canvas.Canvas(response, pagesize=A5)
    largeur, hauteur = A5
    y = hauteur - 40

    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, y, "PharmaGest - Reçu de vente")
    y -= 22
    p.setFont("Helvetica", 10)
    p.drawString(40, y, f"N° {vente.numero}")
    y -= 14
    p.drawString(40, y, timezone.localtime(vente.date).strftime("Date : %d/%m/%Y %H:%M"))
    y -= 14
    p.drawString(40, y, f"Paiement : {vente.get_mode_paiement_display()}")
    y -= 14
    p.drawString(40, y, f"Caissier : {vente.utilisateur or '-'}")
    y -= 24

    p.setFont("Helvetica-Bold", 9)
    p.drawString(40, y, "Médicament")
    p.drawString(200, y, "Lot")
    p.drawRightString(300, y, "Qté")
    p.drawRightString(350, y, "P.U.")
    p.drawRightString(largeur - 40, y, "Total")
    y -= 4
    p.line(40, y, largeur - 40, y)
    y -= 14

    p.setFont("Helvetica", 9)
    for l in vente.lignes.all():
        if y < 70:
            p.showPage()
            p.setFont("Helvetica", 9)
            y = hauteur - 40
        p.drawString(40, y, str(l.medicament)[:28])
        p.drawString(200, y, l.lot.numero_lot[:12])
        p.drawRightString(300, y, str(l.quantite))
        p.drawRightString(350, y, f"{l.prix_unitaire:.0f}")
        p.drawRightString(largeur - 40, y, f"{l.sous_total:.0f}")
        y -= 14

    y -= 6
    p.line(40, y, largeur - 40, y)
    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(largeur - 40, y, f"TOTAL : {vente.total:.0f} Ar")
    y -= 30
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(40, y, "Merci de votre visite.")

    p.showPage()
    p.save()
    return response