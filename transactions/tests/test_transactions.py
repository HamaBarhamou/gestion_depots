from django.test import TestCase
from comptes.models import Client as ClientModel
from tickets.models import Ticket
from transactions.models import Transaction
from django.urls import reverse
from comptes.models import CustomUser as User
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.utils import timezone as django_timezone
from django.core.exceptions import ValidationError
from comptes.models import Client, GlobalSettings
from django.contrib.messages import get_messages
from transactions.forms import TransactionForm


class TransactionTest(TestCase):
    def setUp(self):
        self.fournisseur = User.objects.create_user(
            username="fournisseur", password="12345", role="fournisseur", solde=0
        )
        self.client = Client.objects.create(
            nom="Client Test",
            fournisseur=self.fournisseur,
            solde=0,
        )
        self.client_user = User.objects.create_user(
            username="client", password="12345", role="client"
        )
        GlobalSettings.objects.create()

    def test_solde_only_for_fournisseur(self):
        self.assertIsNone(self.client_user.solde)
        self.assertIsNotNone(self.fournisseur.solde)

    """ def test_creer_transaction_depot(self):
        Transaction.objects.create(
            client=self.client,
            type_transaction="DEPOT",
            montant=15000,
        )

        ticket = Ticket.objects.filter(client=self.client).first()
        # print("tickets=", Ticket.objects.filter(client=self.client).values())
        self.assertIsNotNone(ticket)
        self.assertEqual(Ticket.objects.filter(client=self.client).count(), 1)
        self.assertEqual(ticket.cases_cochees, 3)
        self.assertEqual(ticket.montant_restant, 5000 * 28)
        self.assertEqual(ticket.montant_total, 15000)
        self.assertEqual(self.client.solde, 10000)
        self.assertEqual(self.fournisseur.solde, 5000)
        Transaction.objects.create(
            client=self.client,
            type_transaction="DEPOT",
            montant=5000,
        )
        ticket = Ticket.objects.filter(client=self.client).first()
        self.assertEqual(Ticket.objects.filter(client=self.client).count(), 1)
        self.assertEqual(ticket.cases_cochees, 4)
        self.assertEqual(ticket.montant_restant, 5000 * 27)
        self.assertEqual(ticket.montant_total, 20000)
        self.assertEqual(self.client.solde, 15000)
        self.assertEqual(self.fournisseur.solde, 5000)

    def test_ajouter_plusieurs_tickets(self):
        Transaction.objects.create(
            client=self.client,
            type_transaction="DEPOT",
            montant=460000,
        )

        tickets = Ticket.objects.filter(client=self.client)
        ticket_active = Ticket.objects.filter(active=True).first()
        self.assertEqual(ticket_active.cases_cochees, 30)
        self.assertEqual(tickets.count(), 3)
        self.assertEqual(self.client.solde, 445000)
        self.assertEqual(self.fournisseur.solde, 15000)

        Transaction.objects.create(
            client=self.client,
            type_transaction="DEPOT",
            montant=20000,
        )
        tickets = Ticket.objects.filter(client=self.client)
        ticket_active = Ticket.objects.filter(active=True).first()
        self.assertEqual(ticket_active.cases_cochees, 3)
        self.assertEqual(tickets.count(), 4)
        self.assertEqual(self.client.solde, 460000)
        self.assertEqual(self.fournisseur.solde, 15000 + 5000)

        Transaction.objects.create(
            client=self.client,
            type_transaction="DEPOT",
            montant=10000,
        )
        tickets = Ticket.objects.filter(client=self.client)
        ticket_active = Ticket.objects.filter(active=True).first()
        self.assertEqual(ticket_active.cases_cochees, 5)
        self.assertEqual(tickets.count(), 4)
        self.assertEqual(self.client.solde, 470000)
        self.assertEqual(self.fournisseur.solde, 20000) """

    def test_depot_non_multiple_unite_versement(self):
        transaction = Transaction(
            client=self.client, type_transaction="DEPOT", montant=15500
        )
        with self.assertRaises(ValidationError):
            transaction.save()

    def test_depot_montant_null(self):
        transaction = Transaction(
            client=self.client, type_transaction="DEPOT", montant=0
        )
        with self.assertRaises(ValidationError):
            transaction.save()
