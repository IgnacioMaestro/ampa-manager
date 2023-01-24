# Generated by Django 4.1.5 on 2023-01-23 23:39

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0025_afterschoolregistration_holder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='holder',
            name='year',
            field=models.IntegerField(default=2023, validators=[django.core.validators.MinValueValidator(1000), django.core.validators.MaxValueValidator(3000)], verbose_name='Year'),
        ),
    ]