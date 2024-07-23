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


class RolePermissionTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="normaluser", password="12345", role="client"
        )
        self.fournisseur = User.objects.create_user(
            username="fournisseuruser", password="12345", role="fournisseur"
        )
        self.client = self.client

    def test_access_denied_for_non_fournisseur(self):
        self.client.login(username="normaluser", password="12345")
        response = self.client.get(reverse("tableau_de_bord"))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse("liste_clients"))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse("ajouter_client"))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse("enregistrer_transaction"))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse("bilan_journalier"))
        self.assertEqual(response.status_code, 403)

    def test_access_allowed_for_fournisseur(self):
        self.client.login(username="fournisseuruser", password="12345")
        response = self.client.get(reverse("tableau_de_bord"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("liste_clients"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("ajouter_client"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("enregistrer_transaction"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("bilan_journalier"))
        self.assertEqual(response.status_code, 200)


class TransactionRestrictionTest(TestCase):
    def setUp(self):
        self.fournisseur1 = User.objects.create_user(
            username="fournisseur1", password="12345", role="fournisseur"
        )
        self.fournisseur2 = User.objects.create_user(
            username="fournisseur2", password="12345", role="fournisseur"
        )
        self.client1 = Client.objects.create(
            fournisseur=self.fournisseur1,
            nom="Client1",
            prenom="Test1",
            email="client1@example.com",
            solde=100.0,
        )
        self.client2 = Client.objects.create(
            fournisseur=self.fournisseur2,
            nom="Client2",
            prenom="Test2",
            email="client2@example.com",
            solde=200.0,
        )
        GlobalSettings.objects.create()

    def test_fournisseur1_cannot_record_transaction_for_client2(self):
        self.client.login(username="fournisseur1", password="12345")
        response = self.client.post(
            reverse("enregistrer_transaction"),
            {
                "client": self.client2.id,
                "type_transaction": "DEPOT",
                "montant": 5000,
            },
        )
        self.assertEqual(
            response.status_code,
            403,
            "Fournisseur1 ne devrait pas pouvoir enregistrer une transaction pour Client2",
        )

    def test_fournisseur1_can_record_transaction_for_own_client(self):
        self.client.login(username="fournisseur1", password="12345")
        response = self.client.post(
            reverse("enregistrer_transaction"),
            {
                "client": self.client1.id,
                "type_transaction": "DEPOT",
                "montant": 5000,
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirection après succès
        self.assertEqual(Transaction.objects.filter(client=self.client1).count(), 1)

    def test_fournisseur2_cannot_record_transaction_for_client1(self):
        self.client.login(username="fournisseur2", password="12345")
        response = self.client.post(
            reverse("enregistrer_transaction"),
            {
                "client": self.client1.id,
                "type_transaction": "DEPOT",
                "montant": 5000,
            },
        )
        self.assertEqual(
            response.status_code,
            403,  # On attend un code 403 (Forbidden) et non plus 404
            "Fournisseur2 ne devrait pas pouvoir enregistrer une transaction pour Client1",
        )

    def test_fournisseur2_can_record_transaction_for_own_client(self):
        self.client.login(username="fournisseur2", password="12345")
        response = self.client.post(
            reverse("enregistrer_transaction"),
            {
                "client": self.client2.id,
                "type_transaction": "DEPOT",
                "montant": 5000,
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirection après succès
        self.assertEqual(Transaction.objects.filter(client=self.client2).count(), 1)
