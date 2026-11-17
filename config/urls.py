"""
URL configuration for config project (PharmaGest).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("fournisseurs/", include("fournisseurs.urls")),
    path("", include("medicaments.urls")),
]

# Servir les photos uploadées en développement uniquement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)