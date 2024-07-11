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
        # Create a non-fournisseur user
        self.user = User.objects.create_user(
            username="testuser", password="12345", role="client"
        )
        # Create a fournisseur user
        self.fournisseur = User.objects.create_user(
            username="fournisseuruser", password="12345", role="fournisseur"
        )
        # Create a fournisseur user
        self.usernonrole = User.objects.create_user(username="norole", password="12345")
        # Créer plusieurs clients pour les tests de pagination et de recherche
        self.client_model1 = Client.objects.create(
            nom="Client A", prenom="Alpha", solde=100.0
        )
        self.client_model2 = Client.objects.create(
            nom="Client B", prenom="Bravo", solde=200.0
        )
        self.client_model3 = Client.objects.create(
            nom="Client C", prenom="Charlie", solde=300.0
        )
        self.client_model4 = Client.objects.create(
            nom="Client D", prenom="Delta", solde=400.0
        )
        self.client_model5 = Client.objects.create(
            nom="Client E", prenom="Echo", solde=500.0
        )
        self.client_model6 = Client.objects.create(
            nom="Client F", prenom="Foxtrot", solde=600.0
        )
        self.client_model7 = Client.objects.create(
            nom="Client G", prenom="Golf", solde=700.0
        )
        self.client_model8 = Client.objects.create(
            nom="Client H", prenom="Hotel", solde=800.0
        )
        self.client_model9 = Client.objects.create(
            nom="Client I", prenom="India", solde=900.0
        )
        self.client_model10 = Client.objects.create(
            nom="Client J", prenom="Juliett", solde=1000.0
        )
        self.client_model11 = Client.objects.create(
            nom="Client K", prenom="Kilo", solde=1100.0
        )

    def test_liste_clients_as_non_fournisseur(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("liste_clients"))
        self.assertEqual(response.status_code, 403)

    def test_liste_clients_as_no_role(self):
        self.client.login(username="norole", password="12345")
        response = self.client.get(reverse("liste_clients"))
        self.assertEqual(response.status_code, 403)

    def test_liste_clients_as_fournisseur(self):
        self.client.login(username="fournisseuruser", password="12345")
        response = self.client.get(reverse("liste_clients"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comptes/liste_clients.html")

    def test_ajouter_client_as_non_fournisseur(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("ajouter_client"), {"nom": "Nouveau Client", "solde": 200.0}
        )
        self.assertEqual(response.status_code, 403)

    def test_ajouter_client_as_fournisseur(self):
        self.client.login(username="fournisseuruser", password="12345")
        response = self.client.post(
            reverse("ajouter_client"), {"nom": "Nouveau Client", "solde": 200.0}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Client.objects.count(), 12)

    def test_liste_clients_pagination(self):
        self.client.login(username="fournisseuruser", password="12345")
        response = self.client.get(reverse("liste_clients") + "?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comptes/liste_clients.html")
        self.assertEqual(
            len(response.context["page_obj"]), 10
        )  # Première page, 10 clients
        response = self.client.get(reverse("liste_clients") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context["page_obj"]), 1
        )  # Deuxième page, 1 client

    def test_liste_clients_search_nom(self):
        self.client.login(username="fournisseuruser", password="12345")
        response = self.client.get(reverse("liste_clients") + "?q=Client A")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Client A")
        self.assertNotContains(response, "Client B")

    def test_liste_clients_search_prenom(self):
        self.client.login(username="fournisseuruser", password="12345")
        response = self.client.get(reverse("liste_clients") + "?q=Bravo")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Client B")
        self.assertNotContains(response, "Client A")

    def test_liste_clients_search_solde(self):
        self.client.login(username="fournisseuruser", password="12345")
        response = self.client.get(reverse("liste_clients") + "?q=600")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Client F")
        self.assertNotContains(response, "Client A")

    def test_liste_clients_search_no_results(self):
        self.client.login(username="fournisseuruser", password="12345")
        response = self.client.get(reverse("liste_clients") + "?q=NonExistentClient")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucun client trouvé.")


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
