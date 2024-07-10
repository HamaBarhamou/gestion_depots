# signals.py
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from .models import Transaction


@receiver(pre_save, sender=Transaction)
def update_client_solde(sender, instance, **kwargs):
    if instance.pk is None:  # Only for new transactions
        if instance.type_transaction == "DEPOT":
            instance.client.solde += instance.montant
        elif instance.type_transaction == "RETRAIT":
            if instance.client.solde >= instance.montant:
                instance.client.solde -= instance.montant
            else:
                raise ValidationError("Solde insuffisant pour effectuer ce retrait.")
        instance.client.save()
