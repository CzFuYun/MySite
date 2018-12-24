from django.db import models
from django.db.models import Q

from deposit_and_credit import models_operation
from MySite import utilities


class Staff(models.Model):
    position_choices = (
        (1, '支行员工'),
        (2, '支行负责人'),
        (3, '分行'),
    )
    staff_id = models.CharField(max_length=8, primary_key=True, verbose_name='工号')
    name = models.CharField(blank=True, null=True, max_length=16, verbose_name='姓名')
    staff_level = models.SmallIntegerField(blank=True, null=True, verbose_name='行员等级')
    sub_department = models.ForeignKey(to='SubDepartment', to_field='sd_code', on_delete=models.CASCADE, verbose_name='部门（细分）')     # 细分部门，例如溧阳大客户部应记作LY_2
    phone_number = models.CharField(max_length=16, null=True, blank=True)
    cellphone_number = models.CharField(max_length=16, null=True, blank=True)
    oa = models.CharField(max_length=8, null=True, blank=True)
    yellow_red_card = models.IntegerField(default=0, verbose_name='授信到期黄红牌')
    red_card_expire_date = models.DateField(blank=True, null=True, verbose_name='红牌到期日')

    class Meta:
        # unique_together = ['sub_department', 'name']
        verbose_name = '员工'
        verbose_name_plural = verbose_name
        # ordering = 'sub_department'

    def __str__(self):
        return self.sub_department.caption + self.name       # '{department}—{name}'.format(name=self.name, department=self.sub_department.caption)

    @classmethod
    def bulkUpdate(cls, workbook_name):
        from root_db.models_operation import getSimpleSerializationRule, getXlDataForOrmOperation
        # 先清除到期红牌
        cls.objects.filter(yellow_red_card__gt=1, red_card_expire_date__lte=models_operation.DateOperation().today).update(
            red_card_expire_date=None, yellow_red_card=0
        )
        all_sr_dict = {}
        all_sr_dict['sub_department_id'] = getSimpleSerializationRule(SubDepartment, 'sd_code', 'caption')
        data_source_list = getXlDataForOrmOperation(workbook_name, 'Sheet1')
        data_for_bulk_create = []
        for data_dict in data_source_list:
            for field in data_dict:
                field_sr = all_sr_dict.get(field)
                if field_sr:
                    value_before_serialize = data_dict[field]
                    data_dict[field] = field_sr[value_before_serialize]
            data_for_bulk_create.append(cls(**data_dict))
        cls.objects.bulk_create(data_for_bulk_create)

    def setYellowRedCard(self):
        # 计算红黄牌，yellow_red_card  =0，未被警告；  =1，黄牌；  >1，红牌
        yellow_red_card = self.yellow_red_card
        self.yellow_red_card = yellow_red_card + 1
        if yellow_red_card:     # 之前已经是黄牌或红牌
            self.red_card_expire_date = models_operation.DateOperation().delta_date(90)
        self.save()

    def resetRedCard(self):
        # 禁赛3个月后设置为0
        self.red_card_expire_date = None
        self.yellow_red_card = 0
        self.save()

    @classmethod
    def bulkResetRedCard(cls):
        imp_date = models_operation.DateOperation()
        cls.objects.filter(red_card_expire_date__gte='')

    @classmethod
    def getBusinessDeptStaff(cls, dept_code='', name_contains='', return_mode=utilities.return_as['choice']):
        dept_q = Q(sub_department__superior__code=dept_code) if dept_code else ~Q(sub_department__superior__code__in=['NONE', 'JGBS'])
        name_q = Q(name__contains=name_contains) if name_contains else Q(name__isnull=False)
        staff_qs = Staff.objects.filter(dept_q & name_q).order_by(
                'sub_department__superior__display_order').values('staff_id', 'sub_department__superior__caption', 'name')
        if return_mode == utilities.return_as['choice']:
            ret = []
            for s in staff_qs:
                if len(s['name']) > 4:
                    continue
                ret.append((s['staff_id'], s['sub_department__superior__caption'] + '  ' + s['name']))
            return ret
        elif return_mode == utilities.return_as['list']:
            ret = []
            for s in staff_qs:
                if len(s['name']) > 4:
                    continue
                ret.append(s['sub_department__superior__caption'] + '  ' + s['name'] + '  ' + s['staff_id'])
            return ret
