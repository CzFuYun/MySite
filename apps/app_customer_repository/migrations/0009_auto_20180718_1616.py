# Generated by Django 2.0.2 on 2018-07-18 08:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_customer_repository', '0008_auto_20180718_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectrepository',
            name='pretrial_doc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app_customer_repository.PretrialDocument', verbose_name='预审表'),
        ),
    ]
