# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-04-12 09:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0008_typeof3311_level'),
        ('deposit_and_credit', '0002_auto_20180412_1723'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contributor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approve_line', models.SmallIntegerField(choices=[(1, ''), (2, '地区'), (3, '小微')], default=1, verbose_name='审批条线')),
                ('loan_rate', models.DecimalField(decimal_places=4, default=0, max_digits=8, verbose_name='加权利率（%）')),
                ('loan_interest', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='贷款年息（万元）')),
                ('loan', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='贷款含ABS余额（万元）')),
                ('net_BAB', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='银票净额（万元）')),
                ('net_TF', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='贸易融资净额（万元）')),
                ('net_GL', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='保函净额（万元）')),
                ('net_total', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='一般用信净额（万元）')),
                ('lr_BAB', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='全额银票（万元）')),
                ('ABS_expire', models.DateField(blank=True, null=True, verbose_name='ABS到期日')),
                ('defuse_expire', models.DateField(blank=True, null=True, verbose_name='化解到期日')),
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='root_db.AccountedCompany', verbose_name='客户')),
            ],
            options={
                'verbose_name_plural': '回报客户清单',
            },
        ),
        migrations.RemoveField(
            model_name='contributorlist',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='creditcustomer',
            name='customer',
        ),
        migrations.DeleteModel(
            name='ContributorList',
        ),
        migrations.DeleteModel(
            name='CreditCustomer',
        ),
    ]