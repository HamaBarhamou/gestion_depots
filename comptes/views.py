from django.shortcuts import render, redirect, get_object_or_404
from .models import Client
from .forms import ClientForm
from transactions.models import Transaction
from django.contrib.auth.decorators import login_required
from comptes.decorators import role_required


@login_required
@role_required("fournisseur")
def tableau_de_bord(request):
    transactions = Transaction.objects.all().order_by("-date")[:10]
    context = {"transactions": transactions}
    return render(request, "comptes/tableau_de_bord.html", context)


@login_required
@role_required("fournisseur")
def liste_clients(request):
    clients = Client.objects.all()
    return render(request, "comptes/liste_clients.html", {"clients": clients})


@login_required
@role_required("fournisseur")
def detail_client(request, identifiant_unique):
    client = get_object_or_404(Client, identifiant_unique=identifiant_unique)
    return render(request, "comptes/detail_client.html", {"client": client})


@login_required
@role_required("fournisseur")
def ajouter_client(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("liste_clients")
    else:
        form = ClientForm()
    return render(request, "comptes/ajouter_client.html", {"form": form})
