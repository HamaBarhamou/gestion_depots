from django.shortcuts import render, redirect
from .models import Transaction
from .forms import TransactionForm
from datetime import date
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone


@login_required
def enregistrer_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.date = timezone.now()
            transaction.save()
            return redirect("tableau_de_bord")
    else:
        form = TransactionForm()
    return render(request, "transactions/enregistrer_transaction.html", {"form": form})


""" def enregistrer_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("tableau_de_bord")
    else:
        form = TransactionForm()
    return render(request, "transactions/enregistrer_transaction.html", {"form": form}) """


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


""" @login_required
def bilan_journalier(request):
    today = request.GET.get("date", date.today().strftime("%Y-%m-%d"))
    date_obj = datetime.strptime(today, "%Y-%m-%d").date()
    print("date_obj=", date_obj)

    start_of_day = timezone.make_aware(datetime.combine(date_obj, datetime.min.time()))
    end_of_day = timezone.make_aware(datetime.combine(date_obj, datetime.max.time()))

    transactions = Transaction.objects.filter(date__range=(start_of_day, end_of_day))
    print("transactions=", transactions)

    for t in transactions:
        print("{} {}".format(t, t.date.strftime("%Y-%m-%d")))

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
    return render(request, "transactions/bilan_journalier.html", context) """
