from django.shortcuts import render, redirect
from .models import Transaction
from .forms import TransactionForm


def enregistrer_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("tableau_de_bord")
    else:
        form = TransactionForm()
    return render(request, "transactions/enregistrer_transaction.html", {"form": form})
