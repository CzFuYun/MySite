# Generated by Django 2.1.1 on 2019-02-01 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0002_auto_20190122_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='luledger',
            name='current_amount',
            field=models.FloatField(default=0, verbose_name='当前地区余额（含特别授信）'),
        ),
    ]