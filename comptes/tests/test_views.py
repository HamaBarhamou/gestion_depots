from django.test import TestCase
from comptes.models import Client, GlobalSettings
from django.urls import reverse
import subprocess
import uuid
from comptes.models import CustomUser as User
from django.utils import timezone
from transactions.models import Transaction


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
            nom="Client A", prenom="Alpha", solde=100.0, fournisseur=self.fournisseur
        )
        self.client_model2 = Client.objects.create(
            nom="Client B", prenom="Bravo", solde=200.0, fournisseur=self.fournisseur
        )
        self.client_model3 = Client.objects.create(
            nom="Client C",
            prenom="Charlie",
            solde=300.0,
            fournisseur=self.fournisseur,
        )
        self.client_model4 = Client.objects.create(
            nom="Client D", prenom="Delta", solde=400.0, fournisseur=self.fournisseur
        )
        self.client_model5 = Client.objects.create(
            nom="Client E", prenom="Echo", solde=500.0, fournisseur=self.fournisseur
        )
        self.client_model6 = Client.objects.create(
            nom="Client F", prenom="Foxtrot", solde=600.0, fournisseur=self.fournisseur
        )
        self.client_model7 = Client.objects.create(
            nom="Client G", prenom="Golf", solde=700.0, fournisseur=self.fournisseur
        )
        self.client_model8 = Client.objects.create(
            nom="Client H", prenom="Hotel", solde=800.0, fournisseur=self.fournisseur
        )
        self.client_model9 = Client.objects.create(
            nom="Client I", prenom="India", solde=900.0, fournisseur=self.fournisseur
        )
        self.client_model10 = Client.objects.create(
            nom="Client J", prenom="Juliett", solde=1000.0, fournisseur=self.fournisseur
        )
        self.client_model11 = Client.objects.create(
            nom="Client K", prenom="Kilo", solde=1100.0, fournisseur=self.fournisseur
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


class ClientDetailViewTest(TestCase):
    def setUp(self):
        self.fournisseur = User.objects.create_user(
            username="fournisseur", password="12345", role="fournisseur", solde=0
        )
        self.client_model = Client.objects.create(
            nom="Client Test",
            prenom="Prenom Test",
            fournisseur=self.fournisseur,
            solde=0,
            unite_versement=1000,
        )
        GlobalSettings.objects.create()

    def test_detail_client_view(self):
        self.client.login(username="fournisseur", password="12345")
        self.client.post(
            reverse("enregistrer_transaction"),
            {
                "client": self.client_model.id,
                "type_transaction": "DEPOT",
                "montant": 95000,
            },
        )
        response = self.client.get(
            reverse("detail_client", args=[self.client_model.identifiant_unique])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.client_model.nom)
        self.assertContains(response, self.client_model.id)
        # print(response.content.decode("utf-8"))
        self.assertContains(response, "<p><strong>Cases Cochées :</strong> 2/31</p>")
        self.assertContains(
            response, "<p><strong>Nombre total de Tickets :</strong> 4</p>"
        )

    """ def test_bilan_client_view(self):
        self.client.login(username="fournisseur", password="12345")
        start_date = timezone.now() - timezone.timedelta(days=30)
        end_date = timezone.now()
        response = self.client.get(
            reverse("detail_client", args=[self.client_model.identifiant_unique]),
            {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total Dépôts")
        self.assertContains(response, "Total Retraits") """


class SuperuserViewTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="superuser", password="superuserpassword", role="superuser"
        )
        self.fournisseur = User.objects.create_user(
            username="fournisseur",
            password="fournisseurpassword",
            role="fournisseur",
            solde=0,
        )
        self.client_user = Client.objects.create(
            nom="Client Test",
            fournisseur=self.fournisseur,
            solde=0,
            unite_versement=5000,
        )
        self.client.login(username="superuser", password="superuserpassword")
        GlobalSettings.objects.create()

    def test_vue_ensemble_accessible_by_superuser(self):
        response = self.client.get(reverse("vue_ensemble"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vue d'ensemble de la plateforme")

    def test_vue_ensemble_not_accessible_by_non_superuser(self):
        self.client.logout()
        self.client.login(username="fournisseur", password="fournisseurpassword")
        response = self.client.get(reverse("vue_ensemble"))
        self.assertEqual(response.status_code, 403)

    def test_vue_ensemble_content(self):
        Transaction.objects.create(
            client=self.client_user, type_transaction="DEPOT", montant=15000
        )
        response = self.client.get(reverse("vue_ensemble"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nombre total de clients")
        self.assertContains(response, self.fournisseur.username)
        self.assertContains(response, "15000 FCFA")
        self.assertContains(response, "1")
