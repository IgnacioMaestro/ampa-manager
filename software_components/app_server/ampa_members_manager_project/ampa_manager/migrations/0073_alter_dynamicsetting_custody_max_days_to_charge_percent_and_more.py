# Generated by Django 4.2 on 2024-03-25 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0072_child_normalized_name_family_normalized_surnames_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dynamicsetting',
            name='custody_max_days_to_charge_percent',
            field=models.IntegerField(default=80, help_text='Maximum number of days in a month (as a percentage) to charge to each user', verbose_name='Max days to charge'),
        ),
        migrations.AlterField(
            model_name='dynamicsetting',
            name='custody_members_discount_percent',
            field=models.FloatField(default=27.0, help_text='Percentage discounted to members in the price of the custody', verbose_name='Members discount'),
        ),
    ]
