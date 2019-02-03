# coding: utf-8
import re
from collections import defaultdict, namedtuple, OrderedDict

from django.db import models
from django.db.models import Q

# from root_db import models as m
from . import models_operation
from scraper.models import LuLedger, DcmsBusiness
from scraper.crp import CrpHttpRequest
# from apps.app_customer_repository import models as crm
from dcms_shovel import connection, dig


# class DepartmentDeposit(models.Model):
#     data_date = models.DateField(null=True, blank=True)
#     sub_department = models.ForeignKey(m.SubDepartment, to_field='sd_code', on_delete=models.CASCADE)
#     amount = models.BigIntegerField(default=0, verbose_name='余额（万元）')
#     md_avg = models.BigIntegerField(default=0, verbose_name='月日均（万元）')
#     sd_avg = models.BigIntegerField(default=0, verbose_name='季日均（万元）')
#     yd_avg = models.BigIntegerField(default=0, verbose_name='年日均（万元）')
#
#     class Meta:
#         unique_together = ('data_date', 'sub_department', )


########################################################################################################################
# class IndustryDeposit(models.Model):
#     data_date = models.DateField(null=True, blank=True)
#     industry = models.ForeignKey(m.Industry, to_field='code', default=1, on_delete=models.CASCADE)
#     amount = models.BigIntegerField(default=0, verbose_name='余额（万元）')
#     md_avg = models.BigIntegerField(default=0, verbose_name='月日均（万元）')
#     sd_avg = models.BigIntegerField(default=0, verbose_name='季日均（万元）')
#     yd_avg = models.BigIntegerField(default=0, verbose_name='年日均（万元）')
#
#     class Meta:
#         unique_together = ('data_date', 'industry', )


class Contributor(models.Model):
    approve_line_choices = (
        ('', '无贷'),
        ('地区', '地区'),
        ('小微', '小微'),
    )
    customer = models.ForeignKey('root_db.AccountedCompany', on_delete=models.CASCADE, verbose_name='客户')
    department = models.ForeignKey('root_db.Department', null=True, blank=True, on_delete=models.CASCADE, verbose_name='经营部门')
    approve_line = models.CharField(max_length=8, choices=approve_line_choices, default='', verbose_name='审批条线')
    staff = models.ForeignKey('root_db.Staff', null=True, blank=True, on_delete=models.CASCADE, verbose_name='客户经理')
    loan_rate = models.DecimalField(max_digits=8, decimal_places=4, default=0, verbose_name='加权利率')
    loan_interest = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='贷款年息')
    loan = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='贷款含ABS余额')
    net_BAB = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='银票净额')
    net_TF = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='贸易融资净额')
    net_GL = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='保函净额')
    net_total = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='一般用信净额')
    lr_BAB = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='全额银票')
    expire_date = models.DateField(auto_now_add=False, null=True, blank=True, verbose_name='业务到期')
    invest_banking = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='投行业务')
    invest_expire = models.DateField(auto_now_add=False, null=True, blank=True, verbose_name='投行到期日')
    ABS_expire = models.DateField(auto_now_add=False, null=True, blank=True, verbose_name='ABS到期日')
    defuse_expire = models.DateField(auto_now_add=False, null=True, blank=True, verbose_name='化解到期日')
    data_date = models.DateField(auto_now_add=False, null=True, blank=True)
    saving_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='储蓄余额')
    saving_yd_avg = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='储蓄日均')
    is_green_finance = models.BooleanField(default=False, verbose_name='绿色金融')

    def __str__(self):
        return self.customer.name

    class Meta:
        verbose_name = '贡献度名单'
        verbose_name_plural = verbose_name
        ordering = ['-data_date', 'department__display_order', '-customer__series__gov_plat_lev']


class ContributionTrees(models.Model):
    data_date = models.DateField(primary_key=True, auto_now_add=False, verbose_name='数据日期')
    contribution_tree = models.TextField(verbose_name='贡献度结构树')


