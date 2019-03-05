from decimal import Decimal

from django.db import models
from django.db.models import Q

from .crp import CrpHttpRequest
from .dcms_request import DcmsHttpRequest
from deposit_and_credit.models_operation import DateOperation
from root_db.models import AccountedCompany, Staff


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
    cp_rlk = models.CharField(max_length=32, blank=True, null=True)
    customer = models.ForeignKey(to='root_db.AccountedCompany', blank=True, null=True, on_delete=models.CASCADE, verbose_name='客户')
    dcms_customer_code = models.CharField(max_length=8, blank=True, null=True, verbose_name='客户编号')
    # customer_name = models.CharField(max_length=64, blank=True, null=True, verbose_name='客户名称')
    staff = models.ForeignKey('root_db.Staff', blank=True, null=True, on_delete=models.PROTECT, verbose_name='客户经理')
    reply_date = models.DateField(blank=True, null=True, verbose_name='批复日')
    reply_code = models.CharField(max_length=32, blank=True, null=True, verbose_name='批复号')
    reply_content = models.TextField(blank=True, null=True, verbose_name='批复内容')
    expire_date = models.DateField(blank=True, null=True, verbose_name='授信到期日')
    is_special = models.BooleanField(default=False, verbose_name='特别授信')
    # apply_amount = models.DecimalField(default=0, max_digits=12, decimal_places=2, verbose_name='申报金额')
    # reply_amount = models.DecimalField(default=0, max_digits=12, decimal_places=2, verbose_name='批复金额')
    # baozheng = models.DecimalField(default=0, max_digits=12, decimal_places=2, verbose_name='保证担保')
    # diya = models.DecimalField(default=0, max_digits=12, decimal_places=2, verbose_name='抵押担保')
    # zhiya = models.DecimalField(default=0, max_digits=12, decimal_places=2, verbose_name='质押担保')
    # is_auto_added = models.BooleanField(default=False, verbose_name='是否自动生成')

    class Meta:
        verbose_name = '授信台账'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.cp_num

    # @classmethod
    # def createNotAccountedCustomerByDcms(cls, customer_code, dcms=None):
    #     if dcms is None:
    #         dcms = DcmsHttpRequest()
    #         dcms.login()
    #     dcms.search_customer()
    #     pass

    @classmethod
    def _bulkCreateCpFromCrp(cls, reply_date__gte=None):
        crp = CrpHttpRequest()
        crp.login()
        dcms = DcmsHttpRequest()
        dcms.login()
        imp_date = DateOperation()
        last_add = imp_date.neighbour_date_date_str(cls, imp_date.today_str, 'add_date') or imp_date.delta_date(-1)
        reply_date__gte = reply_date__gte or last_add
        cp = crp.getCp(
            *['客户名称', '客户编号', '授信参考编号', '批复时间', '批复编号', '授信到期时间', '建档人', '是否特别授信'],
            **{
                '申报金额（原币）': crp.NumCondition.between(1, 10000000000),
                '批复时间': crp.DateCondition.between(reply_date__gte, crp.data_date),
            }
        )
        for page in cp:
            page_data = crp.parseQueryResultToDictList(page)
            for i in range(len(page_data)):
                row_data = page_data[i]
                customer_name = row_data['客户名称']
                cp_num = row_data['授信参考编号']
                print('准备添加/更新授信', customer_name, cp_num)
                customer_code = row_data['客户编号']
                reply_date = row_data['批复时间']
                reply_code = row_data['批复编号']
                is_special = True if row_data['是否特别授信'].upper() == 'Y' else False
                cp_rlk = dcms.search_cp(cp_num)
                customer = AccountedCompany.pickCustomer(customer_name, customer_code, dcms)
                expire_date = row_data['授信到期时间']
                if not expire_date:
                    expire_date = imp_date.delta_date(365, row_data['批复时间'])
                if not cls.objects.filter(cp_num=cp_num).exists():
                    staff = Staff.pickStaffByName(row_data['建档人'])
                    cls(
                        customer=customer,
                        cp_num=cp_num,
                        staff=staff,
                        reply_date=reply_date,
                        reply_code=reply_code,
                        expire_date=expire_date,
                        cp_rlk=cp_rlk,
                        is_special=is_special
                        # apply_amount=float(row_data['申报金额（原币）'].replace(',', ''))*float(row_data['汇率']),
                        # reply_amount=float(row_data['批复金额(原币）'].replace(',', ''))*float(row_data['汇率']),
                    ).save()
                # else:
                #     staff_name = row_data['建档人']
                #     obj = cls.objects.filter(cp_num=cp_num)
                #     if obj[0].staff.name != staff_name:
                #         staff = Staff.pickStaffByName(row_data['建档人'])
                #         obj.update(staff=staff)
                #     obj.update(
                #         customer=customer,
                #         reply_date=reply_date,
                #         reply_code=reply_code,
                #         expire_date=expire_date,
                #         cp_rlk=cp_rlk,
                #         is_special=is_special
                #     )


    @classmethod
    def _bulkCreateSmeCpFromCrp(cls, reply_date__gte=None):
        crp = CrpHttpRequest()
        crp.login()
        dcms = DcmsHttpRequest()
        dcms.login('czzxsk', '111111', 'SMEDCMS')
        imp_date = DateOperation()
        last_add = imp_date.neighbour_date_date_str(cls, imp_date.today_str, 'add_date') or imp_date.delta_date(-1)
        reply_date__gte = reply_date__gte or last_add
        cp = crp.getSmeCp(
            *['客户名称', '客户编号', '授信参考编号', '批复时间', '批复编号', '授信到期时间', '是否特别授信', '建档人'],
            **{
                '批复时间': crp.DateCondition.between(reply_date__gte, crp.data_date),
                '批复金额（原币）': crp.NumCondition.between(1, 10000000000),
            }
        )
        for page in cp:
            page_data = crp.parseQueryResultToDictList(page)
            for i in range(len(page_data)):
                row_data = page_data[i]
                customer_name = row_data['客户名称']
                cp_num = row_data['授信参考编号']
                print('准备添加/更新授信', customer_name, cp_num)
                customer_code = row_data['客户编号']
                reply_date = row_data['批复时间']
                reply_code = row_data['批复编号']
                is_special = True if row_data['是否特别授信'].upper() == 'Y' else False
                cp_rlk = dcms.search_cp(cp_num)
                customer = AccountedCompany.pickCustomer(customer_name, customer_code, dcms)
                expire_date = row_data['授信到期时间']
                if not expire_date:
                    expire_date = imp_date.delta_date(365, row_data['批复时间'])
                staff = Staff.pickStaffByDcmsName(row_data['建档人'])
                if not cls.objects.filter(cp_num=cp_num).exists():
                    cls(
                        customer=customer,
                        cp_num=cp_num,
                        staff=staff,
                        reply_date=reply_date,
                        reply_code=reply_code,
                        expire_date=expire_date,
                        cp_rlk=cp_rlk,
                        is_special=is_special
                    ).save()
                # else:
                #     staff_name = row_data['建档人']
                #     obj = cls.objects.filter(cp_num=cp_num)
                #     if obj[0].staff is None or obj[0].staff.name != staff_name:
                #         obj.update(staff=staff)
                #     obj.update(
                #         customer=customer,
                #         reply_date=reply_date,
                #         reply_code=reply_code,
                #         expire_date=expire_date,
                #         cp_rlk=cp_rlk,
                #         is_special=is_special
                #     )

    @classmethod
    def _bulkCreateCsCpFromCrp(cls, reply_date__gte=None):
        crp = CrpHttpRequest()
        crp.login()
        dcms = DcmsHttpRequest()
        # dcms.login(dcms_type='sme')
        dcms.login('czhn', 'hn106412', 'DCMSCS')
        imp_date = DateOperation()
        last_add = imp_date.neighbour_date_date_str(cls, imp_date.today_str, 'add_date') or imp_date.delta_date(-1)
        reply_date__gte = reply_date__gte or last_add
        cp = crp.getCsCp(
            *['客户名称', '客户编号', '授信编号', '批复时间', '批复编号', '授信到期时间', '客户经理'],
            **{
                '授信额度(元)': crp.NumCondition.gt(0),
                '批复时间': crp.DateCondition.between(reply_date__gte, crp.data_date),
            }
        )
        for page in cp:
            page_data = crp.parseQueryResultToDictList(page)
            for i in range(len(page_data)):
                row_data = page_data[i]
                customer_name = row_data['客户名称']
                cp_num = row_data['授信编号']
                print('准备添加/更新授信', customer_name, cp_num)
                customer_code = row_data['客户编号']
                reply_date = row_data['批复时间']
                reply_code = row_data['批复编号']
                is_special = False
                cp_rlk = dcms.search_cp(cp_num)
                customer = AccountedCompany.pickCustomer(customer_name, customer_code, dcms)
                expire_date = row_data['授信到期时间']
                if not expire_date:
                    expire_date = imp_date.delta_date(365, row_data['批复时间'])
                staff = Staff.pickStaffByName(row_data['客户经理'], 1)
                if not cls.objects.filter(cp_num=cp_num).exists():
                    cls(
                        customer=customer,
                        cp_num=cp_num,
                        staff=staff,
                        reply_date=reply_date,
                        reply_code=reply_code,
                        expire_date=expire_date,
                        cp_rlk=cp_rlk,
                        is_special=is_special
                    ).save()
                else:
                    staff_name = row_data['客户经理']
                    obj = cls.objects.filter(cp_num=cp_num)
                    if obj[0].staff is None or obj[0].staff.name != staff_name:
                        obj.update(staff=staff)
                    obj.update(
                        customer=customer,
                        reply_date=reply_date,
                        reply_code=reply_code,
                        expire_date=expire_date,
                        cp_rlk=cp_rlk,
                        is_special=is_special
                    )

    @classmethod
    def fillReplyContentFromDcms(cls, dcms=None):
        '''
        爬取信贷系统授信批复
        :return:
        '''
        pass


