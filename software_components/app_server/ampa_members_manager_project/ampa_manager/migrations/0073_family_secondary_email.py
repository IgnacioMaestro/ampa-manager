# Generated by Django 4.2 on 2024-03-25 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0072_child_normalized_name_family_normalized_surnames_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='secondary_email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Secondary email'),
        ),
    ]
