# Generated by Django 2.1.1 on 2019-03-21 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0033_auto_20190318_1100'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cpledger',
            name='is_virtual',
        ),
        migrations.AlterField(
            model_name='cpledger',
            name='cp_type',
            field=models.CharField(blank=True, choices=[('CP', '地区'), ('SME', '小微'), ('CS', '个人'), ('V', '虚拟')], max_length=8, null=True, verbose_name='类型'),
        ),
    ]
