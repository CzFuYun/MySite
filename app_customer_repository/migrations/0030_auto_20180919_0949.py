# Generated by Django 2.1.1 on 2018-09-19 09:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_customer_repository', '0029_pretrialdocument_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='pretrialdocument',
            name='agree_net',
            field=models.IntegerField(default=0, verbose_name='同意敞口（万元）'),
        ),
        migrations.AddField(
            model_name='pretrialdocument',
            name='exist_net',
            field=models.IntegerField(default=0, verbose_name='已有敞口（万元）'),
        ),
        migrations.AddField(
            model_name='pretrialdocument',
            name='guarantee',
            field=models.TextField(blank=True, null=True, verbose_name='担保方式'),
        ),
        migrations.AddField(
            model_name='pretrialdocument',
            name='net_total',
            field=models.IntegerField(default=0, verbose_name='申报总敞口（万元）'),
        ),
        migrations.AddField(
            model_name='pretrialdocument',
            name='order',
            field=models.IntegerField(default=0, verbose_name='上会顺序'),
        ),
        migrations.AddField(
            model_name='pretrialdocument',
            name='reason',
            field=models.IntegerField(choices=[(0, '未知'), (1, '新增'), (2, '存量新增'), (3, '担保变更'), (4, '其他')], default=0, verbose_name='预审原因'),
        ),
        migrations.AddField(
            model_name='pretrialdocument',
            name='remark',
            field=models.TextField(blank=True, null=True, verbose_name='备注'),
        ),
        migrations.AlterField(
            model_name='pretrialdocument',
            name='accept_date',
            field=models.DateField(auto_now_add=True, null=True, verbose_name='受理日期'),
        ),
        migrations.AlterField(
            model_name='pretrialdocument',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='root_db.Department', verbose_name='经营部门'),
        ),
        migrations.AlterField(
            model_name='pretrialdocument',
            name='document_name',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='预审表'),
        ),
        migrations.AlterField(
            model_name='pretrialdocument',
            name='meeting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app_customer_repository.PretrialMeeting', verbose_name='预审会'),
        ),
        migrations.AlterField(
            model_name='pretrialdocument',
            name='result',
            field=models.IntegerField(choices=[(10, '待预审'), (12, '维持原方案'), (14, '有条件通过'), (20, '通过'), (30, '续议'), (40, '否决')], default=10, verbose_name='审议结果'),
        ),
    ]
