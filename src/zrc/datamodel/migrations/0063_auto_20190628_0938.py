# Generated by Django 2.2.2 on 2019-06-28 09:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0062_rol_registratiedatum'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelevanteZaakRelatie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=1000, verbose_name='URL naar zaak')),
                ('aard_relatie', models.CharField(choices=[('vervolg', 'De andere zaak gaf aanleiding tot het starten van de onderhanden zaak.'), ('onderwerp', 'De andere zaak is relevant voor cq. is onderwerp van de onderhanden zaak.'), ('bijdrage', 'Aan het bereiken van de uitkomst van de andere zaak levert de onderhanden zaak een bijdrage.')], max_length=20)),
                ('zaak', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relevante_andere_zaken', to='datamodel.Zaak')),
            ],
        ),
    ]