class LuLedger(models.Model):
    pay_method_choices = (
        (1, '受托'),
        (2, '自主'),
    )
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateField(auto_now=True, verbose_name='更新日')
    loan_demand = models.ForeignKey(to='deposit_and_credit.LoanDemand', on_delete=models.PROTECT, verbose_name='规模安排')
    lu_num = models.CharField(max_length=32, primary_key=True, verbose_name='放款参考编号')
    is_green = models.BooleanField(default=False, verbose_name='绿色金融')
    pay_method = models.IntegerField(choices=pay_method_choices, default=1, verbose_name='支付方式')
    is_xvbao = models.NullBooleanField(blank=True, null=True, verbose_name='续保标志')
    has_separation_of_duty = models.BooleanField(default=True, verbose_name='信贷责任划分状（有/无）')
    has_sign_receipted = models.BooleanField(default=True, verbose_name='送达签收单合同（有/无）')
    policy_expire = models.DateField(blank=True, null=True, verbose_name='保单到期日')
    has_used_relending_money = models.BooleanField(default=False, verbose_name='是否转贷资金')
    cp = models.ForeignKey(to='CpLedger', db_column='cp_num', blank=True, null=True, on_delete=models.CASCADE, verbose_name='授信')
    inspector = models.ForeignKey(to='root_db.Staff', blank=True, null=True, related_name='inspector', on_delete=models.PROTECT, verbose_name='审查人员')
    department = models.ForeignKey(to='root_db.Department', blank=True, null=True, on_delete=models.PROTECT, verbose_name='经营部门')
    staff = models.ForeignKey(to='root_db.Staff', blank=True, null=True, on_delete=models.PROTECT, verbose_name='客户经理')
    customer = models.ForeignKey(to='root_db.AccountedCompany', on_delete=models.PROTECT, verbose_name='单位名称')
    customer_code = models.CharField(max_length=8, blank=True, null=True, verbose_name='客户编号')
    dcms_business = models.ForeignKey(to='DcmsBusiness', blank=True, null=True, on_delete=models.PROTECT, verbose_name='业务种类')
    lend_date = models.DateField(blank=True, null=True, verbose_name='放款日期')
    plan_expire = models.DateField(blank=True, null=True, verbose_name='计划到期日')
    month_dif = models.IntegerField(default=12, verbose_name='期限(月)')
    currency_type = models.CharField(max_length=8, default='CNY', verbose_name='业务币种')
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
    current_amount = models.FloatField(default=0, verbose_name='当前地区余额（含特别授信）')

    class Meta:
        verbose_name = '放款台账'
        verbose_name_plural = verbose_name
        ordering = ('-add_date', )

    def __str__(self):
        return self.lu_num

    @classmethod
    def fillInfo(cls, loan_date__gte=None):
        '''
        爬取企贷表，补完台账
        :return:
        '''
        crp = CrpHttpRequest()
        crp.login()
        if loan_date__gte is not None:
            crp.setDataDate(loan_date__gte)
        qidai = crp.getQiDai(*['放款参考编号', '业务余额(原币)', '总账汇率'], **{'业务余额(原币)': crp.NumCondition.gt(0)})
        for page in qidai:
            pass

    @classmethod
    def create(cls, lu_num):
        dcms = DcmsHttpRequest()
        dcms.login()
        dcms.search_lu(lu_num)
        pass

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        pass


class DailyLeiShou(models.Model):
    add_date = models.DateField(auto_now_add=True)
    contract_code = models.CharField(max_length=32, blank=True, null=True, verbose_name='信贷合同编号')
    retract_amount = models.FloatField(default=0, verbose_name='收回金额（元）')
    retract_date = models.FloatField(blank=True, null=True, verbose_name='收回日期')

    class Meta:
        verbose_name = '累收'
        verbose_name_plural = verbose_name

    @classmethod
    def getDailyLeishou(cls, retract_date__gte=None):
        pass