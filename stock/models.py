from django.conf import settings
from datetime import timedelta
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class LotStock(models.Model):
    medicament = models.ForeignKey(
        "medicaments.Medicament", on_delete=models.PROTECT, related_name="lots"
    )
    fournisseur = models.ForeignKey(
        "fournisseurs.Fournisseur", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="lots",
    )
    numero_lot = models.CharField(max_length=50)
    date_peremption = models.DateField()
    quantite_recue = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    quantite = models.PositiveIntegerField(help_text="Quantité disponible")
    bloque = models.BooleanField(default=False)
    date_reception = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_peremption"]  # FEFO : le plus proche de la péremption d'abord
        constraints = [
            models.UniqueConstraint(
                fields=["medicament", "numero_lot"], name="lot_unique_par_medicament"
            )
        ]

    def __str__(self):
        return f"{self.medicament} - lot {self.numero_lot}"

    @property
    def est_perime(self):
        return self.date_peremption < timezone.localdate()

    @property
    def proche_peremption(self):
        today = timezone.localdate()
        return today <= self.date_peremption <= today + timezone.timedelta(days=30)

    @property
    def vendable(self):
        return not self.bloque and not self.est_perime and self.quantite > 0


class MouvementStock(models.Model):
    TYPES = [
        ("entree", "Entrée (réception)"),
        ("sortie", "Sortie (vente)"),
        ("retour", "Retour"),
        ("correction", "Correction d'inventaire"),
    ]
    lot = models.ForeignKey(LotStock, on_delete=models.PROTECT, related_name="mouvements")
    type = models.CharField(max_length=12, choices=TYPES)
    quantite = models.IntegerField(help_text="Positif = entrée, négatif = sortie")
    motif = models.CharField(max_length=200, blank=True)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.get_type_display()} {self.quantite} - {self.lot}"