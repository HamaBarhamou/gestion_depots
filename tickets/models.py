# tickets/models.py
from django.db import models
from comptes.models import Client, CustomUser, GlobalSettings


class Ticket(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    fournisseur = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, limit_choices_to={"role": "fournisseur"}
    )
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    montant_restant = models.DecimalField(max_digits=10, decimal_places=2)
    cases_cochees = models.PositiveIntegerField(default=0)
    nombre_cases = models.PositiveIntegerField(default=31)
    active = models.BooleanField(default=True)
    date_ouverture = models.DateTimeField(auto_now_add=True)

    def ajouter_versement(self, montant):

        while montant > 0:
            cases_a_couvrir = montant // self.client.unite_versement
            cases_libres = self.nombre_cases - self.cases_cochees

            if cases_a_couvrir <= cases_libres:
                self.cases_cochees += cases_a_couvrir
                montant_couvert = cases_a_couvrir * self.client.unite_versement
                self.montant_total += montant_couvert
                self.montant_restant -= montant_couvert
                montant -= montant_couvert
            else:
                self.cases_cochees = self.nombre_cases
                montant_couvert = cases_libres * self.client.unite_versement
                self.montant_total += montant_couvert
                self.montant_restant -= montant_couvert
                montant -= montant_couvert
                self.active = False
                self.save()
                self.creer_nouveau_ticket(montant)
                return

            if self.cases_cochees >= self.nombre_cases:
                self.active = False

            self.save()

    def creer_nouveau_ticket(self, montant):
        nouveau_ticket = Ticket.objects.create(
            client=self.client,
            fournisseur=self.fournisseur,
            montant_restant=self.client.unite_versement * self.nombre_cases,
        )

        nouveau_ticket.ajouter_versement(montant)

    """ def creer_nouveau_ticket(self, montant):
        nouveau_ticket = Ticket.objects.create(
            client=self.client,
            fournisseur=self.fournisseur,
            montant_restant=self.client.unite_versement * self.nombre_cases,
        )

        # Calculer la commission ici
        global_settings = GlobalSettings.objects.first()
        commission_rate = global_settings.commission_rate
        commission = self.client.unite_versement * commission_rate

        montant_a_transferer = self.client.unite_versement
        self.fournisseur.solde += montant_a_transferer
        self.client.solde -= montant_a_transferer
        self.fournisseur.platform_balance = montant_a_transferer * commission_rate
        self.fournisseur.save()
        self.client.save()

        self.fournisseur.solde -= commission
        self.fournisseur.platform_balance += commission
        self.fournisseur.save()

        nouveau_ticket.ajouter_versement(montant) """
