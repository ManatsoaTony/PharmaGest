from django.conf import settings
from django.db import models


class CommandeAchat(models.Model):
    STATUTS = [
        ("brouillon", "Brouillon"),
        ("commandee", "Commandée"),
        ("partielle", "Partiellement réceptionnée"),
        ("complete", "Entièrement réceptionnée"),
        ("annulee", "Annulée"),
    ]
    numero = models.CharField(max_length=20, unique=True, null=True, blank=True)
    fournisseur = models.ForeignKey(
        "fournisseurs.Fournisseur", on_delete=models.PROTECT, related_name="commandes"
    )
    statut = models.CharField(max_length=12, choices=STATUTS, default="brouillon")
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_creation"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.numero:
            self.numero = f"C{self.pk:06d}"
            super().save(update_fields=["numero"])

    def __str__(self):
        return self.numero or f"Commande {self.pk}"

    @property
    def total(self):
        return sum(l.sous_total for l in self.lignes.all())

    def maj_statut(self):
        lignes = list(self.lignes.all())
        if lignes and all(l.quantite_recue >= l.quantite for l in lignes):
            self.statut = "complete"
        elif any(l.quantite_recue > 0 for l in lignes):
            self.statut = "partielle"
        self.save(update_fields=["statut"])


class LigneAchat(models.Model):
    commande = models.ForeignKey(CommandeAchat, on_delete=models.CASCADE, related_name="lignes")
    medicament = models.ForeignKey("medicaments.Medicament", on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField()
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_recue = models.PositiveIntegerField(default=0)

    @property
    def sous_total(self):
        return self.quantite * self.prix_achat

    @property
    def restant(self):
        return self.quantite - self.quantite_recue


class ReceptionAchat(models.Model):
    ligne = models.ForeignKey(LigneAchat, on_delete=models.PROTECT, related_name="receptions")
    lot = models.ForeignKey("stock.LotStock", on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField()
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]