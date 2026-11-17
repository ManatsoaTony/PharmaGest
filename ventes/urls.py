from django.urls import path
from . import views

urlpatterns = [
    path("", views.caisse, name="caisse"),
    path("ajouter/", views.panier_ajouter, name="panier_ajouter"),
    path("retirer/<int:pk>/", views.panier_retirer, name="panier_retirer"),
    path("valider/", views.valider, name="vente_valider"),
    path("historique/", views.liste_ventes, name="vente_liste"),
    path("<int:pk>/", views.vente_detail, name="vente_detail"),
    path("<int:pk>/pdf/", views.recu_pdf, name="vente_pdf"),
]