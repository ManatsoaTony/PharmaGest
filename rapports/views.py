from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils import timezone

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