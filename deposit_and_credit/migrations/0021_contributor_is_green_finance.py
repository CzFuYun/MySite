# Generated by Django 2.0.2 on 2018-06-29 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deposit_and_credit', '0020_expireprompt_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributor',
            name='is_green_finance',
            field=models.BooleanField(default=False),
        ),
    ]