from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, UpdateView

from .forms import FournisseurForm
from .models import Fournisseur


class FournisseurListView(ListView):
    model = Fournisseur
    template_name = "fournisseurs/liste.html"
    context_object_name = "fournisseurs"
    paginate_by = 10

    def get_queryset(self):
        qs = Fournisseur.objects.all()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(nom__icontains=q) | Q(telephone__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class FournisseurCreateView(CreateView):
    model = Fournisseur
    form_class = FournisseurForm
    template_name = "fournisseurs/form.html"
    success_url = reverse_lazy("fournisseur_liste")

    def form_valid(self, form):
        messages.success(self.request, "Fournisseur ajouté.")
        return super().form_valid(form)


class FournisseurUpdateView(UpdateView):
    model = Fournisseur
    form_class = FournisseurForm
    template_name = "fournisseurs/form.html"
    success_url = reverse_lazy("fournisseur_liste")

    def form_valid(self, form):
        messages.success(self.request, "Fournisseur modifié.")
        return super().form_valid(form)


@require_POST
def fournisseur_basculer(request, pk):
    """Désactive/réactive un fournisseur sans effacer son historique."""
    f = get_object_or_404(Fournisseur, pk=pk)
    f.actif = not f.actif
    f.save(update_fields=["actif"])
    messages.success(request, "Statut du fournisseur mis à jour.")
    return redirect("fournisseur_liste")