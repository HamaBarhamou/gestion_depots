from django.test import TestCase
from comptes.models import Client, GlobalSettings, CustomUser as User
from django.urls import reverse
from transactions.models import Transaction


class CommissionTest(TestCase):
    def setUp(self):
        GlobalSettings.objects.create(commission_rate=0.10)
        self.superuser = User.objects.create_superuser(
            username="superuser", password="superuserpassword", role="superuser"
        )
        self.fournisseur = User.objects.create_user(
            username="fournisseur",
            password="fournisseurpassword",
            role="fournisseur",
            solde=0,
            active=True,
        )
        self.client_model = Client.objects.create(
            nom="Client Test",
            fournisseur=self.fournisseur,
            solde=0,
        )

    def test_commission_calculation(self):
        self.assertEqual(self.client_model.solde, 0)
        Transaction.objects.create(
            client=self.client_model, type_transaction="DEPOT", montant=15000
        )
        self.client_model.refresh_from_db()
        self.fournisseur.refresh_from_db()

        self.assertEqual(self.client_model.solde, 10000)
        self.assertEqual(self.fournisseur.solde, 5000)
        self.assertEqual(self.fournisseur.platform_balance, 500)

    def test_superuser_access(self):
        self.client.login(username="superuser", password="superuserpassword")
        response = self.client.get(reverse("vue_ensemble"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Platform balance")
        self.assertContains(response, "Détails des Fournisseurs")

    def test_fournisseur_inactive_access(self):
        self.fournisseur.active = False
        self.fournisseur.save()
        self.client.login(username="fournisseur", password="fournisseurpassword")
        response = self.client.get(reverse("tableau_de_bord"))
        self.assertEqual(response.status_code, 302)  # Redirection après paiement
        self.assertEqual(response.url, reverse("logout"))
