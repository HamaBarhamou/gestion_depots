from django.db import models
from django.core.exceptions import ValidationError
from comptes.models import Client
from tickets.models import Ticket


class Transaction(models.Model):
    TYPE_CHOICES = [
        ("DEPOT", "Dépôt"),
        ("RETRAIT", "Retrait"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    type_transaction = models.CharField(max_length=10, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_transaction} de {self.montant} pour {self.client.nom}"

    def clean(self):
        if self.type_transaction == "DEPOT" and self.montant == 0:
            raise ValidationError("Le montant du dépôt doit être un different de 0")
        if self.type_transaction == "RETRAIT" and self.client.solde < self.montant:
            raise ValidationError("Solde insuffisant pour effectuer ce retrait.")

    def save(self, *args, **kwargs):
        if self.type_transaction == "DEPOT":
            if self.montant == 0:
                raise ValidationError("Le montant du dépôt doit être un different de 0")
            if self.montant % self.client.unite_versement != 0:
                raise ValidationError(
                    "Le montant du dépôt doit être un multiple de l'unité de versement du client."
                )
            self.gestion_tickets_depot()
        super().save(*args, **kwargs)

    def gestion_tickets_depot(self):
        client = self.client
        fournisseur = client.fournisseur
        montant = self.montant
        unite_versement = client.unite_versement

        ticket_actif = Ticket.objects.filter(client=client, active=True).first()
        if not ticket_actif:
            ticket_actif = Ticket.objects.create(
                client=client,
                fournisseur=fournisseur,
                montant_restant=unite_versement * 31,
            )

        ticket_actif.ajouter_versement(montant)

        cases_cochees = montant // unite_versement
        nombre_tickets_utilises = (
            cases_cochees // 31 if cases_cochees % 31 == 0 else cases_cochees // 31 + 1
        )
        montant_a_transferer = nombre_tickets_utilises * unite_versement

        client.solde -= montant_a_transferer
        fournisseur.solde += montant_a_transferer
        client.save()
        fournisseur.save()
