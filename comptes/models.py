from django.db import models
from django.contrib.auth.models import AbstractUser


class Client(models.Model):
    nom = models.CharField(max_length=100)
    solde = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nom


class CustomUser(AbstractUser):
    ROLE_CHOICES = (("fournisseur", "Fournisseur"),)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="fournisseur")
