from django.db import models
from django.db.models import Q, F, Sum, Max
from MySite import utilities
from app_customer_repository import models_operation as mo
from deposit_and_credit import models_operation, models as dac_m


industry_factor_rule = {
    'C': 1.5,
}


class CustomerRepository(models.Model):
    stockholder_choices = (
        (10, '国有'),
        (20, '民营'),
        (30, '外资'),
    )
    name = models.CharField(max_length=128, unique=True, verbose_name='企业名称')
    simple_name = models.CharField(max_length=32, unique=True, blank=True, null=True, verbose_name='企业简称')
    customer = models.ForeignKey('root_db.AccountedCompany', blank=True, null=True, verbose_name='核心客户号', on_delete=models.PROTECT)
    credit_file = models.CharField(max_length=16, blank=True, null=True, verbose_name='信贷文件')
    department = models.ForeignKey('root_db.Department', null=True, blank=True, on_delete=models.PROTECT, verbose_name='管户部门')
    type_of_3311 = models.ForeignKey('root_db.TypeOf3311', blank=True, null=True, on_delete=models.PROTECT, verbose_name='3311类型')
    is_strategy = models.BooleanField(default=False, verbose_name='是否战略客户')
    industry = models.ForeignKey('root_db.Industry', blank=True, null=True, on_delete=models.PROTECT, verbose_name='行业门类')
    stockholder = models.IntegerField(choices=stockholder_choices, blank=True, null=True, verbose_name='控股方式')
    taxes_2017 = models.IntegerField(default=0, verbose_name='2017年纳税（万元）')
    inter_clearing_2017 = models.IntegerField(default=0, verbose_name='2017年国际结算（万元）')

    def __str__(self):
        return self.name

    def getCustomer(self):
        pass


