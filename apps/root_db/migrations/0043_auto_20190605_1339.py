# Generated by Django 2.1.1 on 2019-06-05 13:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0042_auto_20190515_1117'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='staff',
            options={'ordering': ('sub_department__superior__display_order',), 'verbose_name': '员工', 'verbose_name_plural': '员工'},
        ),
    ]
