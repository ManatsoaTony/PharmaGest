from django.db import models


class Fournisseur(models.Model):
    nom = models.CharField("Nom / raison sociale", max_length=150)
    adresse = models.CharField(max_length=255, blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    numero_fiscal = models.CharField("Numéro fiscal (NIF/STAT)", max_length=50, blank=True)
    contact_principal = models.CharField(max_length=100, blank=True)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return self.nom