from django.urls import path
from . import views

urlpatterns = [
    path("", views.liste, name="achat_liste"),
    path("nouvelle/", views.creer, name="achat_creer"),
    path("<int:pk>/", views.detail, name="achat_detail"),
    path("<int:pk>/ligne/", views.ajouter_ligne, name="achat_ligne_ajouter"),
    path("ligne/<int:pk>/supprimer/", views.supprimer_ligne, name="achat_ligne_supprimer"),
    path("<int:pk>/valider/", views.valider, name="achat_valider"),
    path("<int:pk>/annuler/", views.annuler, name="achat_annuler"),
    path("ligne/<int:pk>/recevoir/", views.recevoir, name="achat_recevoir"),
]