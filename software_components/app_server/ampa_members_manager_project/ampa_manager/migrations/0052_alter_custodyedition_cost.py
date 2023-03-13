# Generated by Django 4.1.5 on 2023-03-13 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0051_custodyedition_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custodyedition',
            name='cost',
            field=models.DecimalField(decimal_places=2, help_text='Los precios se pueden calcular automáticamente con la acción "Calcular precios" a partir de este coste y los días asistidos. Los no socios tienen un recargo del 27% ', max_digits=6, null=True, verbose_name='Cost'),
        ),
    ]
