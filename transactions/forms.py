from django import forms
from .models import Transaction
from comptes.models import Client


""" class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["client", "type_transaction", "montant"] """


class TransactionForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(), widget=forms.HiddenInput()
    )

    class Meta:
        model = Transaction
        fields = ["client", "type_transaction", "montant"]
