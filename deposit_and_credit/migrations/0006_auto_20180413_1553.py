# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-04-13 07:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0010_auto_20180413_1406'),
        ('deposit_and_credit', '0005_auto_20180412_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributor',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='root_db.Department', verbose_name='经营部门'),
        ),
        migrations.AddField(
            model_name='contributor',
            name='invest_banking',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='投行业务（万元）'),
        ),
    ]
