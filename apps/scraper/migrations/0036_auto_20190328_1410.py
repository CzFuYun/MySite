# Generated by Django 2.1.1 on 2019-03-28 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0035_auto_20190326_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='luledger',
            name='is_inspected',
            field=models.BooleanField(default=False, verbose_name='已发放'),
        ),
        migrations.AlterField(
            model_name='luledger',
            name='month_dif',
            field=models.IntegerField(default=0, verbose_name='期限(月)'),
        ),
    ]
