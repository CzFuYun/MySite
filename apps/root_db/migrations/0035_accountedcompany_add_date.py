# Generated by Django 2.1.1 on 2019-02-27 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0034_auto_20190214_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountedcompany',
            name='add_date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
