import re
from decimal import Decimal

from django.db import models
from django.db.models import F, Q, Sum

from MySite.utilities import field_choices_to_dict
from .crp import CrpHttpRequest
from .dcms_request import DcmsHttpRequest, RegExp
from deposit_and_credit.models_operation import DateOperation
from root_db.models import AccountedCompany, Staff, Department
from scraper.dcms_work_flow import LuWorkFlow, CpWorkFlow



class DcmsBusiness(models.Model):
    code = models.CharField(max_length=8, primary_key=True, verbose_name='业务编号')
    caption = models.CharField(max_length=64, unique=True, verbose_name='业务名称')

    class Meta:
        verbose_name = '信贷系统业务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.caption

    @classmethod
    def pickObjectByCaption(cls, caption):
        try:
            return cls.objects.get(caption=caption)
        except:
            print('业务品种', caption, '不存在，请新建')
            code = input('code>>>')
            cls(code=code, caption=caption).save()
            return cls.objects.get(caption=caption)


class CpLedger(models.Model):
    cp_type_choice = (
        ('CP', '地区'),
        ('SME', '小微'),
        ('CS', '个人'),
        ('V', '虚拟'),
    )
    add_date = models.DateField(auto_now_add=True)
    cp_num = models.CharField(max_length=32, blank=True, null=True, unique=True, verbose_name='参考编号')
    cp_rlk = models.CharField(max_length=32, blank=True, null=True)
    customer = models.ForeignKey(to='root_db.AccountedCompany', blank=True, null=True, on_delete=models.CASCADE, verbose_name='客户')
    # customer_name = models.CharField(max_length=64, blank=True, null=True, verbose_name='客户名称')
    staff = models.ForeignKey('root_db.Staff', blank=True, null=True, on_delete=models.PROTECT, verbose_name='客户经理')
    reply_date = models.DateField(blank=True, null=True, verbose_name='批复日')
    reply_code = models.CharField(max_length=32, blank=True, null=True, verbose_name='批复号')
    reply_content = models.TextField(blank=True, null=True, verbose_name='批复内容')
    expire_date = models.DateField(blank=True, null=True, verbose_name='授信到期日')
    is_special = models.BooleanField(default=False, verbose_name='特别授信')
    is_approved = models.BooleanField(default=False, verbose_name='已批准')
    previous = models.ForeignKey('self', blank=True, null=True, on_delete=models.PROTECT, verbose_name='前授信')
    cp_type = models.CharField(max_length=8, choices=cp_type_choice, blank=True, null=True, verbose_name='类型')
    # apply_amount = models.DecimalField(default=0, max_digits=12, decimal_places=2, verbose_name='申报金额')
    # reply_amount = models.DecimalField(default=0, max_digits=12, decimal_places=2, verbose_name='批复金额')
    # baozheng = models.DecimalField(default=0, max_digits=12, decimal_places=2, verbose_name='保证担保')
    # diya = models.DecimalField(default=0, max_digits=12, decimal_places=2, verbose_name='抵押担保')
    # zhiya = models.DecimalField(default=0, max_digits=12, decimal_places=2, verbose_name='质押担保')
    # is_auto_added = models.BooleanField(default=False, verbose_name='是否自动生成')
    # is_virtual = models.BooleanField(default=False, verbose_name='虚拟')      # 针对未建档，甚至客户都不存在的业务
    remark = models.TextField(blank=True, null=True, verbose_name='备注')

    class Meta:
        verbose_name = '授信台账'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.cp_num

    def as_dcms_work_flow(self, dcms=None):
        return CpWorkFlow(cp_num=self.cp_num, rlk=self.cp_rlk, dcms=dcms)

    @classmethod
    def createCpFromCrp(cls, reply_date__gte=None):
        crp = CrpHttpRequest()
        crp.login()
        dcms = DcmsHttpRequest()
        dcms.login()
        imp_date = DateOperation()
        last_add = imp_date.neighbour_date_date_str(cls, imp_date.today_str, 'add_date') or imp_date.delta_date(-1)
        reply_date__gte = reply_date__gte or last_add
        cp = crp.getCp(
            *['客户名称', '客户编号', '授信参考编号', '批复时间', '批复编号', '授信到期时间', '建档人', '是否特别授信', '批复结论'],
            **{
                '申报金额（原币）': crp.NumCondition.between(1, 10000000000),
                '批复时间': crp.DateCondition.between(reply_date__gte, imp_date.today_str),
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
                is_special = row_data['是否特别授信'].upper() == 'Y'
                is_approved = '批准' in row_data['批复结论']
                cp_rlk = dcms.search_cp(cp_num)
                customer = AccountedCompany.pickCustomer(customer_name, customer_code, dcms)
                expire_date = row_data['授信到期时间']
                if not expire_date:
                    expire_date = imp_date.delta_date(365, row_data['批复时间'])
                data_dict = {
                    'customer': customer,
                    'reply_date': reply_date,
                    'reply_code': reply_code,
                    'expire_date': expire_date,
                    'cp_rlk': cp_rlk,
                    'is_special': is_special,
                    'is_approved': is_approved,
                    'cp_type': 'CP',
                }
                if not cls.objects.filter(cp_num=cp_num).exists():
                    data_dict['staff'] = Staff.pickStaffByName(row_data['建档人'])
                    data_dict['cp_num'] = cp_num
                    cls(**data_dict).save()
                else:
                    staff_name = row_data['建档人']
                    obj = cls.objects.filter(cp_num=cp_num)
                    if obj[0].staff.name != staff_name:
                        data_dict['staff'] = Staff.pickStaffByName(row_data['建档人'])
                    obj.update(**data_dict)

    @classmethod
    def createSmeCpFromCrp(cls, reply_date__gte=None):
        crp = CrpHttpRequest()
        crp.login()
        dcms = DcmsHttpRequest()
        dcms.login(dcms_type=dcms.DcmsType.sme.value)
        imp_date = DateOperation()
        last_add = imp_date.neighbour_date_date_str(cls, imp_date.today_str, 'add_date') or imp_date.delta_date(-1)
        reply_date__gte = reply_date__gte or last_add
        cp = crp.getSmeCp(
            *['客户名称', '客户编号', '授信参考编号', '批复时间', '批复编号', '授信到期时间', '是否特别授信', '建档人', '批复结论'],
            **{
                '批复时间': crp.DateCondition.between(reply_date__gte, imp_date.today_str),
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
                is_special = 'Y' in row_data['是否特别授信'].upper()
                is_approved = '批准' in row_data['批复结论']
                cp_rlk = dcms.search_cp(cp_num)
                customer = AccountedCompany.pickCustomer(customer_name, customer_code, dcms)
                expire_date = row_data['授信到期时间']
                if not expire_date:
                    expire_date = imp_date.delta_date(365, row_data['批复时间'])
                data_dict = {
                    'customer': customer,
                    'reply_date': reply_date,
                    'reply_code': reply_code,
                    'expire_date': expire_date,
                    'cp_rlk': cp_rlk,
                    'is_special': is_special,
                    'is_approved': is_approved,
                    'cp_type': 'SME',
                }
                if not cls.objects.filter(cp_num=cp_num).exists():
                    data_dict['staff'] = Staff.pickStaffByDcmsName(row_data['建档人'])
                    data_dict['cp_num'] = cp_num
                    cls(**data_dict).save()
                else:
                    staff_name = row_data['建档人']
                    obj = cls.objects.filter(cp_num=cp_num)
                    if obj[0].staff is None or obj[0].staff.name != staff_name:
                        staff = Staff.pickStaffByDcmsName(row_data['建档人'])
                        data_dict['staff'] = staff
                    obj.update(**data_dict)

    @classmethod
    def createCsCpFromCrp(cls, reply_date__gte=None):
        crp = CrpHttpRequest()
        crp.login()
        dcms = DcmsHttpRequest()
        dcms.login(dcms_type=dcms.DcmsType.cs.value)
        imp_date = DateOperation()
        last_add = imp_date.neighbour_date_date_str(cls, imp_date.today_str, 'add_date') or imp_date.delta_date(-1)
        reply_date__gte = reply_date__gte or last_add
        cp = crp.getCsCp(
            *['客户名称', '客户编号', '授信编号', '批复时间', '批复编号', '授信到期时间', '客户经理', '批复结论'],
            **{
                '授信额度(元)': crp.NumCondition.gt(0),
                '批复时间': crp.DateCondition.between(reply_date__gte, imp_date.today_str),
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
                is_approved = '批准' in row_data['批复结论']
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
                        is_special=is_special,
                        is_approved=is_approved,
                        cp_type='CS',
                    ).save()
                else:
                    obj = cls.objects.filter(cp_num=cp_num)
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
        if dcms is None:
            dcms = DcmsHttpRequest()
            dcms.login()
        no_reply = CpLedger.objects.filter(
            Q(reply_content__isnull=True) &
            (
                Q(cp_num__startswith='SME') |
                Q(cp_num__startswith='CP')
            )
        ).values(
            'pk',
            'cp_num',
            'customer__name',
        )
        count = no_reply.count()
        i = 0
        for nr in no_reply:
            i += 1
            print(i, '/', count, nr['customer__name'], nr['cp_num'])
            reply_code, reply_content = CpLedger.objects.get(pk=nr['pk']).as_dcms_work_flow(dcms).getReply()
            CpLedger.objects.filter(pk=nr['pk']).update(
                reply_code=reply_code,
                reply_content=reply_content
            )


class LuLedger(models.Model):
    pay_method_choices = (
        (1, '受托'),
        (2, '自主'),
    )
    currency_type_choices = (
        ('CNY', '人民币'),
        ('USD', '美元'),
        ('OTHER', '其他'),
    )
    add_date = models.DateTimeField(auto_now_add=True, verbose_name='创建于')
    update_date = models.DateField(auto_now=True, verbose_name='更新日')
    # loan_demand = models.ForeignKey(to='deposit_and_credit.LoanDemand', blank=True, null=True, on_delete=models.PROTECT, verbose_name='规模安排')
    lu_num = models.CharField(max_length=32, primary_key=True, verbose_name='放款参考编号')
    is_green = models.NullBooleanField(blank=True, null=True, verbose_name='绿色金融')
    pay_method = models.IntegerField(choices=pay_method_choices, default=1, verbose_name='支付方式')
    is_xvbao = models.NullBooleanField(blank=True, null=True, verbose_name='续保标志')
    has_separation_of_duty = models.NullBooleanField(blank=True, null=True, verbose_name='信贷责任划分状（有/无）')
    has_sign_receipted = models.NullBooleanField(blank=True, null=True, verbose_name='送达签收单合同（有/无）')
    policy_expire = models.DateField(blank=True, null=True, verbose_name='保单到期日')
    has_used_relending_money = models.NullBooleanField(blank=True, null=True, verbose_name='是否转贷资金')
    inspector = models.ForeignKey(to='root_db.Staff', blank=True, null=True, related_name='inspector', on_delete=models.PROTECT, verbose_name='审查人员')
    cp = models.ForeignKey(to='CpLedger', blank=True, null=True, on_delete=models.CASCADE, verbose_name='授信')
    department = models.ForeignKey(to='root_db.Department', blank=True, null=True, on_delete=models.PROTECT, verbose_name='经营部门')
    staff = models.ForeignKey(to='root_db.Staff', blank=True, null=True, on_delete=models.PROTECT, verbose_name='客户经理')
    customer = models.ForeignKey(to='root_db.AccountedCompany', blank=True, null=True, on_delete=models.PROTECT, verbose_name='客户名称')
    dcms_business = models.ForeignKey(to='DcmsBusiness', blank=True, null=True, on_delete=models.PROTECT, verbose_name='业务种类')
    lend_date = models.DateField(blank=True, null=True, verbose_name='发放日期')
    plan_expire = models.DateField(blank=True, null=True, verbose_name='计划到期日')
    month_dif = models.IntegerField(default=0, verbose_name='期限(月)')
    currency_type = models.CharField(max_length=8, default='CNY', choices=currency_type_choices, verbose_name='业务币种')
    lend_amount = models.FloatField(default=0, verbose_name='发放金额（元）')
    rate = models.FloatField(default=0, verbose_name='利率或费率%')
    pledge_ratio = models.FloatField(default=0, verbose_name='保证金或质押担保比例%')
    float_ratio = models.FloatField(blank=True, null=True, verbose_name='浮动比例%')
    net_amount = models.FloatField(default=0, verbose_name='敞口金额')
    has_baozheng = models.BooleanField(default=False, verbose_name='保证')
    has_diya = models.BooleanField(default=False, verbose_name='抵押')
    has_zhiya = models.BooleanField(default=False, verbose_name='质押')
    contract_code = models.CharField(max_length=32, unique=True, blank=True, null=True, verbose_name='信贷合同编号')
    current_amount = models.FloatField(default=0, verbose_name='当前地区余额（含特别授信）')
    loan_demand = models.ManyToManyField(to='deposit_and_credit.LoanDemand', blank=True, verbose_name='贷款需求')
    is_inspected = models.BooleanField(default=False, verbose_name='已发放')
    rlk = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        verbose_name = '放款台账'
        verbose_name_plural = verbose_name
        ordering = ('-add_date', )

    def __str__(self):
        return self.lu_num

    def _vf_reply_content(self):
        try:
            return self.cp.reply_content
        except ValueError:
            return 'Null'
    _vf_reply_content.short_description = '批复内容'

    def _vf_reply_code(self):
        try:
            return self.cp.reply_code
        except ValueError:
            return 'Null'
    _vf_reply_code.short_description = '批复编号'

    def _vf_inspector_name(self):
        try:
            return self.inspector.name
        except ValueError:
            return 'Null'
    _vf_inspector_name.short_description = '审查人员'

    @classmethod
    def _updateCurrentAmountByDailyLeiShou(cls):
        '''
        上一步：爬取最近累收数据
        :return:
        '''
        print('累收数据爬取完毕，准备更新放款台账余额……')
        imp_date = DateOperation()
        new_retract = DailyLeiShou.objects.filter(
            add_date=imp_date.today_str,
            dcms_business__caption__contains='贷',
        ).exclude(
            contract_code__startswith='CZZX'
        )
        new_retract_values = new_retract.values(
            'contract_code',
            'customer__name'
        ).annotate(
            Sum('retract_amount')
        )
        not_found = []
        for nr in new_retract_values:
            customer_name = nr['customer__name']
            contract_code = nr['contract_code']
            retract_amount = nr['retract_amount__sum']
            try:
                lu = LuLedger.objects.get(contract_code=contract_code)
                new_amount = lu.current_amount - retract_amount
                if new_amount >= 0:
                    lu.current_amount = new_amount
                    lu.save(update_fields=['current_amount'])
                    print('已更新', customer_name, contract_code, '余额')
                else:
                    print(customer_name, contract_code, '用信余额已小于零，请核实')
                    input('>>>')
            except:
                not_found.append(
                    (customer_name, contract_code)
                )
        if not_found:
            print('以下回收数据未找到与之对应的放款记录：')
            for i in range(len(not_found)):
                print(i, '.', not_found[i])

    @classmethod
    def fillCpSmeDetail(cls, lu_num=None):
        from root_db.models import Department, Staff
        from deposit_and_credit.models import LoanDemand
        from MySite.utilities import field_choices_to_dict
        dept_sr = {'分行营业部': '营业部'}
        imp_date = DateOperation()
        currency_type_choices = field_choices_to_dict(cls.currency_type_choices)
        if lu_num:
            uncompleted = cls.objects.filter(
                lu_num=lu_num
            ).values(
                'lu_num'
            ).distinct()
        else:
            pass
            uncompleted = cls.objects.filter(
                Q(add_date__lt=imp_date.today_str) &
                Q(contract_code__isnull=True) &
                (
                    Q(lu_num__startswith='LU') |
                    Q(lu_num__startswith='SMELU')
                )
            ).values(
                'lu_num',
            ).distinct()
        if uncompleted.exists():
            crp = CrpHttpRequest()
            crp.login()
            dcms = DcmsHttpRequest()
            dcms.login()
            for uc in uncompleted:
                lu_num = uc['lu_num']
                lu_flow_base_info_page = cls.objects.get(lu_num=lu_num).as_dcms_work_flow(dcms).apply_info()
                page_areas = lu_flow_base_info_page.areas
                lu_flow_base_info = page_areas['申请明细'].parse()
                lu_flow_info_fee = page_areas['业务费'].parse()
                qidai = crp.getQiDaiLu(
                    *[
                        '授信参考编号', '经办行', '管户客户经理', '客户编号', '业务种类',
                        '发放日期', '业务到期日', '业务币种', '放款金额(元)', '利率',
                        '费率(百分比)', '保证金比例', '利率浮动比例', '利率调整频率',
                        '担保方式', '合同号', '客户名称', '放款参考编号'
                    ],
                    **{
                        '放款参考编号': crp.CharCondition.equal(lu_num)
                    }
                )
                for page in qidai:
                    page_data = crp.parseQueryResultToDictList(page)
                    for row_data in page_data:
                        data_dict = {}
                        if '保证' in row_data['担保方式']:
                            data_dict['has_baozheng'] = True
                        if '抵押' in row_data['担保方式']:
                            data_dict['has_diya'] = True
                        if '质押' in row_data['担保方式']:
                            data_dict['has_zhiya'] = True
                        lu = cls.objects.get(lu_num=lu_num)
                        if lu.contract_code is None:
                            customer_name = row_data['客户名称']
                            customer_code = row_data['客户编号']
                            staff = Staff.pickStaffByName(row_data['管户客户经理'])
                            customer = AccountedCompany.pickCustomer(customer_name, customer_code, dcms)
                            department = dept_sr.get(row_data['经办行'].split('-')[1]) or row_data['经办行'].split('-')[1]
                            data_dict['rlk'] = dcms.search_lu(lu_num)
                            cp_num = row_data['授信参考编号']
                            cp_num = cp_num if cp_num.startswith('CP') or cp_num.startswith('SME') else lu_flow_base_info['对应的授信申请'][0].inner_text
                            data_dict['cp'] = CpLedger.objects.get(cp_num=cp_num)
                            data_dict['contract_code'] = row_data['合同号']
                            data_dict['department'] = Department.pickObjByCaption(department)
                            data_dict['staff'] = staff
                            data_dict['customer'] = customer
                            data_dict['dcms_business'] = DcmsBusiness.pickObjectByCaption(row_data['业务种类'])
                            data_dict['lend_date'] = row_data['发放日期']
                            data_dict['plan_expire'] = row_data['业务到期日']
                            data_dict['month_dif'] = imp_date.month_count(row_data['业务到期日'], row_data['发放日期'])
                            data_dict['currency_type'] = currency_type_choices.get(row_data['业务币种'].strip(), 'OTHER')
                            data_dict['lend_amount'] = crp.strToNum(row_data['放款金额(元)'])
                            data_dict['rate'] = crp.strToNum(row_data['利率']) or crp.strToNum(row_data['费率(百分比)']) or crp.strToNum(lu_flow_info_fee[0]['费率'].inner_text) * 100
                            data_dict['pledge_ratio'] = crp.strToNum(row_data['保证金比例'])
                            data_dict['float_ratio'] = crp.strToNum(row_data['利率浮动比例']) if '固定' not in row_data['利率调整频率'] and '贷' in row_data['业务种类'] else None
                            data_dict['net_amount'] = (100 - crp.strToNum(row_data['保证金比例'])) * crp.strToNum(row_data['放款金额(元)']) / 100
                            data_dict['current_amount'] = data_dict['lend_amount']
                            data_dict['is_inspected'] = True
                        else:
                            data_dict['lend_amount'] = lu.lend_amount + crp.strToNum(row_data['放款金额(元)'])
                        cls.objects.filter(lu_num=row_data['放款参考编号']).update(**data_dict)
                        # todo:↓扣除项目储备的剩余敞口
        # return uncompleted

    @classmethod
    def fillCsDetail(cls):
        from root_db.models import Department, Staff
        from MySite.utilities import field_choices_to_dict
        dept_sr = {'分行营业部': '营业部'}
        imp_date = DateOperation()
        currency_type_choices = field_choices_to_dict(cls.currency_type_choices)
        uncompleted = cls.objects.filter(
            Q(add_date__lt=imp_date.today_str) &
            Q(contract_code__isnull=True) &(
                Q(lu_num__startswith='CSLU') |
                Q(lu_num__startswith='SMELU')
            )
        ).values(
            'lu_num',
        ).distinct()
        if uncompleted.exists():
            crp = CrpHttpRequest()
            crp.login()
            dcms = DcmsHttpRequest()
            dcms.login()
            dcms.setDcmsType(dcms.DcmsType.cs.value)
            for uc in uncompleted:
                lu_num = uc['lu_num']
                lu_flow_base_info_page = cls.objects.get(lu_num=lu_num).as_dcms_work_flow(dcms).apply_info()
                page_areas = lu_flow_base_info_page.areas
                apply_detail = page_areas['申请明细'].parse()
                customer_name = apply_detail['申请人名称'][0].inner_text
                if len(customer_name) > 4:
                    continue
                edu_detail = page_areas['额度使用明细'].parse()
                contract_code = edu_detail['合同编号'][0].inner_text
                gedai = crp.getGeDaiLu(
                    *[
                        '授信参考编号', '经办行', '管户客户经理', '客户编号', '业务名称',
                        '业务开始时间(发放日)', '业务到期日', '币种', '发放金额', '利率',
                        '利率浮动比例', '利息调整频率',
                        '担保方式', '合同号', '客户名称'
                    ],
                    **{
                        '合同号': crp.CharCondition.equal(contract_code),
                    }
                )
                for page in gedai:
                    page_data = crp.parseQueryResultToDictList(page)
                    for row_data in page_data:
                        data_dict = {}
                        if '保证' in row_data['担保方式']:
                            data_dict['has_baozheng'] = True
                        if '抵押' in row_data['担保方式']:
                            data_dict['has_diya'] = True
                        if '质押' in row_data['担保方式']:
                            data_dict['has_zhiya'] = True
                        lu = cls.objects.get(lu_num=lu_num)
                        if lu.contract_code is None:
                            customer_name = row_data['客户名称']
                            customer_code = row_data['客户编号']
                            department = dept_sr.get(row_data['经办行'].split('-')[1]) or row_data['经办行'].split('-')[1]
                            data_dict['rlk'] = dcms.search_lu(lu_num)
                            cp_num = row_data['授信参考编号'] if row_data['授信参考编号'].strip() else apply_detail['对应的授信申请'][0].inner_text
                            data_dict['cp'] = CpLedger.objects.get(cp_num=cp_num)
                            data_dict['contract_code'] = contract_code
                            data_dict['department'] = Department.pickObjByCaption(department)
                            data_dict['staff'] = Staff.pickStaffByName(row_data['管户客户经理'])
                            data_dict['customer'] = AccountedCompany.pickCustomer(customer_name, customer_code, dcms)
                            data_dict['dcms_business'] = DcmsBusiness.pickObjectByCaption(row_data['业务名称'])
                            data_dict['lend_date'] = row_data['业务开始时间(发放日)']
                            data_dict['plan_expire'] = row_data['业务到期日']
                            data_dict['month_dif'] = imp_date.month_count(data_dict['plan_expire'], data_dict['lend_date'])
                            data_dict['currency_type'] = currency_type_choices.get(row_data['币种'].strip(), 'OTHER')
                            data_dict['lend_amount'] = crp.strToNum(row_data['发放金额'])
                            data_dict['rate'] = crp.strToNum(row_data['利率'])
                            data_dict['pledge_ratio'] = crp.strToNum(edu_detail['保证金比例%'][0].inner_text)
                            data_dict['float_ratio'] = crp.strToNum(row_data['利率浮动比例']) if '固定利率' not in row_data['利息调整频率'] else None
                            data_dict['net_amount'] = (100 - data_dict['pledge_ratio']) * data_dict['lend_amount'] / 100
                            data_dict['current_amount'] = data_dict['lend_amount']
                            data_dict['is_inspected'] = True
                        else:
                            data_dict['lend_amount'] = crp.strToNum(row_data['发放金额']) + lu.lend_amount
                        cls.objects.filter(lu_num=lu_num).update(**data_dict)

    @classmethod
    def getSingleLuDetailFromDcms(cls, lu_num, dcms):
        work_flow = LuWorkFlow(lu_num=lu_num, dcms=dcms)
        currency_type_dict = field_choices_to_dict(cls.currency_type_choices)
        ret = {}
        if lu_num.startswith('LU'):
            dcms.setDcmsType(dcms.DcmsType.cp.value)
        elif lu_num.startswith('SMELU'):
            dcms.setDcmsType(dcms.DcmsType.sme.value)
        elif lu_num.startswith('CSLU'):
            dcms.setDcmsType(dcms.DcmsType.cs.value)
        apply_info_areas = work_flow.apply_info().areas
        apply_detail = apply_info_areas['申请明细'].parse()
        customer_rlk = RegExp.rlk.search(str(apply_detail['申请人名称'][0])).groups()[0]
        try:
            ret['customer'] = AccountedCompany.objects.get(rlk_customer=customer_rlk)
        except:
            customer_name = apply_detail['申请人名称'][0].inner_text
            ret['customer'] = AccountedCompany.objects.get(name=customer_name)
        dept_code = apply_detail['入帐经办行'][0].inner_text.split(' - ')[0]
        ret['department'] = Department.pickObjectByDcmsOrgCode(dept_code)
        cp_num = apply_detail['对应的授信申请'][0].inner_text
        try:
            ret['cp'] = CpLedger.objects.get(cp_num=cp_num)
        except:
            pass
        edu_detail = apply_info_areas['额度使用明细'].parse()
        dcms_business_caption = edu_detail['业务'][0].inner_text.split(' - ')[1]
        ret['dcms_business'] = DcmsBusiness.pickObjectByCaption(dcms_business_caption)
        ret['currency_type'] = currency_type_dict.get(edu_detail['币种'][0].inner_text.split(' - ')[1], 'OTHER')
        # ret['contract_code'] = edu_detail['合同编号'][0].inner_text
        ret['lend_amount'] = CrpHttpRequest.strToNum(edu_detail['本次发放占用授信金额'][0].inner_text)
        try:
            ret['pledge_ratio'] = CrpHttpRequest.strToNum(edu_detail['特别授信类担保品比例%(授信层)'][0].inner_text)
        except:
            ret['pledge_ratio'] = CrpHttpRequest.strToNum(edu_detail['保证金比例%'][0].inner_text)
        ret['net_amount'] = ret['lend_amount'] * (100 - ret['pledge_ratio']) / 100
        return ret

    def as_dcms_work_flow(self, dcms=None):
        return LuWorkFlow(lu_num=self.lu_num, rlk=self.rlk, dcms=dcms)

    @classmethod
    def bulkUpdateAmountByQiDai(cls):
        '''
        爬取企贷表，批量更新地区、小微企业的用信余额
        :return:
        '''
        crp = CrpHttpRequest()
        crp.login()
        pass


class DailyLeiShou(models.Model):
    '''
    数据来源：企贷自定义明细-当月累收
    '''
    add_date = models.DateField(auto_now_add=True)
    customer = models.ForeignKey('root_db.AccountedCompany', blank=True, null=True, on_delete=models.PROTECT, verbose_name='客户')
    contract_code = models.CharField(max_length=32, blank=True, null=True, verbose_name='信贷合同编号')
    retract_amount = models.FloatField(default=0, verbose_name='收回金额（人民币，元）')
    retract_date = models.DateField(blank=True, null=True, verbose_name='收回日期')
    dcms_business = models.ForeignKey('DcmsBusiness', blank=True, null=True, on_delete=models.PROTECT, verbose_name='业务种类')
    lu = models.ForeignKey('LuLedger', blank=True, null=True, on_delete=models.PROTECT, verbose_name='放款')
    cp = models.ForeignKey('CpLedger', blank=True, null=True, on_delete=models.PROTECT, verbose_name='授信')

    class Meta:
        verbose_name = '回收'
        verbose_name_plural = verbose_name

    @classmethod
    def getDailyLeishou(cls, retract_date__gte=None):
        from deposit_and_credit.models import LoanDemand
        imp_date = DateOperation()
        crp = CrpHttpRequest()
        crp.login()
        retract_date__gte = retract_date__gte or str(imp_date.delta_date(1, imp_date.last_data_date_str(DailyLeiShou, 'retract_date')))
        leishou = crp.getLeiShou(
            *('合同号', '客户名称', '客户编号', '收回日期', '收回金额(元)', '业务种类', '汇率'),
            **{
                '收回日期': crp.DateCondition.between(retract_date__gte, imp_date.today_str)
            }
        )
        total_retract_loan = 0
        data_for_bulk_create = []
        for page in leishou:
            page_data = crp.parseQueryResultToDictList(page)
            for i in range(len(page_data)):
                row_data = page_data[i]
                customer_name = row_data['客户名称']
                customer_code = row_data['客户编号']
                exchange_rate = crp.strToNum(row_data['汇率'], 100) / 100
                retract_amount = exchange_rate * crp.strToNum(row_data['收回金额(元)'].strip()) / 10000
                customer = AccountedCompany.pickCustomer(row_data['客户名称'], customer_code)
                dcms_business = DcmsBusiness.pickObjectByCaption(row_data['业务种类'].strip())
                contract_code = row_data['合同号'].strip()
                lu = None
                cp = None
                try:
                    lu = LuLedger.objects.get(contract_code=contract_code)
                except:
                    pass
                else:
                    try:
                        cp = lu.cp
                    except:
                        pass
                retract_date = row_data['收回日期'].strip()
                print(retract_date, '收回', customer_name, contract_code, row_data['业务种类'], '折合人民币', retract_amount)
                if '贷' in row_data['业务种类']:
                    total_retract_loan += retract_amount
                data_for_bulk_create.append(
                    cls(
                        contract_code=contract_code,
                        retract_date=retract_date,
                        retract_amount=retract_amount,
                        dcms_business=dcms_business,
                        customer=customer,
                        lu=lu,
                        cp=cp,
                    )
                )
        print(retract_date__gte, '（含）至', imp_date.today_str, '（不含），收回贷款折合人民币', total_retract_loan, '万元')
        if data_for_bulk_create:
            cls.objects.bulk_create(data_for_bulk_create)
            LuLedger._updateCurrentAmountByDailyLeiShou()
        else:
            print('无需更新放款台账余额')
            print('无需更新贷款需求')

