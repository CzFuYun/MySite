# Generated by Django 2.0.2 on 2018-07-20 08:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0023_typeof3311_remark'),
        ('app_customer_repository', '0012_auto_20180719_1714'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectrepository',
            name='approver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='approver', to='root_db.Staff', verbose_name='初审'),
        ),
    ]
