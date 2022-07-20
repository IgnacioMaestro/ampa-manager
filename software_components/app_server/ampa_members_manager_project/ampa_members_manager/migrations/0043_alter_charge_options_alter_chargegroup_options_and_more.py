# Generated by Django 4.0.6 on 2022-07-15 10:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_members_manager', '0042_add_secondary_email_to_family'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='charge',
            options={'verbose_name': 'Charge', 'verbose_name_plural': 'Charges'},
        ),
        migrations.AlterModelOptions(
            name='chargegroup',
            options={'verbose_name': 'Charge group', 'verbose_name_plural': 'Charge groups'},
        ),
        migrations.AlterField(
            model_name='charge',
            name='activity_registrations',
            field=models.ManyToManyField(to='ampa_members_manager.activityregistration', verbose_name='Activity registrations'),
        ),
        migrations.AlterField(
            model_name='charge',
            name='amount',
            field=models.FloatField(blank=True, null=True, verbose_name='Amount'),
        ),
        migrations.AlterField(
            model_name='charge',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ampa_members_manager.chargegroup', verbose_name='Group'),
        ),
        migrations.AlterField(
            model_name='charge',
            name='state',
            field=models.IntegerField(choices=[(1, 'Created'), (2, 'Send'), (3, 'Paid')], default=1, verbose_name='State'),
        ),
        migrations.AlterField(
            model_name='chargegroup',
            name='single_activities',
            field=models.ManyToManyField(to='ampa_members_manager.singleactivity', verbose_name='Single activities'),
        ),
        migrations.AlterField(
            model_name='singleactivity',
            name='payment_type',
            field=models.IntegerField(choices=[(1, 'Single'), (2, 'Per Day'), (3, 'Per Week'), (4, 'Per Month')], verbose_name='Payment type'),
        ),
    ]