class ProjectRepository(models.Model):
    close_reason_choices = (
        (10, '预审未通过终止申报'),
        (20, '申报过程中终止'),
        (30, '分行续议后终止申报'),
        (35, '获批但未新增额度'),
        (40, '分行否决'),
        (50, '总行否决'),
        (60, '获批后不再继续'),
        (70, '部分落地后终止'),
        (80, '全部落地'),
        (90, '授信到期'),
    )
    whose_matter_choices = (
        (10, '我行原因'),
        (20, '监管原因'),
        (30, '客户原因'),
    )
    customer = models.ForeignKey('CustomerRepository', on_delete=models.PROTECT, verbose_name='客户')
    project_name = models.CharField(max_length=64, blank=True, null=True, verbose_name='项目名称')
    staff = models.ForeignKey('root_db.Staff', null=True, blank=True, on_delete=models.PROTECT, verbose_name='客户经理')
    cp_con_num = models.CharField(max_length=32, blank=True, null=True, verbose_name='授信编号')
    is_green = models.BooleanField(default=False, verbose_name='绿色金融')
    is_focus = models.BooleanField(default=False, verbose_name='重点项目')
    pretrial_doc = models.ForeignKey('PretrialDocument', blank=True, null=True, on_delete=models.PROTECT, verbose_name='预审表')
    create_date = models.DateField(auto_now_add=True, verbose_name='创建日期')
    plan_pretrial_date =  models.DateField(blank=True, null=True, verbose_name='计划预审')
    plan_chushen =  models.DateField(blank=True, null=True, verbose_name='计划初审')
    plan_zhuanshen =  models.DateField(blank=True, null=True, verbose_name='计划专审')
    plan_xinshen =  models.DateField(blank=True, null=True, verbose_name='计划信审')
    plan_reply =  models.DateField(blank=True, null=True, verbose_name='计划批复')
    plan_luodi =  models.DateField(blank=True, null=True, verbose_name='计划投放')
    business = models.ForeignKey('SubBusiness', on_delete=models.PROTECT, verbose_name='业务品种')
    total_net = models.IntegerField(default=0, verbose_name='总敞口')
    existing_net = models.IntegerField(default=0, verbose_name='存量敞口')
    reply_content = models.TextField(blank=True, null=True, verbose_name='批复内容')
    account_num = models.DecimalField(default=0, max_digits=3, decimal_places=2, verbose_name='折算户数')
    is_defuse = models.BooleanField(default=False, verbose_name='涉及化解')
    is_pure_credit = models.BooleanField(default=False, verbose_name='纯信用')
    close_date = models.DateField(blank=True, null=True, verbose_name='关闭日期')
    tmp_close_date = models.DateField(blank=True, null=True, verbose_name='临时关闭日期')
    close_reason = models.IntegerField(choices=close_reason_choices, blank=True, null=True, verbose_name='关闭理由')
    whose_matter = models.IntegerField(choices=whose_matter_choices, blank=True, null=True, verbose_name='责任方')
    reply_date = models.DateField(blank=True, null=True, verbose_name='批复日期')
    pre_approver = models.ForeignKey('root_db.Staff', blank=True, null=True, on_delete=models.PROTECT, related_name='pre_approver', verbose_name='初审')
    approver = models.ForeignKey('root_db.Staff', blank=True, null=True, on_delete=models.PROTECT, related_name='approver', verbose_name='专审')

    def __str__(self):
        return self.project_name

    def judge_is_focus(self):
        self.is_focus = True if self.total_net > 8000 or self.business.is_focus else False

    def calculate_acc_num(self):
        base = 1        # 基数
        factor = 1      # 系数
        b_id = self.business.id
        if b_id in range(10, 15):  # 一般授信的讲究比较多
            industry = self.customer.industry_id
            factor_industry = industry_factor_rule.get(industry, 1)     # 行业带来的系数，目前仅有制造业有额外加成系数1.5
            factor_3311 = 2 if self.customer.type_of_3311.id >= 10 else 1       # 3311客户加成系数2
            factor = factor_industry * factor_3311      # max(factor_industry, factor_3311)
            imp_d = models_operation.DateOperation()
            if self.existing_net:
                base = 0.5
            else:
                try:
                    history_sum_net = self.customer.customer.contributor_set.filter(
                        data_date__gte=imp_d.last_year_today,
                        data_date__lte=imp_d.today
                    ).values_list('net_total').aggregate(Sum('net_total'))['net_total__sum']
                    base = 0.5 if int(history_sum_net) else 1       # 一年内用过信或直接声明有存量敞口的，基数为0.5户
                except:
                    pass
        else:
            factor = self.business.acc_factor
        self.account_num = base * factor

    # @classmethod
    # def create_or_update(cls, pr_dict):
    #     '''
    #     根据传入的数据更新或创建储备项目，自动填充创建日期并生成快照
    #     :param pr_dict:
    #     :return:
    #     '''
    #     # fields = self._meta.fields
    #     imp_date = models_operation.DateOperation()
    #     need_photo = False
    #     if pr_dict.get('id'):       # 修改
    #         pr = ProjectRepository.objects.get(id=pr_dict['id'])
    #     else:       # 创建
    #         pr = ProjectRepository({**pr_dict, **{'create_date': imp_date.today}})
    #         need_photo = True
    #     # pr.judge_is_focus()
    #     # pr.calculate_acc_num()
    #     pr.save()
    #     if need_photo:
    #         ProjectExecution.takePhoto(pr)

    def create(self, **kwargs):
        if kwargs:
            self.__dict__.update(**kwargs)
        self.judge_is_focus()
        self.calculate_acc_num()
        self.save(force_insert=True)        # 强制数据库使用INSERT，而不是UDPATE语句
        ProjectExecution.takePhoto(self)

    def update(self, **kwargs):
        if kwargs:
            self.__dict__.update(**kwargs)
        self.save(force_update=True)

    def closeTemply(self, request):
        exclude_fields = ['csrfmiddlewaretoken', 'id']
        try:
            update_dict = {
                **{'tmp_close_date': models_operation.DateOperation().today},
                **getattr(request, request.method).dict()
            }
            for ef in exclude_fields:
                if update_dict.get(ef):
                    update_dict.pop(ef)
            self.update(**update_dict)
        except Exception as error:
            return False
        return True


