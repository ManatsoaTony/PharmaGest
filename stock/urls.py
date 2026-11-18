from django.urls import path
from . import views

urlpatterns = [
    path("", views.apercu_stock, name="stock_apercu"),
    path("lots/", views.liste_lots, name="stock_lots"),
    path("reception/", views.reception, name="stock_reception"),
    path("mouvements/", views.mouvements, name="stock_mouvements"),
    path("inventaire/", views.inventaire, name="stock_inventaire"),
]