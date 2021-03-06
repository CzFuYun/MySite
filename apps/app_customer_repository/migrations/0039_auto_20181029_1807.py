# Generated by Django 2.1.1 on 2018-10-29 18:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0029_auto_20180928_1031'),
        ('app_customer_repository', '0038_auto_20180928_1029'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pretrialdocument',
            options={'ordering': ['-accept_date', 'department__display_order'], 'verbose_name': '预审项目', 'verbose_name_plural': '预审项目'},
        ),
        migrations.AddField(
            model_name='pretrialdocument',
            name='industry',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.PROTECT, to='root_db.Industry', verbose_name='行业'),
        ),
        migrations.AddField(
            model_name='pretrialdocument',
            name='stockholder',
            field=models.IntegerField(choices=[(0, 'unknown'), (10, '国有'), (20, '民营'), (30, '外资')], default=0),
        ),
        migrations.AddField(
            model_name='pretrialdocument',
            name='type_of_3311',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.PROTECT, to='root_db.TypeOf3311', verbose_name='3311类型'),
        ),
        migrations.AlterField(
            model_name='customerrepository',
            name='stockholder',
            field=models.IntegerField(choices=[(0, 'unknown'), (10, '国有'), (20, '民营'), (30, '外资')], verbose_name='控股方式'),
        ),
    ]
