from django.shortcuts import render, redirect
from .models import Client
from .forms import ClientForm
from transactions.models import Transaction


def tableau_de_bord(request):
    transactions = Transaction.objects.all().order_by("-date")[:10]
    context = {"transactions": transactions}
    return render(request, "comptes/tableau_de_bord.html", context)


def liste_clients(request):
    clients = Client.objects.all()
    return render(request, "comptes/liste_clients.html", {"clients": clients})


def ajouter_client(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("liste_clients")
    else:
        form = ClientForm()
    return render(request, "comptes/ajouter_client.html", {"form": form})
