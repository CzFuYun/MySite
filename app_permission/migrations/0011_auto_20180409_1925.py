# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-04-09 11:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_permission', '0010_permission_display_icon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mainmenuitem',
            name='parent',
        ),
        migrations.AddField(
            model_name='mainmenuitem',
            name='parent_perm',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='parent_item', to='app_permission.Permission'),
        ),
    ]
