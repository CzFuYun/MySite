# Generated by Django 2.0.2 on 2018-05-09 03:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0018_remove_staff_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountedcompany',
            name='series',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='root_db.Series', verbose_name='企业系列'),
        ),
    ]