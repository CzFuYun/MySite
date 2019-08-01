# Generated by Django 2.1.1 on 2019-07-31 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deposit_and_credit', '0064_expireprompt_approve_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expireprompt',
            name='expire_date',
            field=models.DateField(null=True, verbose_name='到期日'),
        ),
        migrations.AlterField(
            model_name='loandemand',
            name='already_achieved',
            field=models.FloatField(default=0, verbose_name='当月累放'),
        ),
        migrations.AlterField(
            model_name='loandemand',
            name='expire_amount',
            field=models.FloatField(default=0, verbose_name='存量到期金额'),
        ),
        migrations.AlterField(
            model_name='loandemand',
            name='original_plan_amount',
            field=models.FloatField(default=0, verbose_name='月初拟放'),
        ),
        migrations.AlterField(
            model_name='loandemand',
            name='plan_amount',
            field=models.FloatField(default=0, verbose_name='当前拟放'),
        ),
        migrations.AlterField(
            model_name='loandemand',
            name='this_month_leishou',
            field=models.FloatField(default=0, verbose_name='当月累收'),
        ),
    ]