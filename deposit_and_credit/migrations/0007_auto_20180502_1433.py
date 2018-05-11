# Generated by Django 2.0.4 on 2018-05-02 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deposit_and_credit', '0006_auto_20180413_1553'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContributionTrees',
            fields=[
                ('data_date', models.DateField(primary_key=True, serialize=False, verbose_name='数据日期')),
                ('contribution_tree', models.TextField(verbose_name='贡献度结构树')),
            ],
        ),
        migrations.AlterField(
            model_name='contributor',
            name='customer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='root_db.AccountedCompany', verbose_name='客户'),
        ),
    ]