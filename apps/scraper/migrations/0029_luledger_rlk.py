# Generated by Django 2.1.1 on 2019-03-12 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0028_auto_20190312_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='luledger',
            name='rlk',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
