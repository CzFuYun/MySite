# Generated by Django 2.0.2 on 2018-09-12 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0027_auto_20180820_1318'),
        ('app_customer_repository', '0028_pretrialmeeting_caption'),
    ]

    operations = [
        migrations.AddField(
            model_name='pretrialdocument',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='root_db.Department'),
        ),
    ]