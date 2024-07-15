from django.test import TestCase
from comptes.models import Client as ClientModel
from .models import Transaction
from django.urls import reverse
from comptes.models import CustomUser as User
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.utils import timezone as django_timezone
from django.core.exceptions import ValidationError
from comptes.models import Client
from django.contrib.messages import get_messages


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

    def test_enregistrer_transaction_as_fournisseur(self):
        self.client.login(username="fournisseuruser", password="12345")
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

    def test_bilan_journalier_as_fournisseur(self):
        self.client.login(username="fournisseuruser", password="12345")

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
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "<p><strong>Total des Dépôts :</strong> 50 FCFA</p>"
        )
        self.assertContains(
            response, "<p><strong>Total des Retraits :</strong> 20 FCFA</p>"
        )

    """ def test_bilan_periode_as_fournisseur(self):
        self.client.login(username="fournisseuruser", password="12345")

        start_date = datetime(2024, 7, 1)
        end_date = datetime(2024, 7, 10)

        # Transactions for the period
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="DEPOT",
            montant=50.0,
            date=start_date,
        )
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="RETRAIT",
            montant=20.0,
            date=end_date,
        )
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="DEPOT",
            montant=100.0,
            date=start_date + timedelta(days=5),
        )

        # Check transactions for the period
        response = self.client.get(
            reverse("bilan_journalier"),
            {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "<p><strong>Total des Dépôts :</strong> 150 FCFA</p>"
        )
        self.assertContains(
            response, "<p><strong>Total des Retraits :</strong> 20 FCFA</p>"
        ) """

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


class TransactionModelTest(TestCase):

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

    def test_depot_transaction(self):
        Transaction.objects.create(
            client=self.client_model,
            type_transaction="DEPOT",
            montant=50.0,
            date=timezone.now(),
        )
        self.client_model.refresh_from_db()
        self.assertEqual(self.client_model.solde, 150.0)

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
                "montant": 50.0,
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

    def test_fournisseur1_cannot_record_transaction_for_client2(self):
        self.client.login(username="fournisseur1", password="12345")
        response = self.client.post(
            reverse("enregistrer_transaction"),
            {
                "client": self.client2.id,
                "type_transaction": "DEPOT",
                "montant": 50.0,
            },
        )
        self.assertEqual(
            response.status_code,
            403,  # On attend un code 403 (Forbidden) et non plus 404
            "Fournisseur1 ne devrait pas pouvoir enregistrer une transaction pour Client2",
        )

    def test_fournisseur1_can_record_transaction_for_own_client(self):
        self.client.login(username="fournisseur1", password="12345")
        response = self.client.post(
            reverse("enregistrer_transaction"),
            {
                "client": self.client1.id,
                "type_transaction": "DEPOT",
                "montant": 50.0,
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
                "montant": 50.0,
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
                "montant": 50.0,
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirection après succès
        self.assertEqual(Transaction.objects.filter(client=self.client2).count(), 1)


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
