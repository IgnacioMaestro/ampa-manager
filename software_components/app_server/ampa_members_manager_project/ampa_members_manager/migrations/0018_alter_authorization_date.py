# Generated by Django 4.0.6 on 2022-12-23 14:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_members_manager', '0017_alter_afterschoolreceipt_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorization',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
