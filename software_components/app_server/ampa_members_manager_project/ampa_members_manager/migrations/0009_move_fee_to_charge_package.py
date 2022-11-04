# Generated by Django 4.0.6 on 2022-11-04 22:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_members_manager', '0008_family_decline_membership_alter_family_is_defaulter'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='academiccourse',
            name='fee',
        ),
        migrations.CreateModel(
            name='Fee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(blank=True, null=True, verbose_name='Fee')),
                ('academic_course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ampa_members_manager.academiccourse')),
            ],
        ),
    ]
