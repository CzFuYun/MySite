# Generated by Django 2.1.1 on 2018-09-19 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_customer_repository', '0032_auto_20180919_1123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pretrialmeeting',
            name='folder',
        ),
    ]