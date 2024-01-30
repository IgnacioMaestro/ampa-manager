# Generated by Django 4.2 on 2024-01-30 15:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0065_alter_dynamicsetting_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='after_school_holder',
            field=models.ForeignKey(blank=True, help_text='Save the family to see its bank accounts', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='after_school_holder', to='ampa_manager.holder', verbose_name='After-school holder'),
        ),
        migrations.AddField(
            model_name='family',
            name='camps_holder',
            field=models.ForeignKey(blank=True, help_text='Save the family to see its bank accounts', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='camps_holder', to='ampa_manager.holder', verbose_name='Camps holder'),
        ),
    ]