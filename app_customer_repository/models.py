from django.db import models
from django.db.models import Q, F, Sum, Max
from deposit_and_credit import models_operation


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
    simple_name = models.CharField(max_length=32, unique=True, blank=True, null=True)
    customer = models.ForeignKey('root_db.AccountedCompany', blank=True, null=True, verbose_name='核心客户号', on_delete=models.PROTECT)
    credit_file = models.CharField(max_length=16, blank=True, null=True, verbose_name='信贷文件')
    department = models.ForeignKey('root_db.Department', null=True, blank=True, on_delete=models.PROTECT, verbose_name='支行')
    type_of_3311 = models.ForeignKey('root_db.TypeOf3311', blank=True, null=True, on_delete=models.PROTECT, verbose_name='3311类型')
    is_strategy = models.BooleanField(default=False, verbose_name='是否战略客户')
    industry = models.ForeignKey('root_db.Industry', blank=True, null=True, on_delete=models.PROTECT)
    stockholder = models.IntegerField(choices=stockholder_choices, blank=True, null=True)
    taxes_2017 = models.IntegerField(default=0, verbose_name='2017年纳税（万元）')
    inter_clearing_2017 = models.IntegerField(default=0, verbose_name='2017年国际结算（万元）')


class ProjectRepository(models.Model):
    close_reason_choices = (
        (10, '预审未通过终止申报'),
        (20, '申报过程中终止'),
        (30, '分行续议后终止申报'),
        (40, '分行否决'),
        (50, '总行否决'),
        (60, '获批后不再继续'),
        (70, '部分落地后终止'),
        (80, '全部落地'),
    )
    whose_matter_choices = (
        (10, '我行原因'),
        (20, '监管原因'),
        (30, '客户原因'),
    )
    customer = models.ForeignKey('CustomerRepository', on_delete=models.PROTECT)
    project_name = models.CharField(max_length=64, blank=True, null=True, verbose_name='项目名称')
    staff = models.ForeignKey('root_db.Staff', null=True, blank=True, on_delete=models.PROTECT)
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
    business = models.ForeignKey('SubBusiness', on_delete=models.PROTECT)
    total_net = models.IntegerField(default=0, verbose_name='总敞口')
    existing_net = models.IntegerField(default=0, verbose_name='存量敞口')
    reply_content = models.TextField(blank=True, null=True, verbose_name='批复内容')
    account_num = models.DecimalField(default=0, max_digits=3, decimal_places=2, verbose_name='折算户数')
    is_defuse = models.BooleanField(default=False, verbose_name='涉及化解')
    is_pure_credit = models.BooleanField(default=False, verbose_name='纯信用')
    close_date = models.DateField(blank=True, null=True, verbose_name='关闭日期')
    tmp_close_date = models.DateField(blank=True, null=True, verbose_name='临时关闭日期')
    close_reason = models.IntegerField(choices=close_reason_choices, blank=True, null=True)
    whose_matter = models.IntegerField(choices=whose_matter_choices, blank=True, null=True)
    reply_date = models.DateField(blank=True, null=True, verbose_name='批复日期')

    def judge_is_focus(self):
        self.is_focus = True if self.total_net > 8000 or self.is_pure_credit or self.business.id >= 15 else False

    def calculate_acc_num(self):
        base = 1
        factor = 1      # 系数
        b_id = self.business.id
        if b_id in range(20, 30):      # 投行项目
            factor = 2
        elif b_id in range(10, 20):    # 一般授信
            industry = self.customer.industry_id
            factor = 2 if b_id == 15 else industry_factor_rule.get(industry, 1)     # 项目贷系数2，制造业1.5，其他1
            factor = max(factor, 2 if self.customer.type_of_3311.id >= 10 else 1)   # 3311系数2
            imp_d = models_operation.DateOperation()
            if self.existing_net:
                base = 0.5
            else:
                history_sum_net = self.customer.customer.contributor_set.filter(
                    data_date__gte=imp_d.last_year_today,
                    data_date__lte=imp_d.today
                ).values_list('net_total').aggregate(Sum('net_total'))['net_total__sum']
                base = 0.5 if int(history_sum_net) else 1       # 一年内用过信或直接声明有存量敞口的，基数为0.5户
        else:
            base = 0        # 投行和一般授信以外的业务，不折算户数
        self.account_num = base * factor

    @classmethod
    def create_or_update(cls, pr_dict):
        '''
        根据传入的数据更新或创建储备项目，自动填充创建日期并生成快照
        :param pr_dict:
        :return:
        '''
        # fields = self._meta.fields
        imp_date = models_operation.DateOperation()
        need_photo = False
        if pr_dict.get('id'):       # 修改
            pr = ProjectRepository.objects.get(id=pr_dict['id'])
        else:       # 创建
            pr = ProjectRepository(**pr_dict)
            pr.create_date = imp_date.today
            need_photo = True
        pr.judge_is_focus()
        pr.calculate_acc_num()
        pr.save()
        if need_photo:
            ProjectExecution.takePhoto(pr)

    # def close(self):
    #     imp_date = models_operation.DateOperation()
    #     self.close_date = imp_date.today
    #     self.save()


