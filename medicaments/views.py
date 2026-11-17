from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import CategorieForm, MedicamentForm
from .models import Categorie, Medicament


class MedicamentListView(ListView):
    model = Medicament
    template_name = "medicaments/liste.html"
    context_object_name = "medicaments"
    paginate_by = 10

    def get_queryset(self):
        qs = Medicament.objects.select_related("categorie")
        q = self.request.GET.get("q", "").strip()
        cat = self.request.GET.get("categorie", "")
        if q:
            qs = qs.filter(Q(nom_commercial__icontains=q) | Q(code_barres__icontains=q))
        if cat:
            qs = qs.filter(categorie_id=cat)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Categorie.objects.all()
        ctx["q"] = self.request.GET.get("q", "")
        ctx["cat"] = self.request.GET.get("categorie", "")
        return ctx


class MedicamentDetailView(DetailView):
    model = Medicament
    template_name = "medicaments/detail.html"


class MedicamentCreateView(CreateView):
    model = Medicament
    form_class = MedicamentForm
    template_name = "medicaments/form.html"
    success_url = reverse_lazy("medicament_liste")

    def form_valid(self, form):
        messages.success(self.request, "Médicament ajouté.")
        return super().form_valid(form)


class MedicamentUpdateView(UpdateView):
    model = Medicament
    form_class = MedicamentForm
    template_name = "medicaments/form.html"
    success_url = reverse_lazy("medicament_liste")

    def form_valid(self, form):
        messages.success(self.request, "Médicament modifié.")
        return super().form_valid(form)


@require_POST
def medicament_archiver(request, pk):
    med = get_object_or_404(Medicament, pk=pk)
    med.actif = not med.actif
    med.save(update_fields=["actif"])
    messages.success(request, "Statut mis à jour (archivé/actif).")
    return redirect("medicament_liste")

class CategorieListView(ListView):
    model = Categorie
    template_name = "medicaments/categorie_liste.html"
    context_object_name = "categories"


class CategorieCreateView(CreateView):
    model = Categorie
    form_class = CategorieForm
    template_name = "medicaments/categorie_form.html"
    success_url = reverse_lazy("categorie_liste")

    def form_valid(self, form):
        messages.success(self.request, "Catégorie ajoutée.")
        return super().form_valid(form)


class CategorieUpdateView(UpdateView):
    model = Categorie
    form_class = CategorieForm
    template_name = "medicaments/categorie_form.html"
    success_url = reverse_lazy("categorie_liste")

    def form_valid(self, form):
        messages.success(self.request, "Catégorie modifiée.")
        return super().form_valid(form)