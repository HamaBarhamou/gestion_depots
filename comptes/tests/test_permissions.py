from django.test import TestCase
from comptes.models import Client, GlobalSettings, CustomUser as User
from django.urls import reverse


class LoginTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_login_success(self):
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "testpassword"}
        )
        self.assertEqual(response.status_code, 302)

    def test_login_failure(self):
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nom d'utilisateur ou mot de passe incorrect.")


class FournisseurClientRestrictionTest(TestCase):
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

    def test_fournisseur1_cannot_see_client2(self):
        self.client.login(username="fournisseur1", password="12345")
        response = self.client.get(
            reverse("detail_client", args=[self.client2.identifiant_unique])
        )
        self.assertEqual(
            response.status_code, 404
        )  # Fournisseur1 ne peut pas accéder aux détails de Client2

    def test_fournisseur2_cannot_see_client1(self):
        self.client.login(username="fournisseur2", password="12345")
        response = self.client.get(
            reverse("detail_client", args=[self.client1.identifiant_unique])
        )
        self.assertEqual(
            response.status_code, 404
        )  # Fournisseur2 ne peut pas accéder aux détails de Client1

    def test_fournisseur1_can_see_own_client(self):
        self.client.login(username="fournisseur1", password="12345")
        response = self.client.get(
            reverse("detail_client", args=[self.client1.identifiant_unique])
        )
        self.assertEqual(
            response.status_code, 200
        )  # Fournisseur1 peut accéder aux détails de son propre client

    def test_fournisseur2_can_see_own_client(self):
        self.client.login(username="fournisseur2", password="12345")
        response = self.client.get(
            reverse("detail_client", args=[self.client2.identifiant_unique])
        )
        self.assertEqual(
            response.status_code, 200
        )  # Fournisseur2 peut accéder aux détails de son propre client
