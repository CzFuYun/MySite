# Generated by Django 2.1.1 on 2019-03-06 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0019_auto_20190306_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='luledger',
            name='has_separation_of_duty',
            field=models.NullBooleanField(verbose_name='信贷责任划分状（有/无）'),
        ),
        migrations.AlterField(
            model_name='luledger',
            name='has_sign_receipted',
            field=models.NullBooleanField(verbose_name='送达签收单合同（有/无）'),
        ),
        migrations.AlterField(
            model_name='luledger',
            name='has_used_relending_money',
            field=models.NullBooleanField(verbose_name='是否转贷资金'),
        ),
        migrations.AlterField(
            model_name='luledger',
            name='is_green',
            field=models.NullBooleanField(verbose_name='绿色金融'),
        ),
    ]