########################################################################################################################
class Department(models.Model):
    code = models.CharField(primary_key=True, max_length=8, unique=True, verbose_name='部门编号')
    caption = models.CharField(max_length=32, unique=True, verbose_name='部门名称')
    display_order = models.SmallIntegerField(unique=True, verbose_name='排序先后')      # 连续不可间断，可按需更改，无耦合

    class Meta:
        verbose_name_plural = '部门（综合）'
        ordering = ('display_order', )

    def __str__(self):
        return self.caption



    @classmethod
    def getDepartments(cls, return_mode=utilities.return_as['choice']):
        dept = cls.objects.values('code', 'caption').order_by('display_order')
        if return_mode == utilities.return_as['choice']:
            l = []
            for d in dept:
                l.append((d['code'], d['caption']))
            return l
        elif return_mode == utilities.return_as['dict']:
            dic = {}
            for d in dept:
                dic[d['code']] = d['caption']
            return dic

    @classmethod
    def getDeptChoices(cls):
        pass

    @classmethod
    def getBusinessDept(cls, return_mode=utilities.return_as['choice']):
        dept = cls.objects.exclude(code__in=['JGBS' , 'NONE']).values('code', 'caption').order_by('display_order')
        if return_mode == utilities.return_as['choice']:
            l = []
            for d in dept:
                l.append((d['code'], d['caption']))
            return l
        elif return_mode == utilities.return_as['dict']:
            dic = {}
            for d in dept:
                dic[d['code']] = d['caption']
            return dic
########################################################################################################################
class SubDepartment(models.Model):
    sd_code = models.CharField(primary_key=True, max_length=8, verbose_name='部门编号')
    caption = models.CharField(max_length=32, unique=True, verbose_name='部门名称')
    superior = models.ForeignKey('Department', to_field='code', on_delete=models.CASCADE, verbose_name='所属部门')

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = '部门（细分）'
########################################################################################################################


class AccountedCompany(models.Model):
    customer_id = models.CharField(primary_key=True, max_length=32, verbose_name='客户号')
    name = models.CharField(max_length=128, verbose_name='账户名称')
    district = models.ForeignKey('District', default=1, on_delete=models.CASCADE, verbose_name='区域')
    customer_type = models.ForeignKey('CustomerType', default=1, on_delete=models.CASCADE, verbose_name='客户类别')
    scale = models.ForeignKey('Scale', default=1, on_delete=models.CASCADE, verbose_name='规模')
    industry = models.ForeignKey('Industry', to_field='code', default=1, on_delete=models.CASCADE, verbose_name='行业门类')
    series = models.ForeignKey('Series', to_field='code', default='NONE', null=True, blank=True, on_delete=models.CASCADE, verbose_name='企业系列')
    type_of_3311 = models.ForeignKey('TypeOf3311', default=1,  on_delete=models.CASCADE, verbose_name='3311类型')
    has_base_acc = models.BooleanField(default=False, verbose_name='是否基本户')
    has_credit = models.BooleanField(default=False, verbose_name='是否有贷户')
    sum_settle = models.IntegerField(default=0, verbose_name='累计结算量')
    inter_settle = models.IntegerField(default=0, verbose_name='国际结算量')

    def __str__(self):
        try:
            return self.name
        except:
            return 'None'

    class Meta:
        verbose_name_plural = '已开户对公客户'

    @classmethod
    def matchAccountByName(cls, name, return_mode=utilities.return_as['choice']):
        c_qs = cls.objects.filter(name__contains=name).values('name', 'customer_id')
        if return_mode == utilities.return_as['choice']:
            ret = []
            for c in c_qs:
                ret.append((c['customer_id'], c['name'] + '  ' + c['customer_id']))
            return ret
        elif return_mode == utilities.return_as['list']:
            ret = []
            for c in c_qs:
                ret.append(str(c['customer_id']) + '  ' + c['name'])
            return ret
        elif return_mode == utilities.return_as['dict']:
            ret = {}
            for c in c_qs:
                ret[c['customer_id']] = c['name']
            return ret
