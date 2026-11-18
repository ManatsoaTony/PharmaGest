from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ClientForm
from .models import Client


class ClientListView(ListView):
    model = Client
    template_name = "clients/liste.html"
    context_object_name = "clients"
    paginate_by = 10

    def get_queryset(self):
        qs = Client.objects.all()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(nom__icontains=q) | Q(telephone__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/form.html"
    success_url = reverse_lazy("client_liste")

    def form_valid(self, form):
        messages.success(self.request, "Client ajouté.")
        return super().form_valid(form)


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/form.html"
    success_url = reverse_lazy("client_liste")

    def form_valid(self, form):
        messages.success(self.request, "Client modifié.")
        return super().form_valid(form)


class ClientDetailView(DetailView):
    model = Client
    template_name = "clients/detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ventes"] = self.object.ventes.all()[:50]
        return ctx