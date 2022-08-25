# Generated by Django 4.0.6 on 2022-08-25 06:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_members_manager', '0062_alter_activityperiod_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('funding', models.IntegerField(choices=[(1, 'No funding'), (2, 'Cultural'), (3, 'Sport')], verbose_name='Funding')),
                ('academic_course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ampa_members_manager.academiccourse', verbose_name='Academic course')),
            ],
            options={
                'verbose_name': 'Activity',
                'verbose_name_plural': 'Activity',
            },
        ),
    ]