class PretrialMeeting(models.Model):
    meeting_date = models.DateField(blank=True, null=True, verbose_name='会议日期')
    notify_date = models.DateField(blank=True, null=True, verbose_name='通报日期')
    result = models.CharField(max_length=256, blank=True, null=True)


class PretrialDocument(models.Model):
    meeting = models.ForeignKey('PretrialMeeting', on_delete=models.PROTECT)
    document_name = models.CharField(max_length=128, blank=True, null=True)
    accept_date = models.DateField(auto_now_add=True, blank=True, null=True)


class ProjectExecution(models.Model):
    project = models.ForeignKey('ProjectRepository', on_delete=models.PROTECT, verbose_name='项目')
    current_progress = models.ForeignKey('Progress', blank=True, null=True, on_delete=models.PROTECT, verbose_name='进度')
    total_used = models.IntegerField(default=0, verbose_name='累计投放敞口')          # 含本次
    new_net_used = models.IntegerField(default=0, verbose_name='累计投放新增敞口')      # 自动计算，含本次
    remark = models.ForeignKey('ProjectRemark', blank=True, null=True, on_delete=models.PROTECT, verbose_name='备注')
    update_count = models.IntegerField(default=0, verbose_name='已更新次数')      # 以便捷的跳到上一次，用于比对进度等
    photo_date = models.DateField(blank=True, null=True, verbose_name='快照日期')

    @property
    def previous_update(self):
        if self.id:     # 若本条记录确实存在于数据库
            today = models_operation.DateOperation().today
            pe = ProjectExecution.objects.filter(project_id=self.project_id, photo_date__lt=today)
            if pe.exists():
                return pe.values_list('update_count').order_by('-update_count')[0]
            return (0, )

    def update(self, pe_dict):
        '''
        更新进度
        :param pe_dict: 字段名和新值构成的字典
        :return:
        '''
        fields_to_compare = {
            'total_used': 'total_used',
            'remark': 'remark.content',
        }
        # fields_no_edit = ['project']
        # imp_date = models_operation.DateOperation()
        field_list = self._meta.fields
        self.previous_pe = ProjectExecution.objects.filter(project=self.project, update_count=self.update_count-1).first() or ProjectExecution()
        for field in field_list:
            field_name = field.name
            # if field in fields_no_edit:
            #     continue
            new_value = pe_dict.get(field_name, None)
            if new_value:
                if field_name in fields_to_compare:
                    if eval('self.previous_pe.' + fields_to_compare[field_name]) != new_value:
                        edit_method = getattr(self, '_update_' + field_name)
                        edit_method(new_value)
                    else:
                        pass
                else:
                    eval('self.' + field_name + '=' + new_value)
            else:
                pass
        self.save()

    @property
    def total_used_in_last_contribution(self):
        data_date = models_operation.DateOperation().last_data_date_str(dac_m.Contributor)
        c = self.project.customer.customer.contributor_set.filter(data_date=data_date)
        # customer = self.objects.prefetch_related('project__customer__customer_id')
        return c.annotate(Sum('net_total'))

    # @property
    # def total_used_after_last_borrow(self):
    #     '''
    #     上次投放后的用信净余额
    #     :return:
    #     '''

    def _update_total_used(self, new_value):
        self.total_used = new_value
        this_time_used = self.total_used - self.previous_pe.total_used     # 本次投放敞口=截至本次的总投放敞口-截至上次修改的总投放敞口
        self.new_net_used = this_time_used + self.previous_pe.new_net_used

    def _update_remark(self, new_value):
        new_remark = ProjectRemark(content=new_value)
        new_remark.save()
        self.remark = new_remark
        # self.save()

    @classmethod
    def takePhoto(cls, project_obj=None, photo_date=None):
        # from app_customer_repository.models import ProjectExecution
        imp_date = models_operation.DateOperation()

        if project_obj:
            if not photo_date:
                photo_date = imp_date.last_data_date_str(ProjectExecution, 'photo_date')
            ProjectExecution(
                project=project_obj,
                photo_date=photo_date,
                current_progress_id=0,
            ).save()
            return
        else:
            photo_date_str = str(photo_date) if photo_date else str(imp_date.today)
            if imp_date.last_data_date_str(cls, 'photo_date') == photo_date_str:
                return
            if photo_date_str:
                photo_date = imp_date.strToDate(photo_date_str)
            else:
                return
            # ↓临关超过半年的项目正式关闭
            ProjectRepository.objects.filter(
                tmp_close_date__isnull=False,
                tmp_close_date__lte=imp_date.delta_date(-180, photo_date),
            ).update(close_date=imp_date.today)
            # ↓流程中项目的客户号、总敞口
            project_customer = cls.objects.filter(
                project__close_date__isnull=True,
                # project__business_id=11,
            ).values(
                'project__customer__customer_id',
                'project__total_net',
                'project__existing_net',
            )
            customer_project_amount = {}
            for c in project_customer:
                customer_project_amount[c['project__customer__customer_id']] = {
                    'project__total_net': c['project__total_net'],
                    'project__existing_net': c['project__existing_net'],
                }
            # ↓查找一般授信已用信金额
            used_net_data = dac_m.Contributor.objects.filter(
                customer_id__in=customer_project_amount,
                data_date=imp_date.neighbour_date_date_str(dac_m.Contributor, photo_date_str)
            ).values(
                'customer_id',
                'net_total',
            )
            customer_used_net = {}
            for un in used_net_data:
                customer_used_net[un['customer_id']] = un['net_total']
            last_photo_date = imp_date.last_data_date_str(cls, 'photo_date')
            pe_on_the_way = cls.objects.filter(
                project__close_date__isnull=True,
                photo_date=last_photo_date
            )
            fields = cls._meta.get_fields()
            exclude_fields = ['id', 'photo_date',]
            pe_photo_list = []
            attention = []
            for pe in pe_on_the_way:
                tmp = {}
                for field in fields:
                    field_name = field.name
                    if field_name in exclude_fields:
                        continue
                    try:
                        field_data = getattr(pe, field_name)
                        tmp[field_name] = field_data
                    except:
                        field_data = getattr(pe, field_name + '_id')
                        tmp[field_name + '_id'] = field_data
                customer_id = pe.project.customer.customer_id
                tmp['photo_date'] = photo_date
                # ↓为一般授信填充已投放净额
                if pe.project.business.id < 15:
                    tmp['total_used'] = customer_used_net.get(customer_id, 0)
                    # ↓若已投净额小于项目的净额
                    if tmp['total_used'] <= customer_project_amount[customer_id]['project__total_net']:
                        tmp['new_net_used'] = tmp['total_used'] - customer_project_amount[customer_id]['project__existing_net']
                    # ↓若已投净额大项目的净额，则可能有两种情况：1、存在质押贷款；2、同时有多笔业务（例如既有项目贷又有流贷）
                    else:
                        attention.append(pe.project.customer.customer)
                pe_photo_list.append(cls(**tmp))
            if pe_photo_list:
                cls.objects.bulk_create(pe_photo_list)
                print('success')
            if attention:
                print('请核实以下客户的真实用信情况：')
                for a in attention:
                    print(a)

    @classmethod
    def lastExePhoto(cls):
        imp_date = models_operation.DateOperation()
        last_photo_date = imp_date.last_data_date_str(ProjectExecution, 'photo_date')
        exe_qs = ProjectExecution.objects.filter(photo_date=last_photo_date)
        return exe_qs


