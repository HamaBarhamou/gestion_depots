from django.test import TestCase
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


class TransactionViewsTest(TestCase):

    def setUp(self):
        # Create users
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.fournisseur_user = User.objects.create_user(
            username="fournisseuruser", password="12345", role="fournisseur"
        )
        # Create a client model instance
        self.client_model = ClientModel.objects.create(
            fournisseur=self.fournisseur_user,
            nom="Client Test",
            email="test@example.com",
            telephone="1234567890",
            solde=100.0,
        )
        GlobalSettings.objects.create()

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
        self.assertEqual(response.status_code, 302)  # Redirection après ajout
        self.assertEqual(Transaction.objects.count(), 1)

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
        self.assertEqual(response.status_code, 403)  # Access should be denied

    def test_client_search(self):
        self.client.login(username="fournisseuruser", password="12345")
        response = self.client.get(reverse("client_search"), {"q": "Client"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Client Test")

    def test_enregistrer_transaction_get(self):
        self.client.login(username="fournisseuruser", password="12345")
        response = self.client.get(
            reverse("enregistrer_transaction"), {"client": self.client_model.id}
        )
        # print(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Client Test")
        self.assertContains(response, "Test")
        self.assertContains(response, "test@example.com")
        self.assertContains(response, "1234567890")
        self.assertContains(response, "</strong> 100.00 FCFA</p>")
