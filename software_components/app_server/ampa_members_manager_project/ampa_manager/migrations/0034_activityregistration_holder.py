# Generated by Django 4.1.5 on 2023-01-24 01:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0033_alter_bankaccount_options_remove_bankaccount_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityregistration',
            name='holder',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='ampa_manager.holder', verbose_name='Holder'),
            preserve_default=False,
        ),
    ]
