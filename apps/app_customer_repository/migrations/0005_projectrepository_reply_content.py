# Generated by Django 2.0.2 on 2018-07-17 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_customer_repository', '0004_auto_20180716_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectrepository',
            name='reply_content',
            field=models.TextField(blank=True, null=True, verbose_name='批复内容'),
        ),
    ]
