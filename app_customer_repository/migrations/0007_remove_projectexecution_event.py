# Generated by Django 2.0.2 on 2018-07-18 02:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_customer_repository', '0006_targettask'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectexecution',
            name='event',
        ),
    ]