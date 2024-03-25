# Generated by Django 4.2 on 2024-02-29 16:21
from math import floor

from django.db import migrations, models
import django.db.models.deletion

from ampa_manager.dynamic_settings.dynamic_settings import DynamicSetting


def calculate_days_with_service(apps, schema_editor):
    CustodyEdition = apps.get_model('ampa_manager', 'CustodyEdition')
    max_days_percent = (DynamicSetting.load().custody_max_days_to_charge_percent / 100.0)
    for edition in CustodyEdition.objects.all():
        edition.days_with_service = floor(edition.max_days_for_charge / max_days_percent)
        edition.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0069_alter_afterschoolremittance_concept_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='custodyedition',
            name='days_with_service',
            field=models.PositiveIntegerField(default=30, help_text='Days in which there was custody this edition', verbose_name='Days with service'),
        ),
        migrations.AlterField(
            model_name='custodyregistration',
            name='assisted_days',
            field=models.PositiveIntegerField(verbose_name='Assisted days'),
        ),
        migrations.AlterField(
            model_name='family',
            name='membership_holder',
            field=models.ForeignKey(blank=True, help_text='Guarda la familia para ver sus cuentas bancarias. Se usará esta cuenta por defecto si no se indica otra', null=True, on_delete=django.db.models.deletion.SET_NULL, to='ampa_manager.holder', verbose_name='Membership holder'),
        ),
        migrations.RunPython(calculate_days_with_service),
    ]