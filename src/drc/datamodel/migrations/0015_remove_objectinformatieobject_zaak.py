# Generated by Django 2.0.6 on 2018-09-19 10:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0014_auto_20180919_1008'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='objectinformatieobject',
            name='zaak',
        ),
    ]