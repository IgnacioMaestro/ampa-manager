# Generated by Django 4.1.5 on 2023-02-10 11:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0046_delete_activityregistration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activityperiod',
            name='activity',
        ),
        migrations.DeleteModel(
            name='Activity',
        ),
        migrations.DeleteModel(
            name='ActivityPeriod',
        ),
    ]
