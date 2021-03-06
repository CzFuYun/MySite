# Generated by Django 2.0.2 on 2018-06-21 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deposit_and_credit', '0014_auto_20180620_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='expireprompt',
            name='explain',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='expireprompt',
            name='finish_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='办结日期'),
        ),
        migrations.AlterField(
            model_name='expireprompt',
            name='remark',
            field=models.CharField(default='', max_length=512),
        ),
        migrations.AlterUniqueTogether(
            name='expireprompt',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='expireprompt',
            name='explain_img',
        ),
    ]