class ExpirePrompt(models.Model):
    apply_type_choices = (
        (1, '如期'),
        (2, '暂缓'),
        (3, '退出'),
    )
    customer = models.ForeignKey('root_db.AccountedCompany', on_delete=models.CASCADE, verbose_name='客户')
    staff_id = models.ForeignKey('root_db.Staff', blank=True, null=True, on_delete=models.CASCADE, verbose_name='客户经理')
    expire_date = models.DateField(auto_now_add=False, null=True, blank=True, verbose_name='到期日')
    remark = models.CharField(max_length=512, default='', blank=True, null=True, verbose_name='备注')
    finish_date = models.DateField(auto_now_add=False, null=True, blank=True, verbose_name='办结日期')
    punishment = models.IntegerField(default=0, verbose_name='扣罚金额')
    created_at = models.DateField(auto_now_add=True)
    apply_type = models.IntegerField(choices=apply_type_choices, default=1, verbose_name='续做')
    current_progress = models.ForeignKey('app_customer_repository.Progress', blank=True, null=True, on_delete=models.CASCADE, verbose_name='系统进度')
    chushen = models.DateField(blank=True, null=True, verbose_name='预计初审')
    reply = models.DateField(blank=True, null=True, verbose_name='预计批复')
    cp_num = models.CharField(max_length=32, blank=True, null=True, verbose_name='授信编号')
    progress_update_date = models.DateField(blank=True, null=True)
    remark_update_date = models.DateField(blank=True, null=True)
    pre_approver = models.ForeignKey('root_db.Staff', blank=True, null=True, on_delete=models.CASCADE, related_name='xvshouxin_pre_approver', verbose_name='初审')
    approver = models.ForeignKey('root_db.Staff', blank=True, null=True, on_delete=models.CASCADE, related_name='xvshouxin_approver', verbose_name='专审')

    def __str__(self):
        return self.customer

    def toDict(self):
        fields = []
        d = {}
        for field in self._meta.fields:
            fields.append(field.name)
        import datetime
        for field in fields:
            field_obj = getattr(self, field)
            if isinstance(field_obj, datetime.datetime):
                d[field] = field_obj.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(field_obj, datetime.date):
                d[field] = field_obj.strftime('%Y-%m-%d')
            else:
                d[field] = str(field_obj)
        return d

    @classmethod
    def fill_cp_num(cls):
        dcms = connection.DcmsConnection('http://110.17.1.21:9082')
        dcms.login('czfzc', 'hxb123')
        customer_list = cls.objects.filter(
            Q(finish_date__isnull=True) &
            Q(cp_num__isnull=True)  &
            (Q(current_progress__status_num__lt=100) | Q(current_progress__isnull=True))
        ).values(
            'id',
            'customer__name',
        )
        from app_customer_repository.models import ProjectRepository
        for customer in customer_list:
            cp_num = dig.get_cp_num(dcms, customer['customer__name'])
            if cp_num:
                cls.objects.filter(pk=customer['id']).update(cp_num=cp_num)
                project = ProjectRepository.objects.filter(
                    customer__name=customer['customer__name'],
                    cp_con_num__isnull=True,
                    business_id__in=(11, 12),
                    tmp_close_date__isnull=False,
                    close_date__isnull=False
                )
                if project.exists():
                    project = project.order_by('-create_date')[0]
                    print('是否同步更新项目库中【' + project.project_name + '】的授信参考编号？\n0.否\n1.是')
                    need_fill_project_cp_num = input('>>>')
                    if int(need_fill_project_cp_num):
                        project.update(cp_con_num=cp_num)

    @classmethod
    def updateProgress(cls):
        imp_date = models_operation.DateOperation()
        updated = []
        non_updated = []
        approved = []
        dcms = connection.DcmsConnection('http://110.17.1.21:9082')
        dcms.login('czfzc', 'hxb123')
        customer_list = cls.objects.filter(
            Q(finish_date__isnull=True) &
            Q(cp_num__isnull=False) &
            (Q(current_progress__status_num__lt=100) | Q(current_progress__isnull=True))
        ).values(
            'id',
            'customer__name',
            'expire_date',
            'cp_num',
            'current_progress_id',
            'progress_update_date'
        )
        for customer in customer_list:
            progress_id, event_date = dig.get_cp_progress_id(dcms, customer['cp_num'])
            if progress_id == 0:
                non_updated.append(customer['customer__name'])
            elif progress_id == -1:
                print('【'+ customer['customer__name'] + customer['cp_num'] + '】流程已取消')
                cls.objects.filter(id=customer['id']).update(cp_num=None, current_progress_id=None)
            elif progress_id != customer['current_progress_id']:
                updated.append(customer['customer__name'] + str(customer['current_progress_id']) + '→' + str(progress_id))
                exp = cls.objects.filter(id=customer['id'])
                exp.update(current_progress_id=progress_id)

                if progress_id > 100:
                    approved.append(customer['customer__name'])
            pass
        for i in updated:
            print(i)
        print('\t\t其中新获批：', approved)
        print('无更新:', non_updated)

    @staticmethod
    def getCpNum(dcms, name, cf):
        customer = dcms.search_customer(name, cf)
        customer.go_to_cf_label('授信申请')


