# Generated by Django 4.1.5 on 2023-01-24 01:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0031_rename_document_holder_authorization_document'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='family',
            name='default_bank_account',
        ),
    ]
