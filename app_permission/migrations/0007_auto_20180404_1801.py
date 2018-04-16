# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-04-04 10:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_permission', '0006_auto_20180404_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainmenuitem',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parent_item', to='app_permission.Permission'),
        ),
    ]
