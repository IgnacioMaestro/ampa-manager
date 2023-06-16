# Generated by Django 4.2 on 2023-06-16 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0056_camps_receipt_and_remittance'),
    ]

    operations = [
        migrations.AddField(
            model_name='afterschoolremittance',
            name='sepa_id',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Sepa_id'),
        ),
        migrations.AddField(
            model_name='campsremittance',
            name='sepa_id',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Sepa_id'),
        ),
        migrations.AddField(
            model_name='custodyremittance',
            name='sepa_id',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Sepa_id'),
        ),
        migrations.AddField(
            model_name='membershipremittance',
            name='sepa_id',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Sepa_id'),
        ),
    ]
