# Generated by Django 4.0.6 on 2022-11-23 23:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_members_manager', '0013_add_after_school'),
    ]

    operations = [
        migrations.CreateModel(
            name='AfterSchoolEdition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('levels', models.CharField(max_length=300, verbose_name='Levels')),
                ('price_for_member', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Price for members')),
                ('price_for_no_member', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Price for no members')),
                ('period', models.CharField(max_length=300, verbose_name='Period')),
                ('timetable', models.CharField(max_length=300, verbose_name='Timetable')),
                ('academic_course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ampa_members_manager.academiccourse', verbose_name='Academic course')),
                ('after_school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ampa_members_manager.afterschool', verbose_name='AfterSchool')),
            ],
        ),
        migrations.AddConstraint(
            model_name='afterschooledition',
            constraint=models.UniqueConstraint(fields=('after_school', 'academic_course', 'period', 'timetable'), name='unique_important_fields'),
        ),
    ]
