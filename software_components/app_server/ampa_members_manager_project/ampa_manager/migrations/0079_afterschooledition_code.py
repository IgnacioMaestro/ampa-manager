# Generated by Django 4.2 on 2024-11-08 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0078_dynamicsetting_remittances_custody_bic_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='afterschooledition',
            name='code',
            field=models.CharField(blank=True, max_length=300, null=True, unique=True, verbose_name='Code'),
        ),
    ]