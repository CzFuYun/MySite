# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-04-10 07:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_permission', '0011_auto_20180409_1925'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='permission',
            name='display_icon',
        ),
        migrations.AddField(
            model_name='mainmenuitem',
            name='order',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]