class Progress(models.Model):
    caption = models.CharField(max_length=32)
    status_num = models.IntegerField(default=0)
    display_order = models.IntegerField(default=0)
    star = models.ForeignKey('Stars', blank=True, null=True, on_delete=models.PROTECT)
    suit_for_business = models.ManyToManyField('SubBusiness')

    class Meta:
        ordering = ('display_order', )

    def __str__(self):
        return self.caption

    @classmethod
    def getSuitableProgressForSubbusiness(cls, subbusiness, return_mode=utilities.return_as['choice']):
        if type(subbusiness) == int:
            suit_progress = cls.objects.filter(suit_for_business=subbusiness, status_num__lte=100)
        elif type(subbusiness) == str:
            suit_progress = cls.objects.filter(suit_for_business__caption=subbusiness, status_num__lte=100)
        if return_mode == utilities.return_as['choice']:
            return suit_progress.values_list('id', 'caption')


class Business(models.Model):
    caption = models.CharField(max_length=32)
    display_order = models.IntegerField(default=0)

    def __str__(self):
        return self.caption

    @classmethod
    def getAllBusiness(cls, value='caption'):
        businesses = cls.objects.values(value).order_by('display_order')
        business_list = []
        for b in businesses:
            business_list.append(b[value])
        return business_list


