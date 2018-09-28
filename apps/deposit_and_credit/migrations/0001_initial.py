# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-04-12 07:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('root_db', '0008_typeof3311_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='ABS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_rate', models.DecimalField(decimal_places=4, max_digits=8, verbose_name='利率（%）')),
                ('loan', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='金额（万元）')),
                ('loan_interest', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='年息（万元）')),
                ('expire', models.DateField(verbose_name='到期日')),
            ],
            options={
                'verbose_name_plural': '资产证券化',
            },
        ),
        migrations.CreateModel(
            name='ContributorList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='root_db.AccountedCompany', verbose_name='客户')),
            ],
            options={
                'verbose_name_plural': '回报客户清单',
            },
        ),
        migrations.CreateModel(
            name='CreditCustomer',
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
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='deposit_and_credit.ContributorList', to_field='customer_id', verbose_name='客户')),
            ],
            options={
                'verbose_name_plural': '用信情况',
            },
        ),
        migrations.CreateModel(
            name='Defuse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='余额（万元）')),
                ('expire', models.DateField(verbose_name='到期日')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='deposit_and_credit.ContributorList', to_field='customer_id', verbose_name='客户')),
            ],
            options={
                'verbose_name_plural': '化解情况',
            },
        ),
        migrations.CreateModel(
            name='DepartmentDeposit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_date', models.DateField(blank=True, null=True)),
                ('amount', models.BigIntegerField(default=0, verbose_name='余额（万元）')),
                ('md_avg', models.BigIntegerField(default=0, verbose_name='月日均（万元）')),
                ('sd_avg', models.BigIntegerField(default=0, verbose_name='季日均（万元）')),
                ('yd_avg', models.BigIntegerField(default=0, verbose_name='年日均（万元）')),
                ('sub_department', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='root_db.SubDepartment')),
            ],
        ),
        migrations.CreateModel(
            name='ExpirePrompt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='root_db.CreditLedger', verbose_name='客户')),
            ],
        ),
        migrations.CreateModel(
            name='IndustryDeposit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_date', models.DateField(blank=True, null=True)),
                ('amount', models.BigIntegerField(default=0, verbose_name='余额（万元）')),
                ('md_avg', models.BigIntegerField(default=0, verbose_name='月日均（万元）')),
                ('sd_avg', models.BigIntegerField(default=0, verbose_name='季日均（万元）')),
                ('yd_avg', models.BigIntegerField(default=0, verbose_name='年日均（万元）')),
                ('industry', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='root_db.Industry')),
            ],
        ),
        migrations.AddField(
            model_name='abs',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='deposit_and_credit.ContributorList', to_field='customer_id', verbose_name='客户'),
        ),
        migrations.AlterUniqueTogether(
            name='industrydeposit',
            unique_together=set([('data_date', 'industry')]),
        ),
        migrations.AlterUniqueTogether(
            name='departmentdeposit',
            unique_together=set([('data_date', 'sub_department')]),
        ),
    ]