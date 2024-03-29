# Generated by Django 4.0.6 on 2022-11-02 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0007_alter_parent_additional_phone_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='decline_membership',
            field=models.BooleanField(default=False, help_text='It prevents the family from becoming a member. For example, if they no longer have children at school but you do not want to delete the record.', verbose_name='Decline membership'),
        ),
        migrations.AlterField(
            model_name='family',
            name='is_defaulter',
            field=models.BooleanField(default=False, help_text='Informative field only', verbose_name='Defaulter'),
        ),
    ]
