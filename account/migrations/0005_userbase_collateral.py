# Generated by Django 4.2.6 on 2024-03-08 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_userbase_options_alter_userbase_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbase',
            name='collateral',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=50),
        ),
    ]