# Generated by Django 2.1.1 on 2019-03-08 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0023_cpledger_is_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='luledger',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='root_db.AccountedCompany', verbose_name='单位名称'),
        ),
    ]
