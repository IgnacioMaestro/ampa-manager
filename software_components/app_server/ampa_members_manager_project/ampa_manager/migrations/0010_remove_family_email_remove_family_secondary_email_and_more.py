# Generated by Django 4.0.6 on 2022-11-06 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0009_move_fee_to_charge_package'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='family',
            name='email',
        ),
        migrations.RemoveField(
            model_name='family',
            name='secondary_email',
        ),
        migrations.AlterField(
            model_name='parent',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email'),
        ),
    ]
