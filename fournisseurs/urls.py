from django.urls import path
from . import views

urlpatterns = [
    path("", views.FournisseurListView.as_view(), name="fournisseur_liste"),
    path("ajouter/", views.FournisseurCreateView.as_view(), name="fournisseur_ajouter"),
    path("<int:pk>/modifier/", views.FournisseurUpdateView.as_view(), name="fournisseur_modifier"),
    path("<int:pk>/basculer/", views.fournisseur_basculer, name="fournisseur_basculer"),
    path("fournisseurs/", include("fournisseurs.urls")),
]