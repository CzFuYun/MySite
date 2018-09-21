# Generated by Django 2.0.2 on 2018-07-13 08:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0023_typeof3311_remark'),
        ('app_customer_repository', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(max_length=32)),
                ('display_order', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerRepository',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='企业名称')),
                ('simple_name', models.CharField(blank=True, max_length=32, null=True, unique=True)),
                ('credit_file', models.CharField(blank=True, max_length=16, null=True, verbose_name='信贷文件')),
                ('is_strategy', models.BooleanField(default=False, verbose_name='是否战略客户')),
                ('stockholder', models.IntegerField(blank=True, choices=[(10, '国有'), (20, '民营'), (30, '外资')], null=True)),
                ('taxes_2017', models.IntegerField(default=0, verbose_name='2017年纳税（万元）')),
                ('inter_clearing_2017', models.IntegerField(default=0, verbose_name='2017年国际结算（万元）')),
                ('claimer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='root_db.SubDepartment', verbose_name='认领')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='root_db.AccountedCompany', verbose_name='核心客户号')),
                ('industry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='root_db.Industry')),
                ('type_of_3311', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='root_db.TypeOf3311', verbose_name='3311类型')),
            ],
        ),
        migrations.CreateModel(
            name='PretrialDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_name', models.CharField(blank=True, max_length=128, null=True)),
                ('accept_date', models.DateField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PretrialMeeting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meeting_date', models.DateField(blank=True, null=True, verbose_name='会议日期')),
                ('notify_date', models.DateField(blank=True, null=True, verbose_name='通报日期')),
                ('result', models.CharField(blank=True, max_length=256, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(max_length=32)),
                ('status_num', models.DecimalField(decimal_places=1, default=0, max_digits=2)),
                ('display_order', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectExecution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.IntegerField(blank=True, choices=[(10, '预审/立项'), (20, '初审'), (30, '专审'), (40, '信审'), (50, '批复'), (60, '投放'), (70, '结束')], null=True)),
                ('event_date', models.DateField(blank=True, null=True, verbose_name='事件日期')),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('this_time_used', models.IntegerField(default=0, verbose_name='本次投放敞口')),
                ('total_used', models.IntegerField(default=0, verbose_name='累计投放敞口')),
                ('new_net_used', models.IntegerField(default=0, verbose_name='累计投放新增敞口')),
                ('update_count', models.IntegerField(default=0, verbose_name='已更新次数')),
                ('current_progress', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app_customer_repository.Progress', verbose_name='进度')),
            ],
            options={
                'ordering': ('-update_date',),
                'get_latest_by': 'update_date',
            },
        ),
        migrations.CreateModel(
            name='ProjectRemark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectRepository',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(blank=True, max_length=64, null=True, verbose_name='项目名称')),
                ('cp_con_num', models.CharField(blank=True, max_length=32, null=True, verbose_name='授信编号')),
                ('is_green', models.BooleanField(default=False, verbose_name='绿色金融')),
                ('is_focus', models.BooleanField(default=False, verbose_name='重点项目')),
                ('create_date', models.DateField(auto_now_add=True, verbose_name='创建日期')),
                ('plan_pretrial_date', models.DateField(blank=True, null=True, verbose_name='计划预审')),
                ('plan_chushen', models.DateField(blank=True, null=True, verbose_name='计划初审')),
                ('plan_zhuanshen', models.DateField(blank=True, null=True, verbose_name='计划专审')),
                ('plan_xinshen', models.DateField(blank=True, null=True, verbose_name='计划信审')),
                ('plan_reply', models.DateField(blank=True, null=True, verbose_name='计划批复')),
                ('plan_luodi', models.DateField(blank=True, null=True, verbose_name='计划投放')),
                ('total_net', models.IntegerField(default=0, verbose_name='总敞口')),
                ('existing_net', models.IntegerField(default=0, verbose_name='存量敞口')),
                ('account_num', models.DecimalField(decimal_places=2, default=0, max_digits=3, verbose_name='折算户数')),
                ('is_defuse', models.BooleanField(default=False, verbose_name='涉及化解')),
                ('is_pure_credit', models.BooleanField(default=False, verbose_name='纯信用')),
                ('close_date', models.DateField(blank=True, null=True, verbose_name='关闭日期')),
                ('close_reason', models.IntegerField(blank=True, choices=[(10, '预审未通过终止申报'), (20, '申报过程中终止'), (30, '分行续议后终止申报'), (40, '分行否决'), (50, '总行否决'), (60, '获批后不再继续'), (70, '部分落地后终止'), (80, '全部落地')], null=True)),
                ('whose_matter', models.IntegerField(blank=True, choices=[(10, '预审未通过终止申报'), (20, '申报过程中终止'), (30, '分行续议后终止申报'), (40, '分行否决'), (50, '总行否决'), (60, '获批后不再继续'), (70, '部分落地后终止'), (80, '全部落地')], null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Stars',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(blank=True, max_length=32, null=True)),
                ('description', models.CharField(blank=True, max_length=64, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubBusiness',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(max_length=32)),
                ('display_order', models.IntegerField(default=0)),
                ('superior', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app_customer_repository.Business')),
            ],
        ),
        migrations.RemoveField(
            model_name='customerstore',
            name='claimer',
        ),
        migrations.RemoveField(
            model_name='customerstore',
            name='district',
        ),
        migrations.RemoveField(
            model_name='customerstore',
            name='industry',
        ),
        migrations.RemoveField(
            model_name='customerstore',
            name='type_of_3311',
        ),
        migrations.DeleteModel(
            name='CustomerStore',
        ),
        migrations.AddField(
            model_name='projectrepository',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app_customer_repository.SubBusiness'),
        ),
        migrations.AddField(
            model_name='projectrepository',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app_customer_repository.CustomerRepository'),
        ),
        migrations.AddField(
            model_name='projectrepository',
            name='pretrial_doc',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app_customer_repository.PretrialDocument', verbose_name='预审表'),
        ),
        migrations.AddField(
            model_name='projectrepository',
            name='staff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='root_db.Staff'),
        ),
        migrations.AddField(
            model_name='projectexecution',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app_customer_repository.ProjectRepository'),
        ),
        migrations.AddField(
            model_name='projectexecution',
            name='remark',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app_customer_repository.ProjectRemark'),
        ),
        migrations.AddField(
            model_name='progress',
            name='star',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app_customer_repository.Stars'),
        ),
        migrations.AddField(
            model_name='progress',
            name='suit_for_business',
            field=models.ManyToManyField(to='app_customer_repository.SubBusiness'),
        ),
        migrations.AddField(
            model_name='pretrialdocument',
            name='meeting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app_customer_repository.PretrialMeeting'),
        ),
    ]
