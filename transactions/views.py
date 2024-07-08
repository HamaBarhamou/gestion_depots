from django.shortcuts import render, redirect
from .models import Transaction
from .forms import TransactionForm
from datetime import date
from django.db.models import Sum
from django.contrib.auth.decorators import login_required


@login_required
def enregistrer_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("tableau_de_bord")
    else:
        form = TransactionForm()
    return render(request, "transactions/enregistrer_transaction.html", {"form": form})


@login_required
def bilan_journalier(request):
    today = date.today()
    transactions = Transaction.objects.filter(date__date=today)
    total_depots = (
        transactions.filter(type_transaction="DEPOT").aggregate(Sum("montant"))[
            "montant__sum"
        ]
        or 0
    )
    total_retraits = (
        transactions.filter(type_transaction="RETRAIT").aggregate(Sum("montant"))[
            "montant__sum"
        ]
        or 0
    )
    context = {
        "transactions": transactions,
        "total_depots": total_depots,
        "total_retraits": total_retraits,
    }
    return render(request, "transactions/bilan_journalier.html", context)