########################################################################################################################


class Series(models.Model):
    code = models.CharField(primary_key=True, max_length=8, verbose_name='代号')
    caption = models.CharField(max_length=32, unique=True, verbose_name='名称')
    gov_plat_lev = models.ForeignKey(to='GovernmentPlatformLevel', default=1, on_delete=models.CASCADE, verbose_name='平台级别')

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = '系列'
########################################################################################################################


class TypeOf3311(models.Model):
    caption = models.CharField(max_length=32)
    level = models.CharField(max_length=16, null=True ,blank=True)
    remark = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.caption + '（' + self.level + '）'

    class Meta:
        verbose_name_plural = '3311类型'

    @classmethod
    def get3311Type(cls, return_mode=utilities.return_as['choice']):
        qs = cls.objects.all().values()
        ret = []
        for q in qs:
            ret.append((q['id'], q['caption'] + '#' + q['level'] + (('（' + q['remark'] + '）') if q['remark'] else '')))
        return ret
########################################################################################################################


class Scale(models.Model):
    caption = models.CharField(max_length=16)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = '企业规模'
########################################################################################################################


class Industry(models.Model):
    code = models.CharField(max_length=8, primary_key=True, verbose_name='行业代码')
    caption = models.CharField(max_length=64)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = '行业门类'


########################################################################################################################
class CustomerType(models.Model):
    caption = models.CharField(max_length=16)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = '客户类别'


########################################################################################################################
class District(models.Model):
    caption = models.CharField(max_length=16)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = '区域'


########################################################################################################################
class GovernmentPlatformLevel(models.Model):
    caption = models.CharField(max_length=16)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = '平台级别'


########################################################################################################################
class DividedCompanyAccount(models.Model):
    '''
    单条分配数据
    '''
    customer = models.ForeignKey('AccountedCompany', on_delete=models.CASCADE, verbose_name='客户')
    account_id = models.CharField(max_length=64, verbose_name='账号')
    beneficiary = models.ForeignKey('Staff', on_delete=models.CASCADE, verbose_name='员工')
    department = models.ForeignKey('Department', to_field='code', on_delete=models.CASCADE, verbose_name='部门（综合）')
    sub_department = models.ForeignKey('SubDepartment', to_field='sd_code', on_delete=models.CASCADE, verbose_name='部门（细分）')
    deposit_type = models.ForeignKey(to='DepositType', on_delete=models.CASCADE, default=1, verbose_name='存款类型')
    rate_type = models.ForeignKey(to='RateType', on_delete=models.CASCADE, default=1, verbose_name='存款口径')
    rate = models.FloatField(default=0, verbose_name='利率（%）')
    transfer_price = models.FloatField(default=0, verbose_name='资金转移价（%）')
    rate_spread = models.FloatField(default=0, verbose_name='利差（%）')
    base_rate = models.FloatField(default=0, verbose_name='人行基准利率（%）')
    floating_ratio = models.FloatField(default=0, verbose_name='人行基准上浮比例（%）')
    acc_open_date = models.DateField(null=True, blank=True, auto_now_add=False, verbose_name='开户日期')
    start_date = models.DateField(null=True, blank=True, auto_now_add=False, verbose_name='起始日期')
    exp_date = models.DateField(null=True, blank=True, auto_now_add=False, verbose_name='到期日期')
    acc_status = models.ForeignKey(to='AccountStatus', default=1, on_delete=models.CASCADE, verbose_name='账户状态')
    data_date = models.DateField(auto_now_add=False, verbose_name='数据日期')
    divided_amount = models.IntegerField(default=0, verbose_name='分配余额（万元）')
    divided_md_avg = models.IntegerField(default=0, verbose_name='本月分配日均（万元）')
    divided_sd_avg = models.IntegerField(default=0, verbose_name='本季分配日均（万元）')
    divided_yd_avg = models.IntegerField(default=0, verbose_name='本年分配日均（万元）')

    def __str__(self):
        return self.customer.name

    class Meta:
        verbose_name_plural = '存款分配表'

