from django import forms
from .models import Transaction
from comptes.models import Client
from django.core.exceptions import ValidationError


class TransactionForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(), widget=forms.HiddenInput()
    )

    class Meta:
        model = Transaction
        fields = ["client", "type_transaction", "montant"]

    def clean(self):
        cleaned_data = super().clean()
        montant = cleaned_data.get("montant")
        client = cleaned_data.get("client")
        type_transaction = cleaned_data.get("type_transaction")

        if montant == 0:
            raise ValidationError(
                "Le montant du {} doit être un different de 0".format(type_transaction)
            )
        if client and montant and type_transaction == "DEPOT":
            if montant % client.unite_versement != 0:
                raise ValidationError(
                    f"Le montant du dépôt doit être un multiple de l'unité de versement ({client.unite_versement} FCFA)."
                )

        return cleaned_data
