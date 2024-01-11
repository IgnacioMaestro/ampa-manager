# Generated by Django 4.2 on 2023-12-20 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0059_create_custody_importation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custodyimportationrow',
            name='level',
            field=models.IntegerField(choices=[(1, 'HH2'), (2, 'HH3'), (3, 'HH4'), (4, 'HH5'), (5, 'LH1'), (6, 'LH2'), (7, 'LH3'), (8, 'LH4'), (9, 'LH5'), (10, 'LH6')], verbose_name='Level'),
        ),
    ]
