# Generated by Django 2.1.1 on 2019-03-06 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0037_auto_20190301_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountedcompany',
            name='name',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='账户名称'),
        ),
    ]
