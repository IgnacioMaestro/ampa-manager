# Generated by Django 4.1.5 on 2023-01-23 23:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0029_rename_state_holder_authorization_state'),
    ]

    operations = [
        migrations.RenameField(
            model_name='holder',
            old_name='sign_date',
            new_name='authorization_sign_date',
        ),
    ]
