# Generated by Django 2.0.4 on 2018-08-01 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_customer_repository', '0018_auto_20180726_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='subbusiness',
            name='is_focus',
            field=models.BooleanField(default=False, verbose_name='是否重点产品'),
        ),
    ]