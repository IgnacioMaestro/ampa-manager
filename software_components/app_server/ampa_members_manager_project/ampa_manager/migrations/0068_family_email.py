# Generated by Django 4.2 on 2024-01-30 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0067_alter_family_membership_holder'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email'),
        ),
    ]
