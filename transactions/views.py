from django.shortcuts import render, redirect
from .models import Transaction
from .forms import TransactionForm
from datetime import date
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from datetime import datetime


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
    today = request.GET.get("date", datetime.today().strftime("%Y-%m-%d"))
    date_obj = datetime.strptime(today, "%Y-%m-%d").date()
    transactions = Transaction.objects.filter(date__date=date_obj)
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
        "selected_date": date_obj,
    }
    return render(request, "transactions/bilan_journalier.html", context)
