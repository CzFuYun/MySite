# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-04-13 06:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0008_typeof3311_level'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='built_order',
        ),
        migrations.AddField(
            model_name='department',
            name='display_order',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='排序先后'),
        ),
    ]
