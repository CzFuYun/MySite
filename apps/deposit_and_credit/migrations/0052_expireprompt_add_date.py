# Generated by Django 2.1.1 on 2019-03-26 09:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('deposit_and_credit', '0051_auto_20190322_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='expireprompt',
            name='add_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
