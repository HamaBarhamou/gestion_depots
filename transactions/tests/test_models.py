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


class TransactionModelTest(TestCase):

    def setUp(self):
        self.fournisseur_user = User.objects.create_user(
            username="fournisseuruser", password="12345", role="fournisseur"
        )
        self.client = ClientModel.objects.create(
            fournisseur=self.fournisseur_user,
            nom="Client Test",
            email="test@example.com",
            telephone="1234567890",
            solde=0,
        )
        GlobalSettings.objects.create()

    def test_creer_depot(self):
        transaction = Transaction.objects.create(
            client=self.client, type_transaction="DEPOT", montant=20000
        )
        self.assertEqual(transaction.type_transaction, "DEPOT")
        self.assertEqual(transaction.montant, 20000)
        self.assertEqual(transaction.client, self.client)
        self.assertEqual(self.client.solde, 15000)
        self.assertEqual(self.fournisseur_user.solde, 5000)


class TransactionModelTest2(TestCase):

    def setUp(self):
        # Create a non-fournisseur user
        self.user = User.objects.create_user(
            username="testuser", password="12345", role="client"
        )
        # Create a fournisseur user
        self.fournisseur = User.objects.create_user(
            username="fournisseuruser", password="12345", role="fournisseur"
        )
        self.client_model = ClientModel.objects.create(
            nom="Client Test",
            email="test@example.com",
            adresse="123 Rue Test",
            telephone="1234567890",
            solde=100.0,
            fournisseur=self.fournisseur,
        )
        GlobalSettings.objects.create()

    def test_depot_transaction(self):
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="DEPOT",
            montant=10000,
            date=timezone.now(),
        )
        self.client_model.refresh_from_db()
        self.assertEqual(self.client_model.solde, 5100)

    def test_retrait_transaction(self):
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="RETRAIT",
            montant=50.0,
            date=timezone.now(),
        )
        self.client_model.refresh_from_db()
        self.assertEqual(self.client_model.solde, 50.0)

    def test_retrait_transaction_insufficient_funds(self):
        with self.assertRaises(ValidationError):
            Transaction.objects.create(
                client=self.client_model,
                type_transaction="RETRAIT",
                montant=150.0,
                date=timezone.now(),
            )

    def test_enregistrer_transaction_as_non_fournisseur(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("enregistrer_transaction"),
            {
                "client": self.client_model.id,
                "type_transaction": "DEPOT",
                "montant": 50.0,
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_enregistrer_transaction_as_fournisseur(self):
        self.client.login(username="fournisseuruser", password="12345")
        response = self.client.post(
            reverse("enregistrer_transaction"),
            {
                "client": self.client_model.id,
                "type_transaction": "DEPOT",
                "montant": 5000,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Transaction.objects.count(), 1)

    def test_retrait_with_insufficient_balance(self):
        transaction = Transaction(
            client=self.client_model, type_transaction="RETRAIT", montant=150.0
        )
        with self.assertRaises(ValidationError):
            transaction.clean()
