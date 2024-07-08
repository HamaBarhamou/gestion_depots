from django.test import TestCase
from comptes.models import Client as ClientModel
from .models import Transaction
from django.urls import reverse


class TransactionModelTest(TestCase):

    def setUp(self):
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
        self.client_model = ClientModel.objects.create(nom="Client Test", solde=100.0)

    def test_enregistrer_transaction(self):
        response = self.client.post(
            reverse("enregistrer_transaction"),
            {"client": self.client_model.id, "type_transaction": "DEPOT", "montant": 50.0},
        )
        self.assertEqual(response.status_code, 302)  # Redirection après ajout
        self.assertEqual(Transaction.objects.count(), 1)