# Generated by Django 2.0.2 on 2018-05-07 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0014_accountedperson_dividedpersonalaccount'),
    ]

    operations = [
        migrations.AddField(
            model_name='dividedpersonalaccount',
            name='data_date',
            field=models.DateField(blank=True, null=True, verbose_name='数据日期'),
        ),
    ]
