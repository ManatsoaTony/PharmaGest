from django.urls import path
from . import views

urlpatterns = [
    path("", views.MedicamentListView.as_view(), name="medicament_liste"),
    path("medicaments/ajouter/", views.MedicamentCreateView.as_view(), name="medicament_ajouter"),
    path("medicaments/<int:pk>/", views.MedicamentDetailView.as_view(), name="medicament_detail"),
    path("medicaments/<int:pk>/modifier/", views.MedicamentUpdateView.as_view(), name="medicament_modifier"),
    path("medicaments/<int:pk>/archiver/", views.medicament_archiver, name="medicament_archiver"),
    path("categories/", views.CategorieListView.as_view(), name="categorie_liste"),
    path("categories/ajouter/", views.CategorieCreateView.as_view(), name="categorie_ajouter"),
    path("categories/<int:pk>/modifier/", views.CategorieUpdateView.as_view(), name="categorie_modifier"),
]