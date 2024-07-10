from django.test import TestCase
from comptes.models import Client as ClientModel
from .models import Transaction
from django.urls import reverse
from comptes.models import CustomUser as User
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.core.exceptions import ValidationError
from comptes.models import Client


class TransactionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")
        self.client = ClientModel.objects.create(nom="Client Test", solde=100.0)

    def test_creer_depot(self):
        transaction = Transaction.objects.create(
            client=self.client, type_transaction="DEPOT", montant=50.0
        )
        self.assertEqual(transaction.type_transaction, "DEPOT")
        self.assertEqual(transaction.montant, 50.0)
        self.assertEqual(transaction.client, self.client)


class TransactionViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")
        self.client_model = ClientModel.objects.create(nom="Client Test", solde=100.0)

    def test_enregistrer_transaction(self):
        response = self.client.post(
            reverse("enregistrer_transaction"),
            {
                "client": self.client_model.id,
                "type_transaction": "DEPOT",
                "montant": 50.0,
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirection après ajout
        self.assertEqual(Transaction.objects.count(), 1)


class BilanTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client_model = ClientModel.objects.create(nom="Client Test", solde=100.0)
        self.client.login(username="testuser", password="12345")

    def test_bilan_journalier(self):
        today = datetime(2024, 7, 10)

        # Transactions for today
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="DEPOT",
            montant=50.0,
            date=today,
        )
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="RETRAIT",
            montant=20.0,
            date=today,
        )

        # Check today's transactions
        response = self.client.get(reverse("bilan_journalier"))
        # print(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "<p><strong>Total des Dépôts :</strong> 50 FCFA</p>"
        )
        self.assertContains(
            response, "<p><strong>Total des Retraits :</strong> 20 FCFA</p>"
        )

    """ def test_bilan_journalier(self):
        # Use a fixed date for today
        fixed_today = timezone.make_aware(datetime(2024, 7, 9, 0, 0))
        yesterday = fixed_today - timedelta(days=1)
        print("\n fixed_today=", fixed_today)
        print("\n yesterday=", yesterday)

        # Transactions for today
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="DEPOT",
            montant=50.0,
            date=fixed_today,
        )
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="RETRAIT",
            montant=20.0,
            date=fixed_today,
        )

        # Transactions for yesterday
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="DEPOT",
            montant=30.0,
            date=yesterday,
        )
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="RETRAIT",
            montant=10.0,
            date=yesterday,
        )

        # Check today's transactions
        response = self.client.get(
            reverse("bilan_journalier"),
            {"date": fixed_today.date().strftime("%Y-%m-%d")},
        )
        # print("Today's response:", response.content.decode())  # For debugging
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "<p><strong>Total des Dépôts :</strong> 50 FCFA</p>"
        )
        self.assertContains(
            response, "<p><strong>Total des Retraits :</strong> 20 FCFA</p>"
        )

        # Check yesterday's transactions
        response = self.client.get(
            reverse("bilan_journalier"), {"date": yesterday.date().strftime("%Y-%m-%d")}
        )
        # print("Yesterday's response:", response.content.decode())  # For debugging
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "<p><strong>Total des Dépôts :</strong> 30 FCFA</p>"
        )
        self.assertContains(
            response, "<p><strong>Total des Retraits :</strong> 10 FCFA</p>"
        ) """


class TransactionModelTest(TestCase):

    def setUp(self):
        self.client = Client.objects.create(nom="Client Test", solde=100.0)

    def test_depot_transaction(self):
        Transaction.objects.create(
            client=self.client,
            type_transaction="DEPOT",
            montant=50.0,
            date=timezone.now(),
        )
        self.client.refresh_from_db()
        self.assertEqual(self.client.solde, 150.0)

    def test_retrait_transaction(self):
        Transaction.objects.create(
            client=self.client,
            type_transaction="RETRAIT",
            montant=50.0,
            date=timezone.now(),
        )
        self.client.refresh_from_db()
        self.assertEqual(self.client.solde, 50.0)

    def test_retrait_transaction_insufficient_funds(self):
        with self.assertRaises(ValidationError):
            Transaction.objects.create(
                client=self.client,
                type_transaction="RETRAIT",
                montant=150.0,
                date=timezone.now(),
            )
