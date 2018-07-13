from django.db import models
from deposit_and_credit import models_operation
from django.db.models import Q, Sum, F

EVENT = {

}

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
    claimer = models.ForeignKey('root_db.SubDepartment', null=True, blank=True, on_delete=models.PROTECT, verbose_name='认领')
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
    pretrial_doc = models.OneToOneField('PretrialDocument', blank=True, null=True, on_delete=models.PROTECT, verbose_name='预审表')
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
    account_num = models.DecimalField(default=0, max_digits=3, decimal_places=2, verbose_name='折算户数')
    is_defuse = models.BooleanField(default=False, verbose_name='涉及化解')
    is_pure_credit = models.BooleanField(default=False, verbose_name='纯信用')
    close_date = models.DateField(blank=True, null=True, verbose_name='关闭日期')
    close_reason = models.IntegerField(choices=close_reason_choices, blank=True, null=True)
    whose_matter = models.IntegerField(choices=whose_matter_choices, blank=True, null=True)

    def decide_is_focus(self):
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
            imp_d = models_operation.ImportantDate()
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

    def create_or_update(self):
        self.decide_is_focus()
        self.calculate_acc_num()
        self.save()

    def close(self):
        pass


class PretrialMeeting(models.Model):
    meeting_date = models.DateField(blank=True, null=True, verbose_name='会议日期')
    notify_date = models.DateField(blank=True, null=True, verbose_name='通报日期')
    result = models.CharField(max_length=256, blank=True, null=True)


class PretrialDocument(models.Model):
    meeting = models.ForeignKey('PretrialMeeting', on_delete=models.PROTECT)
    document_name = models.CharField(max_length=128, blank=True, null=True)
    accept_date = models.DateField(auto_now_add=True, blank=True, null=True)


class ProjectExecution(models.Model):
    key_node_choices = (
        (10, '预审/立项'),
        (20, '初审'),
        (30, '专审'),
        (40, '信审'),
        (50, '批复'),
        (60, '投放'),
        (70, '结束'),
    )
    project = models.ForeignKey('ProjectRepository', on_delete=models.PROTECT)
    event = models.IntegerField(choices=key_node_choices, blank=True, null=True)
    event_date = models.DateField(blank=True, null=True, verbose_name='事件日期')       # 区别于更新日，此为事件的发生日期
    update_date = models.DateTimeField(blank=True, null=True)
    current_progress = models.ForeignKey('Progress', blank=True, null=True, on_delete=models.PROTECT, verbose_name='进度')
    this_time_used = models.IntegerField(default=0, verbose_name='本次投放敞口')
    total_used = models.IntegerField(default=0, verbose_name='累计投放敞口')          # 自动计算
    new_net_used = models.IntegerField(default=0, verbose_name='累计投放新增敞口')      # 自动计算
    remark = models.ForeignKey('ProjectRemark', blank=True, null=True, on_delete=models.PROTECT)
    update_count = models.IntegerField(default=0, verbose_name='已更新次数')      # 以便捷的跳到上一次，用于比对进度等
    photo_date = models.DateField(auto_now_add=True, verbose_name='快照日期')

    class Meta:
        get_latest_by = 'update_date'
        ordering = (
            # 'project__staff__sub_department__superior',
            '-update_date',
        )

    @property
    def previous_update(self):
        return ProjectExecution.objects.filter(project_id=self.project_id).values_list('update_count', 'update_date').order_by('-update_count')[0]

    def update(self):
        pass


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

# Progress.objects.filter(id=11).values('suit_for_business__superior__caption')
# SubBusiness.objects.filter(caption='项目贷款').values_list('progress__caption')