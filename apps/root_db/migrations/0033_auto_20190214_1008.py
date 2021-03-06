# Generated by Django 2.1.1 on 2019-02-14 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0032_accountedcompany_dcms_customer_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountedcompany',
            name='cf_num',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='信贷文件编号'),
        ),
        migrations.AddField(
            model_name='accountedcompany',
            name='rlk_cf',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='accountedcompany',
            name='rlk_customer',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
