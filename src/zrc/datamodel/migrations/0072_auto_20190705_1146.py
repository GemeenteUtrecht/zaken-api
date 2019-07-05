# Generated by Django 2.2.2 on 2019-07-05 11:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0071_migrate_to_flattened_urls'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='natuurlijkpersoon',
            name='verblijfsadres',
        ),
        migrations.RemoveField(
            model_name='terreingebouwdobject',
            name='aoa_huisletter',
        ),
        migrations.RemoveField(
            model_name='terreingebouwdobject',
            name='aoa_huisnummer',
        ),
        migrations.RemoveField(
            model_name='terreingebouwdobject',
            name='aoa_huisnummertoevoeging',
        ),
        migrations.RemoveField(
            model_name='terreingebouwdobject',
            name='aoa_postcode',
        ),
        migrations.RemoveField(
            model_name='terreingebouwdobject',
            name='gor_openbare_ruimte_naam',
        ),
        migrations.RemoveField(
            model_name='terreingebouwdobject',
            name='num_identificatie',
        ),
        migrations.RemoveField(
            model_name='terreingebouwdobject',
            name='oao_identificatie',
        ),
        migrations.RemoveField(
            model_name='terreingebouwdobject',
            name='ogo_locatie_aanduiding',
        ),
        migrations.RemoveField(
            model_name='terreingebouwdobject',
            name='wpl_woonplaats_naam',
        ),
        migrations.RemoveField(
            model_name='vestiging',
            name='verblijfsadres',
        ),
        migrations.RemoveField(
            model_name='wozobject',
            name='aoa_huisletter',
        ),
        migrations.RemoveField(
            model_name='wozobject',
            name='aoa_huisnummer',
        ),
        migrations.RemoveField(
            model_name='wozobject',
            name='aoa_huisnummertoevoeging',
        ),
        migrations.RemoveField(
            model_name='wozobject',
            name='aoa_postcode',
        ),
        migrations.RemoveField(
            model_name='wozobject',
            name='gor_openbare_ruimte_naam',
        ),
        migrations.RemoveField(
            model_name='wozobject',
            name='locatie_omschrijving',
        ),
        migrations.RemoveField(
            model_name='wozobject',
            name='oao_identificatie',
        ),
        migrations.RemoveField(
            model_name='wozobject',
            name='wpl_woonplaats_naam',
        ),
        migrations.AddField(
            model_name='adres',
            name='locatie_aanduiding',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='adres',
            name='locatie_omschrijving',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AddField(
            model_name='adres',
            name='natuurlijkpersoon',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='verblijfsadres', to='datamodel.NatuurlijkPersoon'),
        ),
        migrations.AddField(
            model_name='adres',
            name='num_identificatie',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='adres',
            name='terreingebouwdobject',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='adres_aanduiding_grp', to='datamodel.TerreinGebouwdObject'),
        ),
        migrations.AddField(
            model_name='adres',
            name='vestiging',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='verblijfsadres', to='datamodel.Vestiging'),
        ),
        migrations.AddField(
            model_name='adres',
            name='wozobject',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='aanduiding_woz_object', to='datamodel.WozObject'),
        ),
        migrations.AlterField(
            model_name='adres',
            name='zaakobject',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='datamodel.ZaakObject'),
        ),
    ]
