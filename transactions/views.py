from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction
from comptes.models import Client
from .forms import TransactionForm
from datetime import timedelta
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from comptes.decorators import role_required
from datetime import datetime
from django.utils import timezone


@login_required
@role_required("fournisseur")
def enregistrer_transaction(request):
    client_info = None
    form = TransactionForm()

    if "client" in request.GET:
        client_id = request.GET.get("client")
        client_info = get_object_or_404(Client, pk=client_id)
        form = TransactionForm(initial={"client": client_info.id})

    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.date = timezone.now()
            transaction.save()
            return redirect("tableau_de_bord")
        else:
            print("form invalid")
            print(form.errors)

    return render(
        request,
        "transactions/enregistrer_transaction.html",
        {"form": form, "client_info": client_info},
    )


@login_required
@role_required("fournisseur")
def bilan_journalier(request):
    today = request.GET.get("date", datetime.today().strftime("%Y-%m-%d"))
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date and end_date:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        transactions = Transaction.objects.filter(
            date__date__range=(start_date_obj, end_date_obj)
        )
    else:
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
        "selected_date": today,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "transactions/bilan_journalier.html", context)
