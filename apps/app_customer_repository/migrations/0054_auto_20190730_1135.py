# Generated by Django 2.1.1 on 2019-07-30 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_customer_repository', '0053_auto_20190730_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectrepository',
            name='luodi',
            field=models.FloatField(default=1, verbose_name='落地金额或比例'),
        ),
    ]
