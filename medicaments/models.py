from django.core.validators import MinValueValidator
from django.db import models


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"

    def __str__(self):
        return self.nom


class Medicament(models.Model):
    FORMES = [
        ("comprime", "Comprimé"),
        ("gelule", "Gélule"),
        ("sirop", "Sirop"),
        ("injectable", "Injectable"),
        ("pommade", "Pommade"),
        ("autre", "Autre"),
    ]

    nom_commercial = models.CharField(max_length=150)
    denomination_generique = models.CharField(max_length=150, blank=True)
    categorie = models.ForeignKey(
        Categorie, on_delete=models.PROTECT, related_name="medicaments"
    )
    forme = models.CharField(max_length=20, choices=FORMES, default="comprime")
    dosage = models.CharField(max_length=50, blank=True, help_text="Ex : 500 mg")
    laboratoire = models.CharField(max_length=150, blank=True)
    code_barres = models.CharField(max_length=50, unique=True, null=True, blank=True)
    photo = models.ImageField(upload_to="medicaments/", null=True, blank=True)
    prix_achat = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    prix_vente = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    seuil_alerte = models.PositiveIntegerField(default=10)
    actif = models.BooleanField(default=True)  # False = archivé
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nom_commercial"]

    def __str__(self):
        return f"{self.nom_commercial} {self.dosage}".strip()