########################################################################################################################
class DepositType(models.Model):
    caption = models.CharField(max_length=64)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = '存款类型'


########################################################################################################################
class RateType(models.Model):
    caption = models.CharField(max_length=64)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = '存款口径'


########################################################################################################################
class AccountStatus(models.Model):
    caption = models.CharField(max_length=32)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = '账户状态'


########################################################################################################################
class EconomicProperty(models.Model):
    caption = models.CharField(max_length=64)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = '企业经济性质'


########################################################################################################################
class CreditRate(models.Model):
    caption = models.CharField(max_length=16)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = '信用评级'


########################################################################################################################
class CreditProperty(models.Model):
    caption = models.CharField(max_length=32)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = '授信性质'


#######################################################################################################################
class CreditLedger(models.Model):
    credit_type_choices = (
        (1, '组合额度'),
        (2, '专项额度'),
    )
    approved_by_choices = (
        (1, '分行'),
        (2, '总行'),
    )
    data_date = models.DateField(auto_now_add=True, verbose_name='数据日期')
    department = models.ForeignKey('Department', to_field='code', default='NONE', on_delete=models.CASCADE, verbose_name='营销部门')
    staff = models.ForeignKey('Staff', default=1, on_delete=models.CASCADE, verbose_name='客户经理')
    customer = models.ForeignKey('AccountedCompany', on_delete=models.CASCADE, verbose_name='客户名称')
    economic_prop = models.ForeignKey('EconomicProperty', default=1, on_delete=models.CASCADE, verbose_name='经济性质')
    credit_type = models.SmallIntegerField(choices=credit_type_choices, default=1, verbose_name='授信种类')
    credit_rate = models.ForeignKey('CreditRate', default=1, on_delete=models.CASCADE, verbose_name='信用评级')
    apply_fanci = models.IntegerField(default=1, verbose_name='申报金额')
    approved_by = models.SmallIntegerField(default=1, verbose_name='审批行处')
    credit_prop = models.ForeignKey('CreditProperty', default=1, on_delete=models.CASCADE, verbose_name='授信性质')
    guar_type = models.CharField(max_length=32, verbose_name='担保方式')
    approved_date = models.DateField(blank=True, null=True, verbose_name='审批日期')
    exp_date = models.DateField(blank=True, null=True, verbose_name='授信到期日')
    specially_fanci = models.IntegerField(default=0, verbose_name='已批专项额度')
    combine_fanci = models.IntegerField(default=0, verbose_name='已批组合额度')
    combine_net_fanci = models.IntegerField(default=0, verbose_name='已批组合净额')
    loan_fanci = models.IntegerField(default=0, verbose_name='已批贷款额度')
    tangible_fanci_01 = models.IntegerField(default=0, verbose_name='已批经营性物业抵押贷款')
    tangible_fanci_02 = models.IntegerField(default=0, verbose_name='已批城镇化建设贷款')
    tangible_fanci_03 = models.IntegerField(default=0, verbose_name='已批基本建设贷款')
    tangible_fanci_04 = models.IntegerField(default=0, verbose_name='已批外币流动资金贷款')
    tangible_fanci_05 = models.IntegerField(default=0, verbose_name='已批流动资金贷款')
    tangible_fanci_06 = models.IntegerField(default=0, verbose_name='已批房地产开发贷款')
    tangible_fanci_07 = models.IntegerField(default=0, verbose_name='已批银行承兑汇票')
    tangible_fanci_08 = models.IntegerField(default=0, verbose_name='已批贸易融资授信')
    tangible_fanci_09 = models.IntegerField(default=0, verbose_name='已批保函授信')
    tangible_fanci_10 = models.IntegerField(default=0, verbose_name='已批商票')
    tangible_fanci_11 = models.IntegerField(default=0, verbose_name='已批票贷通承诺')
    tangible_fanci_12 = models.IntegerField(default=0, verbose_name='已批票贷通贷款')
    total_used = models.IntegerField(default=0, verbose_name='用信合计')
    loan_used = models.IntegerField(default=0, verbose_name='贷款用信')
    loan_avg = models.FloatField(default=0, verbose_name='贷款日均')
    rate_avg = models.FloatField(default=0, verbose_name='加权利率')
    used_tangible_fanci_01 = models.IntegerField(default=0, verbose_name='已用经营性物业抵押贷款')
    used_tangible_fanci_02 = models.IntegerField(default=0, verbose_name='已用城镇化建设贷款')
    used_tangible_fanci_03 = models.IntegerField(default=0, verbose_name='已用基本建设贷款')
    used_tangible_fanci_04 = models.IntegerField(default=0, verbose_name='已用外币流动资金贷款')
    used_tangible_fanci_05 = models.IntegerField(default=0, verbose_name='已用流动资金贷款')
    used_tangible_fanci_06 = models.IntegerField(default=0, verbose_name='已用房地产开发贷款')
    used_tangible_fanci_07 = models.IntegerField(default=0, verbose_name='已用银行承兑汇票')
    used_tangible_fanci_08 = models.IntegerField(default=0, verbose_name='已用贸易融资授信')
    used_tangible_fanci_09 = models.IntegerField(default=0, verbose_name='已用保函授信')
    used_tangible_fanci_10 = models.IntegerField(default=0, verbose_name='已用商票')
    used_tangible_fanci_11 = models.IntegerField(default=0, verbose_name='已用票贷通承诺')
    used_tangible_fanci_12 = models.IntegerField(default=0, verbose_name='已用票贷通贷款')
    invest_banking_amount = models.IntegerField(default=0, verbose_name='投行业务余额')
    invest_banking_remark = models.CharField(max_length=128, blank=True, null=True, verbose_name='投行业务备注')
    direct_financing = models.IntegerField(default=0, verbose_name='直接融资余额')
    direct_financing_remark = models.CharField(max_length=128, blank=True, null=True, verbose_name='直接融资备注')
    escrow_amount = models.IntegerField(default=0, verbose_name='资金监管金额')
    escrow_remark = models.CharField(max_length=128, blank=True, null=True, verbose_name='资金监管备注')
    approve_text = models.TextField(blank=True, null=True, verbose_name='批复内容')
    is_green_finance = models.BooleanField(default=False, verbose_name='是否绿色金融')
    credit_file = models.CharField(max_length=16, blank=True, null=True, verbose_name='信贷文件编号')
    cp_consult_num = models.CharField(max_length=32, blank=True, null=True, verbose_name='授信参考编号')

    def __str__(self):
        return self.customer.name

    class Meta:
        verbose_name_plural = '授信台账'


