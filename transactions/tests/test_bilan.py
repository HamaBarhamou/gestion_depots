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


class BilanTest(TestCase):

    def setUp(self):
        # Create users with different roles
        self.fournisseur_user = User.objects.create_user(
            username="fournisseuruser", password="12345", role="fournisseur"
        )
        self.client_user = User.objects.create_user(
            username="clientuser", password="12345", role="client"
        )
        self.no_role_user = User.objects.create_user(
            username="noroleuser", password="12345"
        )
        self.client_model = Client.objects.create(
            fournisseur=self.fournisseur_user, nom="Client Test", solde=100.0
        )
        GlobalSettings.objects.create()

    def test_bilan_journalier_as_fournisseur(self):
        self.client.login(username="fournisseuruser", password="12345")

        today = datetime(2024, 7, 10)

        # Transactions for today
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="DEPOT",
            montant=50000,
            date=today,
        )
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="RETRAIT",
            montant=20000,
            date=today,
        )

        # Check today's transactions
        response = self.client.get(reverse("bilan_journalier"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "<p><strong>Total des Dépôts :</strong> 50000 FCFA</p>"
        )
        self.assertContains(
            response, "<p><strong>Total des Retraits :</strong> 20000 FCFA</p>"
        )

    def test_bilan_periode_as_fournisseur(self):
        pass

    def test_bilan_periode_without_dates(self):
        self.client.login(username="fournisseuruser", password="12345")
        response = self.client.get(reverse("bilan_journalier"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Veuillez sélectionner une date de début pour le bilan par période.",
        )
        self.assertContains(
            response, "Veuillez sélectionner une date de fin pour le bilan par période."
        )

    def test_bilan_journalier_as_client(self):
        self.client.login(username="clientuser", password="12345")

        # Attempt to access bilan_journalier as client
        response = self.client.get(reverse("bilan_journalier"))
        self.assertEqual(response.status_code, 403)

    def test_bilan_journalier_as_no_role_user(self):
        self.client.login(username="noroleuser", password="12345")

        # Attempt to access bilan_journalier as no role user
        response = self.client.get(reverse("bilan_journalier"))
        self.assertEqual(response.status_code, 403)
