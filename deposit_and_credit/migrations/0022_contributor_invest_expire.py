# Generated by Django 2.0.2 on 2018-07-12 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deposit_and_credit', '0021_contributor_is_green_finance'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributor',
            name='invest_expire',
            field=models.DateField(blank=True, null=True, verbose_name='投行到期日'),
        ),
    ]