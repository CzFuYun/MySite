# Generated by Django 2.1.1 on 2019-02-12 16:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deposit_and_credit', '0040_auto_20190212_1606'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loandemand',
            name='add_date',
        ),
    ]