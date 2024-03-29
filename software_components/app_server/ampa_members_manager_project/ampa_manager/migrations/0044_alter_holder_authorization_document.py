# Generated by Django 4.1.5 on 2023-02-10 10:55

import ampa_manager.family.models.holder.holder
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0043_custodyreceipt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='holder',
            name='authorization_document',
            field=models.FileField(blank=True, null=True, upload_to=ampa_manager.family.models.holder.holder.generate_holder_authorization_file_name, verbose_name='Document'),
        ),
    ]
