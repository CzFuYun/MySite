# Generated by Django 2.0.2 on 2018-05-07 07:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0016_auto_20180507_1526'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staff',
            name='birthday',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='cellphone',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='mail_address',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='telephone',
        ),
    ]
