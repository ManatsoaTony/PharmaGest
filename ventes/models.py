from django.conf import settings
from django.db import models


class Vente(models.Model):
    MODES = [
        ("especes", "Espèces"),
        ("mobile_money", "Mobile money"),
        ("autre", "Autre"),
    ]
    numero = models.CharField(max_length=20, unique=True, null=True, blank=True)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    mode_paiement = models.CharField(max_length=20, choices=MODES, default="especes")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.numero:
            self.numero = f"V{self.pk:06d}"
            super().save(update_fields=["numero"])

    def __str__(self):
        return self.numero or f"Vente {self.pk}"


class LigneVente(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name="lignes")
    medicament = models.ForeignKey("medicaments.Medicament", on_delete=models.PROTECT)
    lot = models.ForeignKey("stock.LotStock", on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField()
    # Prix figé au moment de la vente (RG12)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire