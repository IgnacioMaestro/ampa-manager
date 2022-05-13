# Generated by Django 4.0.3 on 2022-05-13 22:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_members_manager', '0026_remove_assignment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FamiliarActivityRegistration',
        ),
        migrations.DeleteModel(
            name='IndividualActivityRegistration',
        ),
        migrations.RemoveConstraint(
            model_name='activityregistration',
            name='only one registered',
        ),
        migrations.RemoveField(
            model_name='activityregistration',
            name='registered_child',
        ),
        migrations.RemoveField(
            model_name='activityregistration',
            name='registered_family',
        ),
        migrations.AddField(
            model_name='activityregistration',
            name='child',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ampa_members_manager.child'),
            preserve_default=False,
        ),
    ]