#######################################################################################################################
# class AccountedPerson(models.Model):
#     customer_id = models.CharField(primary_key=True, max_length=32, verbose_name='客户号')
#     name = models.CharField(max_length=128, verbose_name='账户名称')
#     origin = models.ForeignKey('AccountedCompany', to_field='customer_id', null=True, blank=True, on_delete=models.CASCADE, verbose_name='派生自')
#
#
# #######################################################################################################################
# class DividedPersonalAccount(models.Model):
#     customer = models.ForeignKey('AccountedPerson', on_delete=models.CASCADE, verbose_name='客户')
#     beneficiary = models.ForeignKey('Staff', null=True, blank=True, on_delete=models.CASCADE, verbose_name='员工')
#     rate_type = models.ForeignKey(to='RateType', on_delete=models.CASCADE, default=1, verbose_name='存款口径')
#     data_date = models.DateField(auto_now_add=False, null=True, blank=True, verbose_name='数据日期')
#     divided_amount = models.IntegerField(default=0, verbose_name='分配余额（万元）')
#     divided_md_avg = models.IntegerField(default=0, verbose_name='本月分配日均（万元）')
#     divided_sd_avg = models.IntegerField(default=0, verbose_name='本季分配日均（万元）')
#     divided_yd_avg = models.IntegerField(default=0, verbose_name='本年分配日均（万元）')




