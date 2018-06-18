# Generated by Django 2.0.6 on 2018-06-19 07:54

from django.db import migrations, models
import drc.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EnkelvoudigInformatieObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('informatieobjectidentificatie', models.CharField(help_text='Een binnen een gegeven context ondubbelzinnige referentie naar het INFORMATIEOBJECT.', max_length=40, validators=[drc.validators.AlphanumericExcludingDiacritic()])),
                ('bronorganisatie', models.CharField(blank=True, help_text='Het RSIN van de Niet-natuurlijk persoon zijnde de organisatie die het informatieobject heeft gecreëerd of heeft ontvangen en als eerste in een samenwerkingsketen heeft vastgelegd.', max_length=9, null=True, validators=[drc.validators.validate_non_negative_string])),
                ('creatiedatum', models.DateField(help_text='Een datum of een gebeurtenis in de levenscyclus van het INFORMATIEOBJECT.')),
                ('titel', models.CharField(help_text='De naam waaronder het INFORMATIEOBJECT formeel bekend is.', max_length=200)),
                ('auteur', models.CharField(help_text='De persoon of organisatie die in de eerste plaats verantwoordelijk is voor het creëren van de inhoud van het INFORMATIEOBJECT.', max_length=200)),
                ('formaat', models.CharField(blank=True, help_text='De code voor de wijze waarop de inhoud van het ENKELVOUDIG INFORMATIEOBJECT is vastgelegd in een computerbestand.', max_length=255)),
                ('taal', models.CharField(help_text='Een taal van de intellectuele inhoud van het ENKELVOUDIG INFORMATIEOBJECT', max_length=20)),
                ('inhoud', models.FileField(upload_to='')),
            ],
            options={
                'verbose_name': 'informatieobject',
                'verbose_name_plural': 'informatieobject',
                'abstract': False,
            },
        ),
    ]
