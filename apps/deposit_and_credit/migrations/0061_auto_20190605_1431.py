# Generated by Django 2.1.1 on 2019-06-05 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deposit_and_credit', '0060_auto_20190605_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loandemand',
            name='plan_date',
            field=models.DateField(verbose_name='拟投/所属月份'),
        ),
    ]
