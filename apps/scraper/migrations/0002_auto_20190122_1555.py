# Generated by Django 2.1.1 on 2019-01-22 15:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('root_db', '0031_auto_20190117_1334'),
        ('scraper', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DcmsBusiness',
            fields=[
                ('code', models.CharField(max_length=8, primary_key=True, serialize=False, verbose_name='业务编号')),
                ('caption', models.CharField(max_length=64, unique=True, verbose_name='业务名称')),
            ],
            options={
                'verbose_name': '信贷系统业务',
                'verbose_name_plural': '信贷系统业务',
            },
        ),
        migrations.AddField(
            model_name='luledger',
            name='contract_code',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='信贷合同编号'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='currency_type',
            field=models.CharField(choices=[('CNY', '人民币'), ('USD', '美元')], default='CNY', max_length=8, verbose_name='业务币种'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='customer_code',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='客户编号'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='root_db.Department', verbose_name='经营部门'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='float_ratio',
            field=models.FloatField(default=0, verbose_name='浮动比例%'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='guarantee',
            field=models.TextField(blank=True, null=True, verbose_name='担保方式'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='has_separation_of_duty',
            field=models.BooleanField(default=True, verbose_name='信贷责任划分状（有/无）'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='has_sign_receipted',
            field=models.BooleanField(default=True, verbose_name='送达签收单合同（有/无）'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='has_used_relending_money',
            field=models.BooleanField(default=False, verbose_name='是否转贷资金'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='inspector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inspector', to='root_db.Staff', verbose_name='审查人员'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='is_xvbao',
            field=models.NullBooleanField(verbose_name='续保标志'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='lend_amount',
            field=models.FloatField(default=0, verbose_name='贷款金额（元）'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='lend_date',
            field=models.DateField(blank=True, null=True, verbose_name='放款日期'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='month_dif',
            field=models.IntegerField(default=12, verbose_name='期限(月)'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='net_amount',
            field=models.FloatField(default=0, verbose_name='敞口金额'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='pay_method',
            field=models.IntegerField(choices=[(1, '受托')], default=1, verbose_name='支付方式'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='plan_expire',
            field=models.DateField(blank=True, null=True, verbose_name='计划到期日'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='pledge_ratio',
            field=models.FloatField(default=0, verbose_name='保证金或质押担保比例%'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='policy_expire',
            field=models.DateField(blank=True, null=True, verbose_name='保单到期日'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='rate',
            field=models.FloatField(default=0, verbose_name='利率或费率%'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='reply_code',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='授信批复编号'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='reply_content',
            field=models.TextField(blank=True, null=True, verbose_name='授信批复内容'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='reply_date',
            field=models.DateField(blank=True, null=True, verbose_name='授信批复日期'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='staff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='root_db.Staff', verbose_name='客户经理'),
        ),
        migrations.AlterField(
            model_name='luledger',
            name='lu_num',
            field=models.CharField(max_length=32, primary_key=True, serialize=False, verbose_name='放款参考编号'),
        ),
        migrations.AddField(
            model_name='luledger',
            name='dcms_business',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='scraper.DcmsBusiness', verbose_name='业务种类'),
        ),
    ]
