# Generated by Django 2.0.6 on 2018-06-11 09:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("datamodel", "0003_auto_20180608_1605")]

    operations = [
        migrations.CreateModel(
            name="ZaakObject",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "object",
                    models.URLField(
                        help_text="URL naar de resource die het OBJECT beschrijft."
                    ),
                ),
                (
                    "relatieomschrijving",
                    models.CharField(
                        blank=True,
                        help_text="Omschrijving van de betrekking tussen de ZAAK en het OBJECT.",
                        max_length=80,
                    ),
                ),
                (
                    "zaak",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="datamodel.Zaak"
                    ),
                ),
            ],
        )
    ]