class PretrialMeeting(models.Model):
    meeting_date = models.DateField(blank=True, null=True, verbose_name='会议日期')
    notify_date = models.DateField(blank=True, null=True, verbose_name='通报日期')
    result = models.CharField(max_length=256, blank=True, null=True)


class PretrialDocument(models.Model):
    meeting = models.ForeignKey('PretrialMeeting', on_delete=models.PROTECT)
    document_name = models.CharField(max_length=128, blank=True, null=True)
    accept_date = models.DateField(auto_now_add=True, blank=True, null=True)


class ProjectExecution(models.Model):
    # key_node_choices = (
    #     (10, '预审/立项'),
    #     (20, '初审'),
    #     (30, '专审'),
    #     (40, '信审'),
    #     (50, '批复'),
    #     (60, '投放'),
    #     (70, '关闭'),
    # )
    project = models.ForeignKey('ProjectRepository', on_delete=models.PROTECT)
    # event = models.IntegerField(choices=key_node_choices, blank=True, null=True)        # 事件，也可作为申报阶段
    event_date = models.DateField(blank=True, null=True, verbose_name='事件日期')       # 区别于更新日，此为事件的发生日期
    update_date = models.DateField(blank=True, null=True)
    current_progress = models.ForeignKey('Progress', blank=True, null=True, on_delete=models.PROTECT, verbose_name='进度')
    total_used = models.IntegerField(default=0, verbose_name='累计投放敞口')          # 含本次
    this_time_used = models.IntegerField(default=0, verbose_name='本次投放敞口')      # 自动计算
    new_net_used = models.IntegerField(default=0, verbose_name='累计投放新增敞口')      # 自动计算，含本次
    remark = models.ForeignKey('ProjectRemark', blank=True, null=True, on_delete=models.PROTECT)
    update_count = models.IntegerField(default=0, verbose_name='已更新次数')      # 以便捷的跳到上一次，用于比对进度等
    photo_date = models.DateField(blank=True, null=True, verbose_name='快照日期')

    class Meta:
        get_latest_by = 'update_date'
        ordering = ('-update_date', )

    @property
    def previous_update(self):
        if self.id:     # 若本条记录确实存在于数据库
            today = models_operation.DateOperation().today
            pe = ProjectExecution.objects.filter(project_id=self.project_id, photo_date__lt=today)
            if pe.exists():
                return pe.values_list('update_count', 'update_date').order_by('-update_count')[0]
            return (0, None)

    def execute_processing(self, pe_dict):
        '''
        更新进度
        :param pe_dict: 字段名和新值构成的字典
        :return:
        '''
        fields_to_compare = {
            # 'event': 'event',
            'total_used': 'total_used',
            'remark': 'remark.content',
        }
        # fields_no_edit = ['project', 'event', '']
        imp_date = models_operation.DateOperation()
        field_list = self._meta.fields
        self.previous_pe = ProjectExecution.objects.get(project=self.project, update_count=self.update_count-1) or ProjectExecution()
        for f in field_list:
            field = f.name
            # if field in fields_no_edit:
            #     continue
            new_value = pe_dict.get(field, None)
            if new_value:
                if field in fields_to_compare:
                    if eval('self.previous_pe.' + fields_to_compare[field]) != new_value:
                        edit_method = getattr(self, '_edit_' + field)
                        edit_method(new_value)
                    else:
                        pass
                else:
                    eval('self.' + field + '=' + new_value)
            else:
                pass
        self.update_date = imp_date.today
        self.save()

    def _edit_total_used(self, new_value):
        self.total_used = new_value
        self.this_time_used = self.total_used - self.previous_pe.total_used     # 本次投放敞口=截至本次的总投放敞口-截至上次修改的总投放敞口
        self.new_net_used = self.this_time_used + self.previous_pe.new_net_used

    def _edit_remark(self, new_value):
        new_remark = ProjectRemark(content=new_value)
        new_remark.save()
        self.remark = new_remark

    @classmethod
    def takePhoto(cls, project_obj=None):
        # from app_customer_repository.models import ProjectExecution
        imp_date = models_operation.DateOperation()
        if project_obj:
            ProjectExecution(
                project=project_obj,
                photo_date=imp_date.today,
            ).save()
        else:
            photo_date_str = input('photo date?>>>')
            if imp_date.last_data_date_str(cls, 'photo_date') == photo_date_str:
                return
            if photo_date_str:
                photo_date = imp_date.strToDate(photo_date_str)
            else:
                return
            exclude_fields = ['id', 'photo_date']
            ProjectRepository.objects.filter(tmp_close_date__lte=imp_date.delta_date(-180, photo_date)).update(close_date=imp_date.today)
            pe_on_the_way = cls.objects.filter(project__close_date__isnull=True)
            fields = cls._meta.get_fields()
            pe_photo_list = []
            for pe in pe_on_the_way:
                tmp = {}
                for field in fields:
                    field_name = field.name
                    if field_name in exclude_fields:
                        continue
                    tmp[field_name] = getattr(pe, field_name)
                tmp['photo_date'] = photo_date
                pe_photo_list.append(cls(**tmp))
            if pe_photo_list:
                cls.objects.bulk_create(pe_photo_list)


