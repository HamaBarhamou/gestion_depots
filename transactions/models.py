from django.db import models
from django.core.exceptions import ValidationError
from comptes.models import Client


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
        if self.type_transaction == "RETRAIT" and self.client.solde < self.montant:
            raise ValidationError("Solde insuffisant pour effectuer ce retrait.")
