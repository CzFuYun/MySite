# Generated by Django 2.0.2 on 2018-06-28 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deposit_and_credit', '0019_expireprompt_staff_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='expireprompt',
            name='created_at',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]