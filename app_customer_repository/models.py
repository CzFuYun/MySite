from django.db import models
from deposit_and_credit import models_operation
# class CustomerStore(models.Model):
#     name = models.CharField(max_length=128, unique=True, verbose_name='企业名称')
#     industry = models.ForeignKey('root_db.Industry', null=True, blank=True, on_delete=models.PROTECT, verbose_name='行业')
#     sub_industry = models.CharField(max_length=64, null=True, blank=True, verbose_name='细分行业')
#     district = models.ForeignKey('root_db.District', null=True, blank=True, on_delete=models.PROTECT, verbose_name='区域')
#     type_of_3311 = models.ForeignKey('root_db.TypeOf3311', on_delete=models.PROTECT, verbose_name='3311类型')
#
#     taxes = models.PositiveIntegerField(verbose_name='纳税金额（万元）')
#     taxes_rank = models.PositiveSmallIntegerField(verbose_name='纳税排名')
#     inlet = models.PositiveIntegerField(verbose_name='进口额（万美元）')
#     export = models.PositiveIntegerField(verbose_name='出口额（万美元）')
#     in_port = models.PositiveIntegerField(verbose_name='进出口额（万美元）')
#     in_port_rank = models.PositiveSmallIntegerField(verbose_name='进出口排名')
#     claimer = models.ForeignKey('root_db.Department', null=True, blank=True, on_delete=models.PROTECT, verbose_name='认领状态')
#
#
#     class Meta:
#         verbose_name_plural = '客户库'

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
        (1, '国有'),
        (2, '民营'),
        (3, '外资'),
    )
    name = models.CharField(max_length=128, unique=True, verbose_name='企业名称')
    simple_name = models.CharField(max_length=32, unique=True, blank=True, null=True)
    customer_id = models.ForeignKey('root_db.AccountedCompany', blank=True, null=True, verbose_name='核心客户号', on_delete=models.PROTECT)
    credit_file = models.CharField(max_length=16, blank=True, null=True, verbose_name='信贷文件')
    claimer = models.ForeignKey('root_db.SubDepartment', null=True, blank=True, on_delete=models.PROTECT, verbose_name='认领')
    staff = models.ForeignKey('root_db.Staff', null=True, blank=True, on_delete=models.PROTECT)
    type_of_3311 = models.ForeignKey('root_db.TypeOf3311', blank=True, null=True, on_delete=models.PROTECT, verbose_name='3311类型')
    is_strategy = models.BooleanField(default=False, verbose_name='是否战略客户')
    industry = models.ForeignKey('root_db.Industry', blank=True, null=True, on_delete=models.PROTECT)
    stockholder = models.IntegerField(choices=stockholder_choices, blank=True, null=True)
    taxes_2017 = models.IntegerField(default=0, verbose_name='2017年纳税（万元）')
    inter_clearing_2017 = models.IntegerField(default=0, verbose_name='2017年国际结算（万元）')


class ProjectRepository(models.Model):
    customer = models.ForeignKey('CustomerRepository', on_delete=models.PROTECT)
    project_name = models.CharField(max_length=64, blank=True, null=True, verbose_name='项目名称')
    cp_con_num = models.CharField(max_length=32, blank=True, null=True, verbose_name='授信编号')
    is_green = models.BooleanField(default=False, verbose_name='绿色金融')
    is_focus = models.BooleanField(default=False, verbose_name='重点项目')
    pretrial_date = models.DateField(blank=True, null=True, verbose_name='预审日期')
    pretrial_file = models.CharField(max_length=128, blank=True, null=True, verbose_name='预审表')
    create_date = models.DateField(auto_now_add=True, verbose_name='创建日期')
    business = models.ForeignKey('SubBusiness', on_delete=models.PROTECT)
    total_apply_net = models.IntegerField(default=0, verbose_name='申报总敞口（万元）')
    count = models.DecimalField(default=0, max_digits=3, decimal_places=2, verbose_name='折算户数')
    newly_increase_net = models.IntegerField(default=0, verbose_name='其中存量新增敞口（万元）')
    is_defuse = models.BooleanField(default=False, verbose_name='涉及化解')
    close_date = models.DateField(blank=True, null=True, verbose_name='关闭日期')

    def decideIsFocus(self):
        pass

    def paintStars(self):
        pass

    def convertCount(self):
        pass


class ProjectExcution(models.Model):
    event_choices = (
        (1, '建立联系'),
        (2, '方案洽谈'),
        (3, '方案确定'),
        (4, '预审/立项'),
        (5, ''),
        (6, ''),
    )

    project = models.ForeignKey('ProjectRepository', on_delete=models.PROTECT)

    # event = models.IntegerField(choices=)
    event_date = models.DateField(blank=True, null=True, verbose_name='事件日期')       # 区别于更新日，此为事实的发生日期
    update_times = models.IntegerField(default=0, verbose_name='更新次数')      # 可以便捷的跳到上一次，用于比对进度或修改is_newest
    update_date = models.DateField(auto_now=True)
    is_newest = models.BooleanField(default=False)
    progress = models.ManyToManyField('Progress')
    stars = models.CharField(max_length=32, blank=True, null=True, verbose_name='重点项目标识')
    remark = models.CharField(max_length=512, blank=True, null=True)
    
    def countUpdate(self):
        event_date = models_operation.ImportantDate().today
        pass

    def createStars(self):
        pass

    def update(self):
        self.countUpdate()
        self.createStars()



class Progress(models.Model):
    caption = models.CharField(max_length=32)
    status_num = models.DecimalField(default=0, max_digits=2, decimal_places=1)
    suit_for_business = models.ManyToManyField('SubBusiness')




class Business(models.Model):
    caption = models.CharField(max_length=32)


class SubBusiness(models.Model):
    caption = models.CharField(max_length=32)
    super_business = models.ForeignKey('Business', on_delete=models.PROTECT)

