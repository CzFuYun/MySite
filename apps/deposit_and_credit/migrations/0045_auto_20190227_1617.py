# Generated by Django 2.1.1 on 2019-02-27 16:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_customer_repository', '0046_auto_20190117_1128'),
        ('deposit_and_credit', '0044_auto_20190227_1329'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loandemand',
            name='new_increase',
        ),
        migrations.AddField(
            model_name='loandemand',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app_customer_repository.ProjectRepository', verbose_name='项目储备'),
        ),
    ]