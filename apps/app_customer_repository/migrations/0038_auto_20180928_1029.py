# Generated by Django 2.1.1 on 2018-09-28 10:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_customer_repository', '0037_auto_20180926_1713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerrepository',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='root_db.AccountedCompany', verbose_name='核心客户号'),
        ),
        migrations.AlterField(
            model_name='customerrepository',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='root_db.Department', verbose_name='管户部门'),
        ),
        migrations.AlterField(
            model_name='customerrepository',
            name='industry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='root_db.Industry', verbose_name='行业门类'),
        ),
        migrations.AlterField(
            model_name='customerrepository',
            name='type_of_3311',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='root_db.TypeOf3311', verbose_name='3311类型'),
        ),
        migrations.AlterField(
            model_name='pretrialdocument',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='root_db.Department', verbose_name='经营部门'),
        ),
        migrations.AlterField(
            model_name='pretrialdocument',
            name='meeting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_customer_repository.PretrialMeeting', verbose_name='预审会'),
        ),
        migrations.AlterField(
            model_name='progress',
            name='star',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_customer_repository.Stars'),
        ),
        migrations.AlterField(
            model_name='projectexecution',
            name='current_progress',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_customer_repository.Progress', verbose_name='进度'),
        ),
        migrations.AlterField(
            model_name='projectexecution',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_customer_repository.ProjectRepository', verbose_name='项目'),
        ),
        migrations.AlterField(
            model_name='projectexecution',
            name='remark',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='app_customer_repository.ProjectRemark', verbose_name='备注'),
        ),
        migrations.AlterField(
            model_name='projectrepository',
            name='approver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approver', to='root_db.Staff', verbose_name='专审'),
        ),
        migrations.AlterField(
            model_name='projectrepository',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_customer_repository.SubBusiness', verbose_name='业务品种'),
        ),
        migrations.AlterField(
            model_name='projectrepository',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_customer_repository.CustomerRepository', verbose_name='客户'),
        ),
        migrations.AlterField(
            model_name='projectrepository',
            name='pre_approver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pre_approver', to='root_db.Staff', verbose_name='初审'),
        ),
        migrations.AlterField(
            model_name='projectrepository',
            name='pretrial_doc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_customer_repository.PretrialDocument', verbose_name='预审表'),
        ),
        migrations.AlterField(
            model_name='projectrepository',
            name='staff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='root_db.Staff', verbose_name='客户经理'),
        ),
        migrations.AlterField(
            model_name='subbusiness',
            name='superior',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_customer_repository.Business'),
        ),
        migrations.AlterField(
            model_name='targettask',
            name='business',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_customer_repository.Business'),
        ),
        migrations.AlterField(
            model_name='targettask',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='root_db.Department'),
        ),
    ]
