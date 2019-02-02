from django.db import models


from .crp import CrpHttpRequest
from .dcms_request import DcmsHttpRequest

class DcmsBusiness(models.Model):
    code = models.CharField(max_length=8, primary_key=True, verbose_name='业务编号')
    caption = models.CharField(max_length=64, unique=True, verbose_name='业务名称')

    class Meta:
        verbose_name = '信贷系统业务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code + '-' + self.caption


class CpLedger(models.Model):
    add_date = models.DateField(auto_now_add=True)
    cp_num = models.CharField(max_length=32, primary_key=True, verbose_name='参考编号')
    customer = models.ForeignKey(to='root_db.Customer', on_delete=models.CASCADE, verbose_name='客户')
    is_auto_added = models.BooleanField(default=False, verbose_name='是否自动生成')


class LuLedger(models.Model):
    pay_method_choices = (
        (1, '受托'),
    )
    currency_type_choices = (
        ('CNY', '人民币'),
        ('USD', '美元'),
    )
    add_date = models.DateField(auto_now_add=True)
    current_amount = models.FloatField(default=0, verbose_name='当前地区余额（含特别授信）')
    update_date = models.DateField(auto_now=True, verbose_name='更新日')
    cp = models.ForeignKey(to='CpLedger', db_column='cp_num', blank=True, null=True, on_delete=models.CASCADE, verbose_name='授信')
    loan_demand = models.ForeignKey(to='deposit_and_credit.LoanDemand', on_delete=models.PROTECT, verbose_name='规模安排')
    inspector = models.ForeignKey(to='root_db.Staff', blank=True, null=True, related_name='inspector', on_delete=models.PROTECT, verbose_name='审查人员')
    department = models.ForeignKey(to='root_db.Department', blank=True, null=True, on_delete=models.PROTECT, verbose_name='经营部门')
    staff = models.ForeignKey(to='root_db.Staff', blank=True, null=True, on_delete=models.PROTECT, verbose_name='客户经理')
    customer = models.ForeignKey(to='root_db.AccountedCompany', on_delete=models.PROTECT, verbose_name='单位名称')
    customer_code = models.CharField(max_length=8, blank=True, null=True, verbose_name='客户编号')
    pay_method = models.IntegerField(choices=pay_method_choices, default=1, verbose_name='支付方式')
    lu_num = models.CharField(max_length=32, primary_key=True, verbose_name='放款参考编号')
    dcms_business = models.ForeignKey(to='DcmsBusiness', blank=True, null=True, on_delete=models.PROTECT, verbose_name='业务种类')
    lend_date = models.DateField(blank=True, null=True, verbose_name='放款日期')
    plan_expire = models.DateField(blank=True, null=True, verbose_name='计划到期日')
    month_dif = models.IntegerField(default=12, verbose_name='期限(月)')
    currency_type = models.CharField(max_length=8, choices=currency_type_choices, default='CNY', verbose_name='业务币种')
    lend_amount = models.FloatField(default=0, verbose_name='贷款金额（元）')
    rate = models.FloatField(default=0, verbose_name='利率或费率%')
    pledge_ratio = models.FloatField(default=0, verbose_name='保证金或质押担保比例%')
    float_ratio = models.FloatField(default=0, verbose_name='浮动比例%')
    net_amount = models.FloatField(default=0, verbose_name='敞口金额')
    guarantee = models.TextField(verbose_name='担保方式', blank=True, null=True)
    contract_code = models.CharField(max_length=32, unique=True, blank=True, null=True, verbose_name='信贷合同编号')
    reply_date = models.DateField(blank=True, null=True, verbose_name='授信批复日期')
    reply_code = models.CharField(max_length=16, blank=True, null=True, verbose_name='授信批复编号')
    reply_content = models.TextField(blank=True, null=True, verbose_name='授信批复内容')
    is_xvbao = models.NullBooleanField(blank=True, null=True, verbose_name='续保标志')
    has_separation_of_duty = models.BooleanField(default=True, verbose_name='信贷责任划分状（有/无）')
    has_sign_receipted = models.BooleanField(default=True, verbose_name='送达签收单合同（有/无）')
    policy_expire = models.DateField(blank=True, null=True, verbose_name='保单到期日')
    has_used_relending_money = models.BooleanField(default=False, verbose_name='是否转贷资金')

    class Meta:
        verbose_name = '放款台账'
        verbose_name_plural = verbose_name

    def __str__(self):
        return

    @classmethod
    def updateAmountByQiDai(cls, date_str=None):
        '''
        爬取企贷表，更新地区用信余额
        :return:
        '''
        crp = CrpHttpRequest()
        crp.login()
        if date_str is not None:
            crp.setDataDate(date_str)
        qidai = crp.getQiDai(*['放款参考编号', '业务余额(原币)', '总账汇率'], **{'业务余额(原币)': '>0', '是否小企业客户': "='CP'"})
        for page in qidai:
            pass

    @classmethod
    def create(cls, lu_num):
        dcms = DcmsHttpRequest()
        dcms.login()
        dcms.search_lu(lu_num)
        pass