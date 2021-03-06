# Generated by Django 2.1.1 on 2019-03-12 14:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0026_auto_20190311_1859'),
        ('deposit_and_credit', '0048_loandemandforthismonth'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditAmount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_date', models.DateField(auto_now_add=True)),
                ('amount', models.FloatField(default=0, verbose_name='余额（万元）')),
                ('lu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='scraper.LuLedger')),
            ],
            options={
                'verbose_name': '信贷余额',
                'verbose_name_plural': '信贷余额',
            },
        ),
    ]
