from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ampa_manager', '0081_remove_custodyimportationactionchild_child_to_update_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dynamicsetting',
            name='family_email_domain',
            field=models.CharField(
                blank=True, default='', max_length=200, verbose_name='Family email domain',
                help_text='If set, imported family emails must use this domain. Example: @abendanoikastola.com'),
        ),
    ]
