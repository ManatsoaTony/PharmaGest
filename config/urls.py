"""
URL configuration for config project (PharmaGest).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Les urls des apps seront ajoutées ici au fur et à mesure :
    # path("medicaments/", include("medicaments.urls")),
]

# Servir les photos uploadées en développement uniquement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)