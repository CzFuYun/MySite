# Generated by Django 2.1.1 on 2019-03-02 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0014_cpledger_expire_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='cpledger',
            name='is_special',
            field=models.BooleanField(default=False, verbose_name='特别授信'),
        ),
    ]
