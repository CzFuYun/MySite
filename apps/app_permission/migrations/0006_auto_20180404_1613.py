# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-04-04 08:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_permission', '0005_auto_20180404_1500'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MainMenu',
            new_name='MainMenuItem',
        ),
        migrations.AlterField(
            model_name='permission',
            name='url_name',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
