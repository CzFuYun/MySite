# Generated by Django 2.1.1 on 2019-05-21 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0039_auto_20190517_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='luledger',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]