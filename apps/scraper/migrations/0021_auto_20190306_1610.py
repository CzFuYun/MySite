# Generated by Django 2.1.1 on 2019-03-06 16:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0020_auto_20190306_1607'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='luledger',
            name='loan_demand',
        ),
        migrations.RemoveField(
            model_name='luledger',
            name='reply_code',
        ),
        migrations.RemoveField(
            model_name='luledger',
            name='reply_content',
        ),
        migrations.RemoveField(
            model_name='luledger',
            name='reply_date',
        ),
    ]