class Progress(models.Model):
    caption = models.CharField(max_length=32)
    status_num = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    display_order = models.IntegerField(default=0)
    star = models.ForeignKey('Stars', blank=True, null=True, on_delete=models.PROTECT)
    suit_for_business = models.ManyToManyField('SubBusiness')


class Business(models.Model):
    caption = models.CharField(max_length=32)
    display_order = models.IntegerField(default=0)


class SubBusiness(models.Model):
    caption = models.CharField(max_length=32)
    superior = models.ForeignKey('Business', on_delete=models.PROTECT)
    display_order = models.IntegerField(default=0)


class Stars(models.Model):
    caption = models.CharField(max_length=32, blank=True, null=True)
    description = models.CharField(max_length=64, blank=True, null=True)


class ProjectRemark(models.Model):
    content = models.TextField(blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)


class TargetTask(models.Model):
    '''

    '''
    target_type_choices = (
        (10, '户数'),
        (20, '金额'),
    )
    department = models.ForeignKey('root_db.Department', blank=True, null=True, on_delete=models.PROTECT)
    business = models.ForeignKey('Business', blank=True, null=True, on_delete=models.PROTECT)
    target_amount = models.FloatField(blank=True, null=True)
    target_type = models.IntegerField(choices=target_type_choices, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    @classmethod
    def calculate_target(cls, sd='', ed='', business_obj=None):
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
            qs = cls.objects.filter(filter_condition).values(
                'department',
                'business',
                'target_type',
            ).annotate(Sum('target_amount')).order_by('department__display_order')
            dept_target = {}
            for i in qs:
                department = i['department']
                business = i['business']
                target_type = i['target_type']
                target_amount__sum = i['target_amount__sum']
                if not dept_target.get(department):
                    dept_target[department] = {}
                if not dept_target[department].get(business):
                    dept_target[department][business] = {}
                if not dept_target[department][business].get(target_type):
                    dept_target[department][business][target_type] = 0
                dept_target[department][business][target_type] = target_amount__sum
            return dept_target


# Progress.objects.filter(id=11).values('suit_for_business__superior__caption')
# SubBusiness.objects.filter(caption='项目贷款').values_list('progress__caption')
