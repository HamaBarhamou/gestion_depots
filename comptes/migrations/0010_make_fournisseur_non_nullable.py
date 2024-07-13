# Generated by Django 5.0.6 on 2024-07-13 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comptes", "0009_assign_clients_to_first_fournisseur"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="fournisseur",
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name="clients",
                to="comptes.CustomUser",
                limit_choices_to={"role": "fournisseur"},
            ),
        ),
    ]
