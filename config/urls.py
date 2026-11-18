"""
URL configuration for config project (PharmaGest).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("fournisseurs/", include("fournisseurs.urls")),
    path("stock/", include("stock.urls")),
    path("ventes/", include("ventes.urls")),
    path("tableau-de-bord/", include("rapports.urls")),
    path("achats/", include("achats.urls")),
    path("", include("medicaments.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)