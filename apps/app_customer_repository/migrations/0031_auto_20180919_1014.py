# Generated by Django 2.1.1 on 2018-09-19 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_customer_repository', '0030_auto_20180919_0949'),
    ]

    operations = [
        migrations.AddField(
            model_name='pretrialdocument',
            name='is_defuse',
            field=models.NullBooleanField(verbose_name='是否化解'),
        ),
        migrations.AddField(
            model_name='pretrialdocument',
            name='is_green',
            field=models.NullBooleanField(verbose_name='是否绿色金融'),
        ),
    ]