# Generated by Django 4.0.6 on 2022-12-23 15:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0019_add_db_table_to_models'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='afterschool',
            table='after_school',
        ),
        migrations.AlterModelTable(
            name='afterschooledition',
            table='after_school_edition',
        ),
        migrations.AlterModelTable(
            name='afterschoolregistration',
            table='after_school_registration',
        ),
    ]
