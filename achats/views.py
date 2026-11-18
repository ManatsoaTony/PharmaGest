from datetime import date
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from fournisseurs.models import Fournisseur
from medicaments.models import Medicament
from stock.models import LotStock, MouvementStock
from utilisateurs.roles import GESTIONNAIRE, PHARMACIEN, roles_requis

from .models import CommandeAchat, LigneAchat, ReceptionAchat

ROLES = (GESTIONNAIRE, PHARMACIEN)


def _entier(valeur):
    try:
        return int(valeur)
    except (TypeError, ValueError):
        return 0


@roles_requis(*ROLES)
def liste(request):
    commandes = CommandeAchat.objects.select_related("fournisseur")
    return render(request, "achats/liste.html", {"commandes": commandes})


@roles_requis(*ROLES)
def creer(request):
    fournisseurs = Fournisseur.objects.filter(actif=True)
    if request.method == "POST":
        f = get_object_or_404(Fournisseur, pk=request.POST.get("fournisseur"), actif=True)
        c = CommandeAchat.objects.create(fournisseur=f, utilisateur=request.user)
        messages.success(request, f"Commande {c.numero} créée en brouillon.")
        return redirect("achat_detail", pk=c.pk)
    return render(request, "achats/creer.html", {"fournisseurs": fournisseurs})


@roles_requis(*ROLES)
def detail(request, pk):
    c = get_object_or_404(
        CommandeAchat.objects.select_related("fournisseur").prefetch_related("lignes__medicament"),
        pk=pk,
    )
    medicaments = Medicament.objects.filter(actif=True)
    return render(request, "achats/detail.html", {"c": c, "medicaments": medicaments})


@roles_requis(*ROLES)
@require_POST
def ajouter_ligne(request, pk):
    c = get_object_or_404(CommandeAchat, pk=pk)
    if c.statut != "brouillon":
        messages.error(request, "Seul un brouillon peut être modifié.")
        return redirect("achat_detail", pk=pk)
    med = get_object_or_404(Medicament, pk=request.POST.get("medicament"), actif=True)
    qte = _entier(request.POST.get("quantite"))
    try:
        prix = Decimal(request.POST.get("prix_achat") or med.prix_achat)
    except InvalidOperation:
        prix = Decimal("-1")
    if qte <= 0 or prix < 0:
        messages.error(request, "Quantité et prix doivent être valides (quantité > 0).")
        return redirect("achat_detail", pk=pk)
    ligne, cree = LigneAchat.objects.get_or_create(
        commande=c, medicament=med, defaults={"quantite": qte, "prix_achat": prix}
    )
    if not cree:
        ligne.quantite += qte
        ligne.prix_achat = prix
        ligne.save()
    return redirect("achat_detail", pk=pk)


@roles_requis(*ROLES)
@require_POST
def supprimer_ligne(request, pk):
    ligne = get_object_or_404(LigneAchat, pk=pk, commande__statut="brouillon")
    commande_pk = ligne.commande_id
    ligne.delete()
    return redirect("achat_detail", pk=commande_pk)


@roles_requis(*ROLES)
@require_POST
def valider(request, pk):
    c = get_object_or_404(CommandeAchat, pk=pk)
    if c.statut != "brouillon" or not c.lignes.exists():
        messages.error(request, "Impossible de valider : brouillon vide ou déjà validé.")
    else:
        c.statut = "commandee"
        c.save(update_fields=["statut"])
        messages.success(request, f"Commande {c.numero} validée. Le stock n'est pas modifié avant la réception.")
    return redirect("achat_detail", pk=pk)


@roles_requis(*ROLES)
@require_POST
def annuler(request, pk):
    c = get_object_or_404(CommandeAchat, pk=pk)
    if c.statut in ("brouillon", "commandee"):
        c.statut = "annulee"
        c.save(update_fields=["statut"])
        messages.success(request, "Commande annulée.")
    else:
        messages.error(request, "Une commande déjà réceptionnée ne peut pas être annulée.")
    return redirect("achat_detail", pk=pk)


@roles_requis(*ROLES)
def recevoir(request, pk):
    ligne = get_object_or_404(
        LigneAchat.objects.select_related("commande", "medicament"), pk=pk
    )
    c = ligne.commande
    if c.statut not in ("commandee", "partielle"):
        messages.error(request, "Cette commande n'est pas réceptionnable.")
        return redirect("achat_detail", pk=c.pk)

    if request.method == "POST":
        qte = _entier(request.POST.get("quantite"))
        numero_lot = request.POST.get("numero_lot", "").strip()
        try:
            peremption = date.fromisoformat(request.POST.get("date_peremption", ""))
        except ValueError:
            peremption = None

        if qte <= 0 or qte > ligne.restant:
            messages.error(request, f"Quantité invalide (reste à recevoir : {ligne.restant}).")
        elif not numero_lot or peremption is None:
            messages.error(request, "Numéro de lot et date de péremption obligatoires.")
        elif peremption < date.today():
            messages.error(request, "Lot déjà périmé : réception refusée.")
        else:
            with transaction.atomic():
                ligne = LigneAchat.objects.select_for_update().get(pk=ligne.pk)
                if qte > ligne.restant:  # protection contre une double réception
                    messages.error(request, "Quantité déjà réceptionnée.")
                    return redirect("achat_detail", pk=c.pk)
                lot = LotStock.objects.select_for_update().filter(
                    medicament=ligne.medicament, numero_lot=numero_lot
                ).first()
                if lot:
                    lot.quantite += qte
                    lot.quantite_recue += qte
                    lot.save(update_fields=["quantite", "quantite_recue"])
                else:
                    lot = LotStock.objects.create(
                        medicament=ligne.medicament, fournisseur=c.fournisseur,
                        numero_lot=numero_lot, date_peremption=peremption,
                        quantite_recue=qte, quantite=qte,
                    )
                ReceptionAchat.objects.create(
                    ligne=ligne, lot=lot, quantite=qte, utilisateur=request.user
                )
                MouvementStock.objects.create(
                    lot=lot, type="entree", quantite=qte,
                    motif=f"Réception commande {c.numero}", utilisateur=request.user,
                )
                ligne.quantite_recue += qte
                ligne.save(update_fields=["quantite_recue"])
                c.maj_statut()
            messages.success(request, f"{qte} unité(s) réceptionnée(s) (lot {numero_lot}).")
            return redirect("achat_detail", pk=c.pk)

    return render(request, "achats/recevoir.html", {"ligne": ligne, "c": c})