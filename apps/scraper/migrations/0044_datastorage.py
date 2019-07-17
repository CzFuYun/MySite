# Generated by Django 2.1.1 on 2019-07-15 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0043_remove_luledger_loan_demand'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataStorage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_date', models.DateField(null=True, verbose_name='数据日期')),
                ('label', models.CharField(max_length=16, null=True, verbose_name='标签')),
                ('statistic_caliber', models.CharField(choices=[('rh', '人行'), ('yj', '银监'), ('jc', '计财')], max_length=8, null=True, verbose_name='统计口径')),
                ('data', models.CharField(max_length=32, null=True, verbose_name='数据')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='备注')),
            ],
            options={
                'verbose_name': '数据记录',
                'verbose_name_plural': '数据记录',
            },
        ),
    ]
