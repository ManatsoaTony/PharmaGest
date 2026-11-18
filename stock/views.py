from utilisateurs.roles import GESTIONNAIRE, PHARMACIEN, roles_requis
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render
from django.utils import timezone

from medicaments.models import Medicament
from rapports.audit import journaliser
from .forms import ReceptionForm
from .models import LotStock, MouvementStock


def apercu_stock(request):
    """Stock par médicament (lots valides uniquement) + alertes."""
    today = timezone.localdate()
    medicaments = Medicament.objects.filter(actif=True).annotate(
        stock=Coalesce(
            Sum("lots__quantite",
                filter=Q(lots__bloque=False, lots__date_peremption__gte=today)),
            0,
        )
    ).order_by("nom_commercial")

    ruptures = [m for m in medicaments if m.stock == 0]
    faibles = [m for m in medicaments if 0 < m.stock <= m.seuil_alerte]

    limite = today + timezone.timedelta(days=30)
    lots_actifs = LotStock.objects.filter(quantite__gt=0).select_related("medicament")
    perimes = lots_actifs.filter(date_peremption__lt=today)
    proches = lots_actifs.filter(date_peremption__gte=today, date_peremption__lte=limite)

    return render(request, "stock/apercu.html", {
        "medicaments": medicaments,
        "ruptures": ruptures,
        "faibles": faibles,
        "perimes": perimes,
        "proches": proches,
    })


def liste_lots(request):
    lots = LotStock.objects.select_related("medicament", "fournisseur")
    return render(request, "stock/lots.html", {"lots": lots})


@roles_requis(GESTIONNAIRE, PHARMACIEN)
def reception(request):
    """Réception de marchandise : crée le lot ET le mouvement dans une transaction."""
    if request.method == "POST":
        form = ReceptionForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                lot = form.save(commit=False)
                lot.quantite = lot.quantite_recue
                lot.save()
                MouvementStock.objects.create(
                    lot=lot,
                    type="entree",
                    quantite=lot.quantite_recue,
                    motif="Réception de marchandise",
                    utilisateur=request.user if request.user.is_authenticated else None,
                )
                journaliser(request.user, "Réception directe", lot.numero_lot,
                            f"+{lot.quantite_recue} x {lot.medicament}")
            messages.success(request, f"Lot {lot.numero_lot} réceptionné (+{lot.quantite_recue}).")
            return redirect("stock_apercu")
    else:
        form = ReceptionForm()
    return render(request, "stock/reception.html", {"form": form})


def mouvements(request):
    liste = MouvementStock.objects.select_related("lot__medicament", "utilisateur")[:100]
    return render(request, "stock/mouvements.html", {"mouvements": liste})


@roles_requis(GESTIONNAIRE, PHARMACIEN)
def inventaire(request):
    """Inventaire physique : on saisit les quantités comptées, les écarts
    deviennent des corrections tracées (mouvement + journal d'audit)."""
    lots = (LotStock.objects.filter(quantite__gt=0)
            .select_related("medicament").order_by("medicament__nom_commercial", "date_peremption"))
    if request.method == "POST":
        comptes, erreurs = {}, []
        for lot in lots:
            brut = request.POST.get(f"compte_{lot.pk}", "").strip()
            if brut == "":
                continue  # lot non compté : inchangé
            try:
                valeur = int(brut)
            except ValueError:
                valeur = -1
            if valeur < 0:
                erreurs.append(f"Quantité invalide pour {lot} (entier positif ou nul attendu).")
            else:
                comptes[lot.pk] = valeur
        if erreurs:
            for e in erreurs:
                messages.error(request, e)
        else:
            nb = 0
            with transaction.atomic():
                for lot in LotStock.objects.select_for_update().filter(pk__in=comptes):
                    ecart = comptes[lot.pk] - lot.quantite
                    if ecart == 0:
                        continue
                    avant = lot.quantite
                    lot.quantite = comptes[lot.pk]
                    lot.save(update_fields=["quantite"])
                    MouvementStock.objects.create(
                        lot=lot, type="correction", quantite=ecart,
                        motif=f"Inventaire physique : théorique {avant}, compté {lot.quantite}",
                        utilisateur=request.user,
                    )
                    journaliser(request.user, "Inventaire physique", lot.numero_lot,
                                f"{lot.medicament} : {avant} -> {lot.quantite} ({ecart:+d})")
                    nb += 1
            messages.success(request, f"Inventaire enregistré : {nb} écart(s) corrigé(s).")
            return redirect("stock_apercu")
    return render(request, "stock/inventaire.html", {"lots": lots})
