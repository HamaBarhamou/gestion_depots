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


class TransactionFormTest(TestCase):
    def setUp(self):
        self.fournisseur_user = User.objects.create_user(
            username="fournisseur", password="12345", role="fournisseur"
        )
        self.client_model = Client.objects.create(
            nom="Client Test",
            prenom="Test",
            email="test@example.com",
            adresse="123 Rue Test",
            telephone="1234567890",
            solde=50.0,
            fournisseur=self.fournisseur_user,
        )
        self.test_client = self.client  # Utilisez self.test_client pour les requêtes

    def test_transaction_form_displays_errors(self):
        self.test_client.login(username="fournisseur", password="12345")
        response = self.test_client.post(
            reverse("enregistrer_transaction"),
            {
                "client": self.client_model.id,
                "type_transaction": "RETRAIT",
                "montant": 100.0,
            },
        )
        # Vérifiez que le formulaire contient des erreurs
        self.assertContains(response, "Solde insuffisant pour effectuer ce retrait.")
        # Vérifiez que les erreurs sont affichées dans le template
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Formulaire invalide" in message.message for message in messages)
        )

        # Vérifiez que le formulaire est toujours affiché avec les erreurs
        self.assertContains(response, "Solde insuffisant pour effectuer ce retrait.")

    def test_transaction_form_invalid_unite_versement(self):
        form_data = {
            "client": self.client_model.id,
            "type_transaction": "DEPOT",
            "montant": 4500,  # Montant qui n'est pas un multiple de 5000
        }
        form = TransactionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            f"Le montant du dépôt doit être un multiple de l'unité de versement ({self.client_model.unite_versement}.00 FCFA).",
            form.errors["__all__"],
        )

    def test_transaction_form_invalid_depot_null(self):
        form_data = {
            "client": self.client_model.id,
            "type_transaction": "DEPOT",
            "montant": 0,
        }
        form = TransactionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            f"Le montant du dépôt doit être un different de 0",
            form.errors["__all__"],
        )

    def test_transaction_form_invalid_retrait_null(self):
        form_data = {
            "client": self.client_model.id,
            "type_transaction": "RETRAIT",
            "montant": 0,
        }
        form = TransactionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            f"Le montant du RETRAIT doit être un different de 0",
            form.errors["__all__"],
        )

    def test_transaction_form_valid_unite_versement(self):
        form_data = {
            "client": self.client_model.id,
            "type_transaction": "DEPOT",
            "montant": 5000,  # Montant qui est un multiple de 5000
        }
        form = TransactionForm(data=form_data)
        self.assertTrue(form.is_valid())
