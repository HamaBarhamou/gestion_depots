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
    unite_versement = models.DecimalField(max_digits=10, decimal_places=2, default=5000)
    date_creation = models.DateTimeField(auto_now_add=True)
    fournisseur = models.ForeignKey(
        "CustomUser",
        on_delete=models.CASCADE,
        related_name="clients",
        limit_choices_to={"role": "fournisseur"},
    )

    def __str__(self):
        return "{} {}".format(self.nom.upper(), self.prenom)


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("fournisseur", "Fournisseur"),
        ("client", "Client"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    solde = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, blank=True, null=True
    )
    platform_balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )  # Solde de la plateforme
    active = models.BooleanField(default=True)  # Statut actif/inactif du fournisseur

    def save(self, *args, **kwargs):
        # Ensure solde is only set for fournisseur
        if self.role != "fournisseur":
            self.solde = None
        super().save(*args, **kwargs)


class GlobalSettings(models.Model):
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.05)
