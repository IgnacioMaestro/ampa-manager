# Generated by Django 4.1.5 on 2023-02-11 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0047_remove_activityperiod_activity_delete_activity_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='custodyedition',
            name='unique_academic_course_with_period_and_primary',
        ),
        migrations.RemoveField(
            model_name='custodyedition',
            name='primary',
        ),
        migrations.AddField(
            model_name='custodyedition',
            name='cycle',
            field=models.CharField(choices=[('PRE', 'Pre-school'), ('PRI', 'Primary education')], default='PRI', max_length=3, verbose_name='Cycle'),
        ),
        migrations.AddConstraint(
            model_name='custodyedition',
            constraint=models.UniqueConstraint(fields=('academic_course', 'period', 'cycle'), name='unique_academic_course_with_period_and_cycle'),
        ),
    ]
