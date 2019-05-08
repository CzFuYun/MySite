# coding: utf-8
import re
from collections import defaultdict, namedtuple, OrderedDict

from django.db import models
from django.db.models import Q, Sum

from MySite.utilities import reverseDictKeyValue
from root_db.models import AccountedCompany
from deposit_and_credit.models_operation import DateOperation
from scraper.models import LuLedger, DcmsBusiness, DailyLeiShou
from app_customer_repository.models import ProjectRepository, ProjectExecution
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
    add_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = '业务到期提示'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.customer.name + str(self.expire_date)

    def _vf_status_num(self):
        return self.current_progress.status_num
    _vf_status_num.short_description = '状态码'

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
    def fillCpNum(cls):
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
        imp_date = DateOperation()
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

    @classmethod
    def createByLedger(cls):
        '''
        通过放款台账、授信台账增加记录
        :return:
        '''
        from scraper.models import LuLedger, CpLedger
        imp_date = DateOperation()
        last_add = imp_date.last_data_date_str(cls, 'add_date')
        expire_date__lte = imp_date.month_dif(3, last_add)
        LuLedger.objects.filter(
            current_amount__gt=0,
            lu_num__startswith='LU',
            plan_expire__lte=expire_date__lte,
            cp__expire_date__lte=expire_date__lte,
        ).values(
            'customer_id'
        ).distinct()

    @staticmethod
    def getCpNum(dcms, name, cf):
        customer = dcms.search_customer(name, cf)
        customer.go_to_cf_label('授信申请')



