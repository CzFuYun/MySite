# Generated by Django 2.0.2 on 2018-05-07 07:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0015_dividedpersonalaccount_data_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staff',
            name='begin_work',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='political_status',
        ),
    ]
