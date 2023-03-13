# Generated by Django 4.1.5 on 2023-03-12 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0050_alter_afterschoolremittance_payment_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='custodyedition',
            name='cost',
            field=models.DecimalField(decimal_places=2, help_text='Prices will be calculated based on this cost and assisted days. No members have a surcharge of +27% ', max_digits=6, null=True, verbose_name='Cost'),
        ),
    ]