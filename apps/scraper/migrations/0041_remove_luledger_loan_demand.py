# Generated by Django 2.1.1 on 2019-05-21 10:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0040_auto_20190521_0948'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='luledger',
            name='loan_demand',
        ),
    ]