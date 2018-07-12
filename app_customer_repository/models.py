from django.db import models
from deposit_and_credit import models_operation


EVENT = {

}

# star = (
#     {0.5: '☆'},
#     {1.0: '★'},
#     {1.5: '★☆'},
#     {2.0: '★★'},
#     {2.5: '★★☆'},
#     {3.0: '★★★'},
#     {3.5: '★★★☆'},
#     {4.0: '★★★★'},
#     {4.5: '★★★★☆'},
#     {5.0: '★★★★★'},
#     {5.5: '★★★★★☆'},
#     {6.0: '★★★★★★'},
# )

class CustomerRepository(models.Model):
    stockholder_choices = (
        (10, '国有'),
        (20, '民营'),
        (30, '外资'),
    )
    name = models.CharField(max_length=128, unique=True, verbose_name='企业名称')
    simple_name = models.CharField(max_length=32, unique=True, blank=True, null=True)
    customer_id = models.ForeignKey('root_db.AccountedCompany', blank=True, null=True, verbose_name='核心客户号', on_delete=models.PROTECT)
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
    business = models.ForeignKey('SubBusiness', on_delete=models.PROTECT)
    total_apply_net = models.IntegerField(default=0, verbose_name='申报敞口（万元）')
    newly_increase_net = models.IntegerField(default=0, verbose_name='存量敞口（万元）')
    already_used_new_net = models.IntegerField(default=0, verbose_name='已投新增敞口（万元）')
    account_num = models.DecimalField(default=0, max_digits=3, decimal_places=2, verbose_name='折算户数')
    is_defuse = models.BooleanField(default=False, verbose_name='涉及化解')
    is_pure_credit = models.BooleanField(default=False, verbose_name='纯信用')
    close_date = models.DateField(blank=True, null=True, verbose_name='关闭日期')
    close_reason = models.IntegerField(choices=close_reason_choices, blank=True, null=True)
    whose_matter = models.IntegerField(choices=close_reason_choices, blank=True, null=True)

    def decide_is_focus(self):
        if self.is_pure_credit or self.business_id >= 15 or self.total_apply_net > 8000:
            return True
        return False

    # def markStars(self):
    #     if self.is_focus:
    #         pass

    def convertAccountNumber(self):
        pass

    def create(self):
        pass

    def update(self):
        pass

    def finish(self):
        pass

    def remove(self):
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
    event_choices = (
        (40, '流程中止'),
        (50, '获批'),
        (55, '续议'),
        (56, '分行否决'),
        (58, '总行否决'),
        (60, '投放'),
        (70, '未完终止'),
        (80, '完全落地'),
    )
    project = models.ForeignKey('ProjectRepository', on_delete=models.PROTECT)
    event = models.IntegerField(choices=event_choices, blank=True, null=True)
    event_date = models.DateField(blank=True, null=True, verbose_name='事件日期')       # 区别于更新日，此为事件的发生日期
    update_date = models.DateTimeField(auto_now_add=True)
    current_progress = models.ForeignKey('Progress', blank=True, null=True, on_delete=models.PROTECT, verbose_name='进度')
    borrow = models.IntegerField(default=0, verbose_name='本次投放（万元）')
    remark = models.CharField(max_length=512, blank=True, null=True)
    update_count = models.IntegerField(default=0, verbose_name='更新次数')      # 以便捷的跳到上一次，用于比对进度等
    is_last_status = models.BooleanField(default=False)


    class Meta:
        get_latest_by = 'update_date'
        ordering = (
            # 'project__staff__sub_department__superior',
            '-update_date',
        )

    def countUpdate(self):
        event_date = models_operation.ImportantDate().today
        pass

    def update(self):
        self.countUpdate()


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


# Progress.objects.filter(id=11).values('suit_for_business__superior__caption')
# SubBusiness.objects.filter(caption='项目贷款').values_list('progress__caption')