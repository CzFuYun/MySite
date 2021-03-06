# Generated by Django 2.1.1 on 2019-02-14 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0006_auto_20190214_0910'),
    ]

    operations = [
        migrations.AddField(
            model_name='cpledger',
            name='reply_code',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='批复号'),
        ),
        migrations.AddField(
            model_name='cpledger',
            name='reply_content',
            field=models.TextField(blank=True, null=True, verbose_name='批复内容'),
        ),
        migrations.AddField(
            model_name='cpledger',
            name='reply_date',
            field=models.DateField(blank=True, null=True, verbose_name='批复日'),
        ),
        migrations.AlterField(
            model_name='cpledger',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='root_db.AccountedCompany', verbose_name='客户'),
        ),
    ]
