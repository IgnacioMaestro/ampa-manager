# Generated by Django 4.0.6 on 2022-07-26 06:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_members_manager', '0054_modify_constraing_to_single_activity'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SingleActivity',
            new_name='ActivityPayablePart',
        ),
    ]
