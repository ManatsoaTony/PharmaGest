from django.urls import path
from . import views

urlpatterns = [
    path("", views.ClientListView.as_view(), name="client_liste"),
    path("ajouter/", views.ClientCreateView.as_view(), name="client_ajouter"),
    path("<int:pk>/", views.ClientDetailView.as_view(), name="client_detail"),
    path("<int:pk>/modifier/", views.ClientUpdateView.as_view(), name="client_modifier"),
]