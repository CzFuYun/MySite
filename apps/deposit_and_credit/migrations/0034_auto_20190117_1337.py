# Generated by Django 2.1.1 on 2019-01-17 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deposit_and_credit', '0033_auto_20190117_1334'),
    ]

    operations = [
        migrations.RenameField(
            model_name='loandemand',
            old_name='now_deposit_avg',
            new_name='now_deposit_ratio',
        ),
        migrations.RenameField(
            model_name='loandemand',
            old_name='plan_depo_ratio',
            new_name='plan_deposit_ratio',
        ),
        migrations.RemoveField(
            model_name='loandemand',
            name='expection',
        ),
        migrations.AddField(
            model_name='loandemand',
            name='expect',
            field=models.IntegerField(default=100, verbose_name='月底投放把握(100%)'),
        ),
    ]