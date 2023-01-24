# Generated by Django 4.1.5 on 2023-01-24 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0037_remove_afterschoolregistration_bank_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankBicCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_code', models.CharField(help_text='4 characters', max_length=4, unique=True, verbose_name='Bank code')),
                ('bic_code', models.CharField(help_text='8-11 characters: Entity (4), Country (2), City (2), Office (3, Optional)', max_length=11, unique=True, verbose_name='BIC code')),
            ],
        ),
    ]