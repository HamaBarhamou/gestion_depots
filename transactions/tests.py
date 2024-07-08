from django.test import TestCase
from comptes.models import Client as ClientModel
from .models import Transaction
from django.urls import reverse

# from django.contrib.auth.models import User
from comptes.models import CustomUser as User
from datetime import datetime


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
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="DEPOT",
            montant=50.0,
            date=datetime.now(),
        )
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="RETRAIT",
            montant=20.0,
            date=datetime.now(),
        )
        response = self.client.get(reverse("bilan_journalier"))
        # print(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total des dépôts : 50")
        self.assertContains(response, "Total des retraits : 20")
