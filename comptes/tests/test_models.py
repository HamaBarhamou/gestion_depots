from django.test import TestCase
from comptes.models import Client, GlobalSettings, CustomUser as User
import uuid


class ClientModelTest(TestCase):
    def setUp(self):
        self.fournisseur_user = User.objects.create_user(
            username="fournisseuruser", password="12345", role="fournisseur"
        )

    def test_creer_client(self):
        client = Client.objects.create(
            fournisseur=self.fournisseur_user,
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
