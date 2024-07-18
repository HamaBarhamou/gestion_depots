from django.shortcuts import render, redirect, get_object_or_404
from .models import Client
from .forms import ClientForm
from transactions.models import Transaction
from django.contrib.auth.decorators import login_required
from comptes.decorators import role_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from tickets.models import Ticket
from django.utils.dateparse import parse_date
from django.db.models import Sum


@login_required
@role_required("fournisseur")
def tableau_de_bord(request):
    transactions = Transaction.objects.filter(
        client__fournisseur=request.user
    ).order_by("-date")[:10]
    context = {"transactions": transactions}
    return render(request, "comptes/tableau_de_bord.html", context)


@login_required
@role_required("fournisseur")
def liste_clients(request):
    query = request.GET.get("q")
    if query:
        clients_list = Client.objects.filter(
            (
                Q(nom__icontains=query)
                | Q(prenom__icontains=query)
                | Q(solde__icontains=query)
            )
            & Q(fournisseur=request.user)
        ).order_by("date_creation")
    else:
        clients_list = Client.objects.filter(fournisseur=request.user).order_by(
            "date_creation"
        )

    paginator = Paginator(clients_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if not page_obj:
        page_obj = paginator.get_page(1)

    return render(
        request, "comptes/liste_clients.html", {"page_obj": page_obj, "query": query}
    )


@login_required
@role_required("fournisseur")
def client_search(request):
    query = request.GET.get("q", "")
    clients = Client.objects.filter(
        Q(nom__icontains=query)
        | Q(prenom__icontains=query)
        | Q(email__icontains=query)
        | Q(telephone__icontains=query)
        | Q(solde__icontains=query)
        | Q(identifiant_unique__icontains=query),
        fournisseur=request.user,
    )[:10]
    context = {"clients": clients}
    html = render_to_string("comptes/client_search_results.html", context)
    return HttpResponse(html)


@login_required
@role_required("fournisseur")
def detail_client(request, identifiant_unique):
    client = get_object_or_404(
        Client, identifiant_unique=identifiant_unique, fournisseur=request.user
    )
    tickets = Ticket.objects.filter(client=client)
    ticket_actif = tickets.filter(active=True).first()

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        transactions = Transaction.objects.filter(
            client=client, date__range=[start_date, end_date]
        )
    else:
        transactions = Transaction.objects.filter(client=client)

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
        "client": client,
        "tickets": tickets,
        "ticket_actif": ticket_actif,
        "transactions": transactions,
        "total_depots": total_depots,
        "total_retraits": total_retraits,
        "range_cases": list(range(1, 32)),
    }
    return render(request, "comptes/detail_client.html", context)


@login_required
@role_required("fournisseur")
def ajouter_client(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.fournisseur = request.user
            client.save()
            form.save()
            return redirect("liste_clients")
    else:
        form = ClientForm()
    return render(request, "comptes/ajouter_client.html", {"form": form})