class LoanDemand(models.Model):
    add_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='添加时间')
    customer = models.ForeignKey(to='root_db.AccountedCompany', blank=True, null=True, on_delete=models.PROTECT, verbose_name='客户')
    # customer = models.CharField(max_length=128, blank=True, null=True, verbose_name='客户')
    staff = models.ForeignKey(to='root_db.Staff', blank=True, null=True, on_delete=models.PROTECT, verbose_name='客户经理')
    business = models.ForeignKey(to='scraper.DcmsBusiness', blank=True, null=True, on_delete=models.PROTECT, verbose_name='业务种类')
    expire_prompt = models.ForeignKey(to='ExpirePrompt', blank=True, null=True, on_delete=models.PROTECT, verbose_name='到期提示')
    project = models.ForeignKey(to='app_customer_repository.ProjectRepository', blank=True, null=True, on_delete=models.PROTECT, verbose_name='项目储备')
    # lu_ledger = models.ForeignKey(to='scraper.LuLedger', blank=True, null=True, on_delete=models.PROTECT, verbose_name='放款台账记录')
    contract = models.CharField(max_length=32, blank=True, null=True, verbose_name='放款合同号（到期）')
    expire_date = models.DateField(blank=True, null=True, verbose_name='到期日')
    expire_amount = models.IntegerField(default=0, verbose_name='存量到期金额')
    plan_amount = models.IntegerField(default=0, verbose_name='拟放金额')
    this_month_leishou = models.IntegerField(default=0, verbose_name='当月累收')
    already_achieved = models.IntegerField(default=0, verbose_name='当月累放')
    # now_rate = models.FloatField(default=0, verbose_name='当前利率')
    # now_deposit_ydavg = models.IntegerField(default=0, verbose_name='当前存款日均')
    plan_rate = models.FloatField(blank=True, null=True, verbose_name='拟放利率')
    plan_deposit_ratio = models.IntegerField(blank=True, null=True, verbose_name='预计存款回报')
    plan_date = models.DateField(blank=True, null=True, verbose_name='预计投放日期')
    expect = models.IntegerField(default=100, verbose_name='把握(%)')
    remark = models.TextField(blank=True, null=True, verbose_name='备注（规模相关）')
    # can_increase_deposit = models.BooleanField(default=False, verbose_name='存款增长来源')
    last_update = models.DateField(auto_now=True, blank=True, null=True, verbose_name='最后更新')
    # add_date = models.DateField(auto_now_add=True, blank=True , null=True, verbose_name='添加日期')
    finish_date = models.DateField(blank=True, null=True, verbose_name='办结日')

    class Meta:
        verbose_name = '贷款需求'
        verbose_name_plural = verbose_name
        ordering = ('staff__sub_department__superior__display_order', '-add_time')

    def __str__(self):
        if self.expire_prompt:
            customer_name = self.expire_prompt.customer.name
        elif self.project:
            customer_name = self.project.project_name
        else:
            customer_name = self.customer.name
        return customer_name + str(self.plan_amount) + '万元'

    def _vf_current_progress(self):
        try:
            return self.expire_prompt.current_progress
        except:
            try:
                return self.project.current_progress
            except:
                return
    _vf_current_progress.short_description = '当前进度'

    # @classmethod
    # def createFromProjectRepositoryForNextMonth(cls):
    #     # imp_date = DateOperation()
    #     # ↓目前已建档且未落地的授信项目
    #     project = ProjectRepository.objects.filter(
    #         current_progress__status_num__gte=30,
    #         current_progress__status_num__lt=200,
    #         business__superior_id=10,
    #         tmp_close_date__isnull=True,
    #         customer__customer_id__isnull=False
    #     )
    #     for p in project:
    #         project_name = p.project_name
    #         if cls.objects.filter(project=p).exists():
    #             print(project_name, '已存在于贷款需求表中')
    #         else:
    #             print(project_name, '当前进度', p.current_progress, '是否可能投放？')
    #             print('0.否\n1.是')
    #             choice = input('>>>')
    #             if int(choice):
    #                 last_pe = ProjectExecution.lastExePhoto().get(project=p)
    #                 plan_date = p.plan_luodi
    #                 if not plan_date:
    #                     print(project_name, '预计落地时间？')
    #                     plan_date = input('>>>')
    #                 cls(
    #                     customer_id=p.customer.customer_id,
    #                     staff=p.staff,
    #                     project=p,
    #                     plan_amount=p.total_net - last_pe.total_used,
    #                     plan_date=plan_date
    #                 ).save()
    #
    # @classmethod
    # def createFromLuLedgerForNextMonth(cls):
    #     '''
    #     从放款台账中抽取到期贷款，生成贷款需求记录，并关联至EP表
    #     月末执行，执行前先爬取月末企贷表的贷款余额数据
    #     :return:
    #     '''
    #     # LuLedger.fillInfo()      # 先通过爬取企贷表更新用信余额
    #     imp_date = DateOperation()
    #     next_month_last_date = imp_date.month_dif(1, imp_date.month_last_date())
    #     next_month_first_date = imp_date.month_dif(1, imp_date.month_first_date())
    #     expire_lu = LuLedger.objects.filter(
    #         Q(
    #             plan_expire__lte=next_month_last_date,
    #             plan_expire__gte=next_month_first_date,
    #             current_amount__gt=0,
    #             lu_num__startswith='LU',
    #             net_amount__gt=0,
    #         ) & (Q(dcms_business__caption__contains='贷') | Q(dcms_business__caption__contains='保理') | Q(dcms_business__caption__contains='押汇'))
    #     ).values(
    #         'lu_num',
    #         'customer_id',
    #         'current_amount',
    #         'rate',
    #         'dcms_business__code',
    #         'plan_expire',
    #         'staff_id',
    #         'contract_code'
    #     )
    #     for lu in expire_lu:
    #         customer_id = lu['customer_id']
    #         cls(
    #             customer=AccountedCompany.objects.get(customer_id=customer_id).name,
    #             # existing=obj_ep,
    #             existing_lu_id=lu['lu_num'],
    #             now_rate=lu['rate'],
    #             expire_amount=lu['current_amount'],
    #             expire_date=lu['plan_expire'],
    #             business_id=lu['dcms_business__code'],
    #             staff_id=lu['staff_id'],
    #             contract=lu['contract_code']
    #         ).save()

    # @classmethod
    # def updateByLeiShou(cls, retract_date__gte=None):
    #     '''
    #     爬取累收表并更新贷款需求：
    #     1、贷款需求中有对应信贷合同号的，直接对相应贷款需求记录的当月累收金额字段进行累加
    #     2、贷款需求中，合同号为空，但是客户名和品种能匹配的，同上处理
    #     3、其他情况，在贷款需求中新建，并做好备注
    #     :param retract_date__gte: 收回日期大于等于
    #     :return:
    #     '''
    #     imp_date = DateOperation()
    #     if retract_date__gte is None:
    #         last_update = imp_date.neighbour_date_date_str(cls, imp_date.today_str, 'last_update') or str(imp_date.delta_date(-1))
    #         print('贷款需求表上次更新日期', last_update, '是否以此作为累收表的起始日期进行抓取(__gte)？')
    #         print('0.否\n1.是')
    #         confirm = input('>>>')
    #         if confirm == '0':
    #             retract_date__gte = input('累收表起始日期(__gte)>>>')
    #         else:
    #             retract_date__gte = last_update
    #     crp = CrpHttpRequest()
    #     crp.login()
    #     crp.setDataDate()
    #     query_fields = OrderedDict(**{0: '合同号', 1: '客户名称', 2: '业务种类', 3: '收回日期', 4: '收回金额(元)'})
    #     query_condition = {'收回日期': crp.DateCondition.earlierThan(retract_date__gte)}#">" + retract_date__gte}
    #     leishou_aggregation = defaultdict(float)
    #     for page in crp.getLeiShou(*query_fields.values(), **query_condition):
    #         query_result = page.HTML_soup.find_all('td')[1:]
    #         col_num = len(query_fields)
    #         row_num = int(len(query_result) / col_num)
    #         for td_index in range(0, row_num, col_num):
    #             row_data = query_result[td_index: td_index + col_num]
    #             col_index = 0
    #             info = OrderedDict()
    #             for field in query_fields.values():
    #                 # exec(field + '="' + re.sub(r'[,\s\t\n\r]', '', row_data[col_index].text) + '"', scope)
    #                 info[field] = re.sub(r'[,\s\t\n\r]', '', row_data[col_index].text)
    #                 col_index += 1
    #             leishou_aggregation[(info['合同号'], info['客户名称'], info['业务种类'], info['收回日期'])] += float(info['收回金额(元)']) / 10000
    #     index_reflect = reverseDictKeyValue(query_fields)
    #     default_business = DcmsBusiness.objects.get(pk='1011')      # 短期流贷
    #     for info, amount in leishou_aggregation.items():
    #         business_name = info[index_reflect['业务种类']]
    #         if business_name.__contains__('贷') or business_name.__contains__('保理'):
    #             contract_code = info[index_reflect['合同号']].split('_')[0]
    #             customer_name = info[index_reflect['客户名称']]
    #             amount = int(amount)
    #             existed_ld = cls.objects.filter(add_time__gte=imp_date.month_first_date(), contract=contract_code)
    #             if existed_ld.exists():
    #                 index = 0
    #                 if existed_ld.count() > 1:
    #                     print(customer_name, contract_code, '在本月贷款需求中存在多笔记录，请选择：')
    #                     for i in range(existed_ld.count()):
    #                         print('\t', i, '.到期日', existed_ld[i].expire_date, '拟投放日', existed_ld[i].plan_date)
    #                     index = int(input('>>>'))
    #                 this_month_leishou = existed_ld[index].this_month_leishou
    #                 cls.objects.filter(pk=existed_ld[index].pk).update(this_month_leishou= amount + this_month_leishou)
    #                 # existed_ld[index].this_month_leishou = amount + this_month_leishou
    #                 # existed_ld[index].save()
    #                 print(customer_name, contract_code, '合同项下', info[index_reflect['收回日期']], '收回', amount, '已更新至贷款需求→当月累收')
    #             else:       # 若不存在贷款需求，则询问处理方式
    #                 print(customer_name, contract_code, '合同项下', info[index_reflect['收回日期']], '收回', amount, '不存在对应的贷款需求记录，是否新建')
    #                 print('0.否\n1.是（建议选是，以便轧差）')
    #                 need_add= input('>>>')
    #                 if int(need_add):
    #                     try:
    #                         dcms_business = DcmsBusiness.objects.get(caption=business_name)
    #                     except:
    #                         print(customer_name, '未找到用信品种', business_name, '默认使用短期流贷。')
    #                         dcms_business = default_business
    #                     cls(
    #                         customer=customer_name,
    #                         business=dcms_business,
    #                         contract=contract_code,
    #                         this_month_leishou=amount
    #                     ).save()
    #         else:
    #             continue

    @classmethod
    def linkToEpRecord(cls, add_date__gte=None, add_date__lte=None):
        '''
        关联至对应的到期提示
        :param add_date: 贷款需求记录的生成日期，字符串形式
        :return:
        '''
        imp_date = DateOperation()
        next_month_last_date = imp_date.month_dif(1, imp_date.month_last_date())
        # next_month_first_date = imp_date.month_dif(1, imp_date.month_first_date())
        add_date__gte = add_date__gte or imp_date.today_str
        add_date__lte = add_date__lte or imp_date.delta_date(1, imp_date.today_str)
        not_linked = cls.objects.filter(
            # add_time__gte=add_date__gte,
            # add_time__lte=add_date__lte,
            expire_prompt_id__isnull=True
        ).values(
            'pk',
            'customer__name',
        )
        no_customer = []
        for nl in not_linked:
            customer_name = nl['customer__name']
            try:
                customer_id = AccountedCompany.objects.get(name=customer_name).pk
                ep = ExpirePrompt.objects.filter(
                    Q(customer_id=customer_id) &
                    (
                        Q(expire_date__lte=next_month_last_date) |
                        Q(expire_date__gte=imp_date.month_dif(-3, imp_date.month_first_date()))
                    )
                )
                if ep.exists():
                    print('请选择', customer_name, 'EP（到期提示）记录：')
                    print('\t', '0.不关联')
                    for i in range(ep.count()):
                        print('\t', i + 1, '.到期日：', ep[i].expire_date, '，主键：', ep[i].id)
                    ep_index = int(input('>>>'))
                    if ep_index:
                        cls.objects.filter(pk=nl['pk']).update(expire_prompt=ep[int(ep_index) - 1])
            except:
                no_customer.append(customer_name)
        if no_customer:
            print('【注意】以下客户未找到与之名称一致的已开户客户，无法进行EP记录关联')
            for i in no_customer:
                print('\t', i)        # 可能信贷系统或此系统中未及时更新客户名

    @classmethod
    def linkToProjectRepository(cls, add_date=None):
        imp_date = DateOperation()
        next_month_last_date = imp_date.month_dif(1, imp_date.month_last_date())
        # next_month_first_date = imp_date.month_dif(1, imp_date.month_first_date())
        add_date = add_date or imp_date.today_str

    @classmethod
    def createBaseRecordForNewMonth(cls):
        pass

    @classmethod
    def updateByLeishouAndLu(cls):
        '''
        根据累收及放款更新贷款需求
        :return:
        '''
        imp_date = DateOperation()
        last_update = imp_date.neighbour_date_date_str(cls, imp_date.today_str, 'last_update')
        newly_leishou = DailyLeiShou.objects.filter(
            add_date=imp_date.today_str,
            dcms_business__caption__contains='贷',
        ).exclude(
            contract_code__startswith='CZZX'
        ).values(
            'pk',
            'retract_amount',
            'contract_code',
            'customer_id',
            'customer__name',
            'dcms_business_id',
        )
        for nl in newly_leishou:
            loan_demand = LoanDemand.objects.filter(contract=nl['contract_code']).values(
                'pk',
                'expire_amount',
                'this_month_leishou',
            )
            ld_data_dict = {}
            if not loan_demand.exists():
                ld_data_dict['customer_id'] = nl['customer_id']
                ld_data_dict['contract'] = nl['contract_code']
                ld_data_dict['expire_amount'] = nl['retract_amount']
                ld_data_dict['this_month_leishou'] = nl['retract_amount']
                ld_data_dict['business_id'] = nl['dcms_business_id']
                try:
                    old_lu = LuLedger.objects.get(contract_code=nl['contract_code'])
                    ld_data_dict['expire_date'] = old_lu.plan_expire
                    ld_data_dict['staff_id'] = old_lu.staff_id or None
                except:
                    pass
                LoanDemand.objects.create(**ld_data_dict)
                print(nl['customer__name'], nl['contract_code'], '合同项下收回', nl['retract_amount'], '不在计划（LD）内，已在贷款需求表中添加相关记录')
            else:
                ld_data_dict['this_month_leishou'] = loan_demand.first()['this_month_leishou'] + nl['retract_amount']
                ld_data_dict['expire_amount'] = max(ld_data_dict['this_month_leishou'], loan_demand.first()['expire_amount'])
                loan_demand.update(**ld_data_dict)
                print(nl['customer__name'], nl['contract_code'], '合同项下收回', nl['retract_amount'], '已在LD中更新其累收数')
        newly_lu = LuLedger.objects.filter(
            update_date=imp_date.today_str,
            dcms_business__caption__contains='贷',
            lu_num__startswith='LU'
        ).values(
            'pk',
            'customer_id',
            'customer__name',
            'lend_amount',
            'staff_id',
        )
        for nl in newly_lu:
            # ↓关联至贷款需求记录并累加其当月累放金额
            loan_demand = cls.objects.filter(customer_id=nl['customer_id'])
            if loan_demand.exists():
                # ↓将此次投放金额依次去“填”每笔贷款需求中的未投放部分
                left_lend = nl['lend_amount'] / 10000
                for ld in loan_demand:
                    left_demand = ld.plan_amount - ld.already_achieved
                    if left_lend <= left_demand:        # 若填不满
                        ld.already_achieved = ld.plan_amount + ld.already_achieved
                        ld.save(update_fields=['already_achieved'])
                        break
                    else:
                        ld.already_achieved = ld.plan_amount
                        left_lend -= left_demand
                if left_lend > 0:       # 若填掉所有贷款需求的坑后还有盈余
                    to_increase_demand =  cls.objects.filter(
                        customer_id=nl['customer_id'], expire_amount=0
                    )
                    if to_increase_demand.exists():
                        to_increase_demand = to_increase_demand.order_by('expire_amount').first()
                        plan_amount = to_increase_demand.plan_amount
                        to_increase_demand.plan_amount = plan_amount + left_lend
                        to_increase_demand.already_achieved = plan_amount + left_lend
                        to_increase_demand.save(update_fields=['plan_amount', 'already_achieved'])
                    else:
                        cls.objects.create(
                            customer_id=nl['customer_id'],
                            already_achieved=left_lend,
                            plan_amount=left_lend,
                            staff_id=nl['staff_id'],
                        )
                    print('计划内客户', nl['customer__name'], '投放', nl['lend_amount'] / 10000, '万元，但其本月累放已超过计划，已同步更新其计划、累放金额')
                else:
                    print('计划内客户', nl['customer__name'], '投放', nl['lend_amount'] / 10000, '万元，已更新其累放金额')
            else:
                new_ld = LoanDemand.objects.create(
                    customer_id=nl['customer_id'],
                    already_achieved=nl['lend_amount'] / 10000,
                    plan_amount=nl['lend_amount'] / 10000,
                    staff_id=nl['staff_id'],
                )
                print('计划外客户', nl['customer__name'], '投放', nl['lend_amount'] / 10000, '万元，已创建贷款需求并同步更新其累放金额')


class LoanDemandForThisMonth(LoanDemand):
    class Meta:
        verbose_name = '本月贷款规模安排'
        verbose_name_plural = verbose_name
        proxy = True


class CreditAmount(models.Model):
    add_date = models.DateField(auto_now_add=True)
    amount = models.FloatField(default=0, verbose_name='余额（万元）')
    lu = models.ForeignKey(to='scraper.LuLedger', blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name = '信贷余额'
        verbose_name_plural = verbose_name

    @classmethod
    def takePhotoFromLuLedger(cls):
        from scraper.models import LuLedger
        amounted = LuLedger.objects.filter(current_amount__gt=0).values(
            'pk',
            'current_amount'
        )
        data_for_bulk_create = [cls(lu_id=a['pk'], amount=a['current_amount']) for a in amounted]
        cls.objects.bulk_create(data_for_bulk_create)