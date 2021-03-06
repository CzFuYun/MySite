# Generated by Django 2.1.1 on 2019-05-15 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deposit_and_credit', '0052_expireprompt_add_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='loandemandforthismonth',
            options={'verbose_name': '本月贷款规模安排', 'verbose_name_plural': '本月贷款规模安排'},
        ),
        migrations.AddField(
            model_name='loandemand',
            name='this_month_must',
            field=models.NullBooleanField(verbose_name='本月必保'),
        ),
        migrations.AlterField(
            model_name='loandemand',
            name='contract',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='放款合同号（到期）'),
        ),
    ]
