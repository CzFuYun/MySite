# Generated by Django 2.0.2 on 2018-07-24 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0024_staff_yellow_red_card'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='red_card_start_date',
            field=models.DateField(blank=True, null=True, verbose_name='红牌起始日'),
        ),
    ]
