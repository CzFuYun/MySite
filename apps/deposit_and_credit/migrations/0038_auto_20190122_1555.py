# Generated by Django 2.1.1 on 2019-01-22 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deposit_and_credit', '0037_auto_20190121_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loandemand',
            name='remark',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='备注（规模相关）'),
        ),
    ]
