import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class Client(models.Model):
    identifiant_unique = models.UUIDField(
        default=uuid.uuid4, editable=False, null=True, unique=True
    )
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    solde = models.DecimalField(max_digits=10, decimal_places=2)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.nom.upper(), self.prenom)


class CustomUser(AbstractUser):
    ROLE_CHOICES = (("fournisseur", "Fournisseur"),)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="fournisseur")
