# Generated by Django 2.0.2 on 2018-06-22 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deposit_and_credit', '0016_expireprompt_punishment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expireprompt',
            name='finish_date',
            field=models.DateField(blank=True, null=True, verbose_name='办结日期'),
        ),
    ]