# Generated by Django 4.2 on 2024-01-30 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0068_family_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='afterschoolremittance',
            name='concept',
            field=models.CharField(blank=True, help_text='Maximum 30 characters', max_length=30, null=True, verbose_name='Concept'),
        ),
        migrations.AlterField(
            model_name='afterschoolremittance',
            name='name',
            field=models.CharField(blank=True, help_text='Maximum 30 characters', max_length=30, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='campsremittance',
            name='concept',
            field=models.CharField(blank=True, help_text='Maximum 30 characters', max_length=30, null=True, verbose_name='Concept'),
        ),
        migrations.AlterField(
            model_name='campsremittance',
            name='name',
            field=models.CharField(blank=True, help_text='Maximum 30 characters', max_length=30, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='custodyremittance',
            name='concept',
            field=models.CharField(blank=True, help_text='Maximum 30 characters', max_length=30, null=True, verbose_name='Concept'),
        ),
        migrations.AlterField(
            model_name='custodyremittance',
            name='name',
            field=models.CharField(blank=True, help_text='Maximum 30 characters', max_length=30, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='membershipremittance',
            name='concept',
            field=models.CharField(blank=True, help_text='Maximum 30 characters', max_length=30, null=True, verbose_name='Concept'),
        ),
        migrations.AlterField(
            model_name='membershipremittance',
            name='name',
            field=models.CharField(blank=True, help_text='Maximum 30 characters', max_length=30, null=True, verbose_name='Name'),
        ),
    ]