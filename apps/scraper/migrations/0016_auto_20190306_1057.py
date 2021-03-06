# Generated by Django 2.1.1 on 2019-03-06 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0015_cpledger_is_special'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dailyleishou',
            options={'verbose_name': '回收', 'verbose_name_plural': '回收'},
        ),
        migrations.AddField(
            model_name='dailyleishou',
            name='dcms_business',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='scraper.DcmsBusiness', verbose_name='业务种类'),
        ),
        migrations.AlterField(
            model_name='dailyleishou',
            name='retract_amount',
            field=models.FloatField(default=0, verbose_name='收回金额（人民币，元）'),
        ),
    ]
