# Generated by Django 2.1.1 on 2019-02-28 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0011_cpledger_cp_rlk'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cpledger',
            name='apply_amount',
        ),
        migrations.RemoveField(
            model_name='cpledger',
            name='baozheng',
        ),
        migrations.RemoveField(
            model_name='cpledger',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='cpledger',
            name='diya',
        ),
        migrations.RemoveField(
            model_name='cpledger',
            name='is_auto_added',
        ),
        migrations.RemoveField(
            model_name='cpledger',
            name='reply_amount',
        ),
        migrations.RemoveField(
            model_name='cpledger',
            name='zhiya',
        ),
        migrations.AddField(
            model_name='cpledger',
            name='customer_name',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='客户名称'),
        ),
        migrations.AddField(
            model_name='cpledger',
            name='dcms_customer_code',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='客户编号'),
        ),
    ]
