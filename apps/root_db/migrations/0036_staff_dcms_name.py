# Generated by Django 2.1.1 on 2019-03-01 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0035_accountedcompany_add_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='dcms_name',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='信贷系统用户名'),
        ),
    ]