class LoanDemand(models.Model):
    add_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    customer = models.ForeignKey(to='root_db.AccountedCompany', blank=True, null=True, on_delete=models.PROTECT, verbose_name='客户')
    staff = models.ForeignKey(to='root_db.Staff', blank=True, null=True, on_delete=models.PROTECT, verbose_name='客户经理')
    expire_prompt = models.ForeignKey(to='ExpirePrompt', blank=True, null=True, on_delete=models.PROTECT, verbose_name='到期提示')
    # lu_ledger = models.ForeignKey(to='scraper.LuLedger', blank=True, null=True, on_delete=models.PROTECT, verbose_name='放款台账记录')
    contract = models.CharField(max_length=16, blank=True, null=True, verbose_name='放款合同号')
    expire_amount = models.IntegerField(default=0, verbose_name='存量到期金额')
    expire_date = models.DateField(blank=True, null=True, verbose_name='到期日')
    this_month_leishou = models.IntegerField(default=0, verbose_name='当月累收金额')
    new_increase = models.ForeignKey(to='app_customer_repository.ProjectRepository', blank=True, null=True, on_delete=models.PROTECT, verbose_name='新增项目')
    business = models.ForeignKey(to='scraper.DcmsBusiness', blank=True, null=True, on_delete=models.PROTECT, verbose_name='业务种类')
    # now_rate = models.FloatField(default=0, verbose_name='当前利率')
    # now_deposit_ydavg = models.IntegerField(default=0, verbose_name='当前存款日均')
    plan_amount = models.IntegerField(blank=True, null=True, verbose_name='拟放金额')
    plan_rate = models.FloatField(blank=True, null=True, verbose_name='拟放利率')
    plan_deposit_ratio = models.IntegerField(blank=True, null=True, verbose_name='预计存款回报')
    plan_date = models.DateField(blank=True, null=True, verbose_name='预计投放日期')
    expect = models.IntegerField(default=100, verbose_name='把握(%)')
    already_achieved = models.IntegerField(default=0, verbose_name='已放金额')
    remark = models.CharField(max_length=512, blank=True, null=True, verbose_name='备注（规模相关）')
    last_update = models.DateField(auto_now=True, blank=True, null=True, verbose_name='最后更新')
    add_date = models.DateField(auto_now_add=True, blank=True , null=True, verbose_name='添加日期')
    finish_date = models.DateField(blank=True, null=True, verbose_name='办结日')

    class Meta:
        verbose_name = '贷款需求'
        verbose_name_plural = verbose_name

    def __str__(self):
        if self.expire_prompt:
            customer_name = self.expire_prompt.customer.name
        elif self.new_increase:
            customer_name = self.new_increase.customer.name
        else:
            customer_name = 'None'
        return customer_name + str(self.plan_amount) + '万元'

    @classmethod
    def createFromProjectRepositoryForNextMonth(cls):
        pass

    @classmethod
    def createFromLuLedgerForNextMonth(cls):
        '''
        从放款台账中抽取到期贷款，生成贷款需求记录，并关联至EP表
        月末执行，执行前先爬取月末企贷表的贷款余额数据
        :return:
        '''
        imp_date = models_operation.DateOperation()
        next_month_last_date = imp_date.month_dif(1, imp_date.month_last_date())
        next_month_first_date = imp_date.month_dif(1, imp_date.month_first_date())
        expire_lu = LuLedger.objects.filter(
            Q(
                plan_expire__lte=next_month_last_date,
                plan_expire__gte=next_month_first_date,
                current_amount__gt=0,
                lu_num__startswith='LU',
                net_amount__gt=0,
            ) & (Q(dcms_business__caption__contains='贷') | Q(dcms_business__caption__contains='保理') | Q(dcms_business__caption__contains='押汇'))

        ).values(
            'lu_num',
            'customer_id',
            'current_amount',
            'rate',
            'dcms_business__code',
            'plan_expire',
            'staff_id',
            'contract_code'
        )
        for lu in expire_lu:
            customer_id = lu['customer_id']
            ep = ExpirePrompt.objects.filter(
                Q(customer_id=customer_id) &
                (
                    Q(expire_date__lte=next_month_last_date) |
                    Q(expire_date__gte=imp_date.month_dif(-3, imp_date.month_first_date()))
                )
            )
            obj_ep = None
            if ep.exists():
                ep_index = 0
                if ep.count() > 1:
                    print(ep[ep_index].customer.name, '存在多笔EP记录：')
                    for i in range(ep.count()):
                        print(i, '.到期日：', ep[i].expire_date , '，pk:' , ep[i].id)
                    ep_index = int(input('>>>'))
                obj_ep = ep[ep_index]
            cls(
                customer_id=customer_id,
                existing=obj_ep,
                existing_lu_id=lu['lu_num'],
                now_rate=lu['rate'],
                expire_amount=lu['current_amount'],
                expire_date=lu['plan_expire'],
                business_id=lu['dcms_business__code'],
                staff_id=lu['staff_id'],
                contract=lu['contract_code']
            ).save()

    @classmethod
    def updateByLeiShou(cls, data__gte=None):
        '''
        爬取累收表并更新贷款需求：
        1、贷款需求中有对应信贷合同号的，直接对相应贷款需求记录的当月累收金额字段进行累加
        2、贷款需求中，合同号为空，但是客户名和品种能匹配的，同上处理
        3、其他情况，在贷款需求中新建，并做好备注
        :param data__gte: 累收起始日，>=
        :return:
        '''
        imp_date = models_operation.DateOperation()
        last_update = imp_date.neighbour_date_date_str(cls, imp_date.today_str, 'last_update') and str(imp_date.delta_date(-1))
        print('贷款需求表上次更新日期', last_update, '是否是否以此作为累收表的起始日期进行抓取(__gte)？')
        print('0.否\n1.是')
        confirm = input('>>>')
        if confirm == '0':
            data__gte = input('累收表起始日期(__gte)>>>')
        else:
            data__gte = last_update
        crp = CrpHttpRequest()
        crp.login()
        crp.setDataDate(data__gte)
        query_fields = OrderedDict(**{'contract_code': '合同号', 'customer_name': '客户名称', 'dcms_business': '业务种类', 'date': '收回日期', 'amount': '收回金额(元)'})
        query_condition = {'收回日期': ">" + data__gte}
        leishou_aggregation = defaultdict(float)
        for page in crp.getLeiShou(*query_fields.values(), **query_condition):
            query_result = page.HTML_soup.find_all('td')[1:]
            col_num = len(query_fields)
            row_num = int(len(query_result) / col_num)
            for td_index in range(0, row_num, col_num):
                row_data = query_result[td_index: td_index + col_num]
                col_index = 0
                info = OrderedDict()
                for field in query_fields.keys():
                    # exec(field + '="' + re.sub(r'[,\s\t\n\r]', '', row_data[col_index].text) + '"', scope)
                    info[field] = re.sub(r'[,\s\t\n\r]', '', row_data[col_index].text)
                    col_index += 1
                leishou_aggregation[(info['contract_code'], info['customer_name'], info['dcms_business'], info['date'])] += float(info['amount']) / 10000
        for info, amount in leishou_aggregation.items():
            contract_code = info[0]
            customer_name = info[1]
            amount = int(amount)
            try:
                dcms_business = DcmsBusiness.objects.get(caption=info[2])
            except:
                print(customer_name, '未找到用信品种', info[2], '默认使用短期流贷。')
                dcms_business = DcmsBusiness.objects.get(pk='1011')
            existed_ld = cls.objects.filter(add_date__gte=imp_date.month_first_date(), contract=contract_code)
            if existed_ld.exists():
                index = 0
                if existed_ld.count() > 1:
                    print(customer_name, contract_code, '在本月贷款需求中存在多笔记录，请选择：')
                    for i in range(existed_ld.count()):
                        print(i, '到期日', existed_ld[i].expire_date, '，拟投放日', existed_ld[i].plan_date)
                    index = int(input('>>>'))
                existed_ld[index].this_month_leishou += amount
                existed_ld[index].save()
            else:
                pass
            pass


    @classmethod
    def createBaseRecordForNewMonth(cls):
        pass

    # @classmethod
    # def updateDemandAmountByLuLedger(cls):
    #     '''
    #     根据昨日放款更新贷款需求金额
    #     :return:
    #     '''
    #     imp_date = models_operation.DateOperation()
    #     last_update = imp_date.neighbour_date_date_str(cls, imp_date.today_str, 'last_update')
    #     newly_lu = LuLedger.objects.filter(add_date='')