# Generated by Django 2.2.2 on 2019-06-05 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0059_auto_20190531_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zaak',
            name='opschorting_indicatie',
            field=models.BooleanField(blank=True, default=False, help_text='Aanduiding of de behandeling van de ZAAK tijdelijk is opgeschort.', verbose_name='indicatie opschorting'),
        ),
    ]
