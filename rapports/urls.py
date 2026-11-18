from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("stock.pdf", views.rapport_stock, name="rapport_stock"),
    path("peremption.pdf", views.rapport_peremption, name="rapport_peremption"),
    path("ventes.pdf", views.rapport_ventes, name="rapport_ventes"),
]