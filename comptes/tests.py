from django.test import TestCase
from .models import Client
from django.urls import reverse
import subprocess
import uuid
from .models import CustomUser as User


class ClientModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

    def test_creer_client(self):
        client = Client.objects.create(nom="Client Test", solde=100.0)
        self.assertEqual(client.nom, "Client Test")
        self.assertEqual(client.solde, 100.0)


class ClientViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

    def test_liste_clients(self):
        response = self.client.get(reverse("liste_clients"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comptes/liste_clients.html")

    def test_ajouter_client(self):
        response = self.client.post(
            reverse("ajouter_client"), {"nom": "Nouveau Client", "solde": 200.0}
        )
        self.assertEqual(response.status_code, 302)  # Redirection après ajout
        self.assertEqual(Client.objects.count(), 1)


class BlackFormattingTest(TestCase):

    def test_black_formatting(self):
        result = subprocess.run(
            ["black", "--check", "--diff", "."], capture_output=True, text=True
        )
        if result.returncode != 0:
            self.fail(f"Black formatting issues:\n{result.stdout}\n{result.stderr}")


class ClientModelTest(TestCase):

    def test_creer_client(self):
        client = Client.objects.create(
            nom="Client Test",
            prenom="Test",
            email="test@example.com",
            adresse="123 Rue Test",
            telephone="1234567890",
            solde=100.0,
        )
        self.assertEqual(client.nom, "Client Test")
        self.assertEqual(client.prenom, "Test")
        self.assertEqual(client.email, "test@example.com")
        self.assertEqual(client.adresse, "123 Rue Test")
        self.assertEqual(client.telephone, "1234567890")
        self.assertEqual(client.solde, 100.0)
        self.assertIsInstance(client.identifiant_unique, uuid.UUID)
