# Generated by Django 4.1.5 on 2023-02-09 23:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0042_custodyremittance'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustodyReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(verbose_name='Total (€)')),
                ('state', models.IntegerField(choices=[(1, 'Created'), (2, 'Sent'), (3, 'Paid')], default=1, verbose_name='State')),
                ('custody_registration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ampa_manager.custodyregistration', verbose_name='Custody registrations')),
                ('remittance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ampa_manager.custodyremittance', verbose_name='Custody remittance')),
            ],
            options={
                'verbose_name': 'Custody receipt',
                'verbose_name_plural': 'Custody receipts',
                'db_table': 'custody_receipt',
            },
        ),
    ]
