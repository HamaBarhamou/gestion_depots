from django.test import TestCase
from .models import Client
from django.urls import reverse
from django.contrib.auth.models import User


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