class SubBusiness(models.Model):
    caption = models.CharField(max_length=32)
    superior = models.ForeignKey('Business', on_delete=models.PROTECT)
    display_order = models.IntegerField(default=0)
    is_focus = models.BooleanField(default=False, verbose_name='是否重点产品')
    acc_factor = models.FloatField(default=0, verbose_name='折算户数系数')

    class Meta:
        ordering = ('display_order', )

    def __str__(self):
        return self.caption

    @classmethod
    def getAllBusiness(cls):
        sub_bus_qs = cls.objects.values('id', 'caption', 'superior__caption').order_by('display_order')
        bus_list = []
        for b in sub_bus_qs:
            bus_list.append((b['id'], b['superior__caption'] + '　' + b['caption']))
        return bus_list


class Stars(models.Model):
    caption = models.CharField(max_length=32, blank=True, null=True)
    description = models.CharField(max_length=64, blank=True, null=True)


class ProjectRemark(models.Model):
    content = models.TextField(blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content + ('\n' + str(self.create_date) if self.create_date else '')


class TargetTask(models.Model):
    '''

    '''
    target_type_choices = (
        (10, '计划户数'),
        (20, '计划金额'),
    )
    department = models.ForeignKey('root_db.Department', blank=True, null=True, on_delete=models.PROTECT)
    business = models.ForeignKey('Business', blank=True, null=True, on_delete=models.PROTECT)
    target_amount = models.FloatField(blank=True, null=True)
    target_type = models.IntegerField(choices=target_type_choices, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    @classmethod
    def calculate_target(cls, sd='', ed='', business_obj=None, returnType='dict'):
        imp_date = models_operation.DateOperation()
        start_date = imp_date.strToDate(sd) if sd else imp_date.this_year_start_date
        end_date = imp_date.strToDate(ed) if ed else imp_date.this_year_end_date
        if imp_date.month_and_date(start_date) in ('01-01', '04-01', '07-01', '10-01') and imp_date.month_and_date(end_date) in ('03-31', '06-30', '09-30', '12-31'):
            q_start_date = Q(start_date=start_date)
            q_end_date = Q(end_date=end_date)
            q_business = Q(business=business_obj) if business_obj else Q(business_id__gte=0)
            filter_condition = (q_start_date & q_end_date & q_business)
            if not cls.objects.filter(filter_condition).exists():
                q_start_date = Q(start_date__gte=start_date)
                q_end_date = Q(end_date__lte=end_date)
                filter_condition = (q_start_date & q_end_date & q_business)
            qs = cls.objects.filter(filter_condition)
            if returnType == 'qs':
                return qs.order_by('department__display_order', 'business_id', 'target_type', 'start_date')
            elif returnType == 'dict':
                qs = qs.values(
                'department__caption',
                'business__caption',
                'target_type',
            ).annotate(Sum('target_amount')).order_by('department__display_order').order_by('department__display_order')
                dept_target = {}
                target_type_sr = mo.field_choices_to_dict(cls.target_type_choices, False)
                for i in qs:
                    department = i['department__caption']
                    business = i['business__caption']
                    target_type = target_type_sr.get(str(i['target_type']))
                    target_amount__sum = i['target_amount__sum']
                    if not dept_target.get(department):
                        dept_target[department] = {}
                    if not dept_target[department].get(business):
                        dept_target[department][business] = {}
                    if not dept_target[department][business].get(target_type):
                        dept_target[department][business][target_type] = 0
                    dept_target[department][business][target_type] = target_amount__sum
                return dept_target
            return



# b=SubBusiness.objects.filter(id=11)
# Progress.objects.filter(suit_for_business__caption='一般授信')
