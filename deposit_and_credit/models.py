
from django.db import models
from root_db import models as m
from django.db.models import Sum


class DepartmentDeposit(models.Model):
    data_date = models.DateField(null=True, blank=True)
    sub_department = models.ForeignKey(m.SubDepartment, to_field='sd_code', on_delete=models.PROTECT)
    amount = models.BigIntegerField(default=0, verbose_name='余额（万元）')
    md_avg = models.BigIntegerField(default=0, verbose_name='月日均（万元）')
    sd_avg = models.BigIntegerField(default=0, verbose_name='季日均（万元）')
    yd_avg = models.BigIntegerField(default=0, verbose_name='年日均（万元）')

    class Meta:
        unique_together = ('data_date', 'sub_department', )


########################################################################################################################
class IndustryDeposit(models.Model):
    data_date = models.DateField(null=True, blank=True)
    industry = models.ForeignKey(m.Industry, to_field='code', default=1, on_delete=models.PROTECT)
    amount = models.BigIntegerField(default=0, verbose_name='余额（万元）')
    md_avg = models.BigIntegerField(default=0, verbose_name='月日均（万元）')
    sd_avg = models.BigIntegerField(default=0, verbose_name='季日均（万元）')
    yd_avg = models.BigIntegerField(default=0, verbose_name='年日均（万元）')

    class Meta:
        unique_together = ('data_date', 'industry', )


class Contributor(models.Model):
    customer = models.ForeignKey('root_db.AccountedCompany', on_delete=models.PROTECT, verbose_name='客户')
    department = models.ForeignKey('root_db.Department', null=True, blank=True, on_delete=models.PROTECT, verbose_name='经营部门')
    approve_line = models.CharField(max_length=8, default='', verbose_name='审批条线')
    staff = models.ForeignKey(m.Staff, null=True, blank=True, on_delete=models.PROTECT)
    loan_rate = models.DecimalField(max_digits=8, decimal_places=4, default=0, verbose_name='加权利率（%）')
    loan_interest = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='贷款年息（万元）')
    loan = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='贷款含ABS余额（万元）')
    net_BAB = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='银票净额（万元）')
    net_TF = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='贸易融资净额（万元）')
    net_GL = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='保函净额（万元）')
    net_total = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='一般用信净额（万元）')
    lr_BAB = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='全额银票（万元）')
    expire_date = models.DateField(auto_now_add=False, null=True, blank=True)
    invest_banking = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='投行业务（万元）')
    invest_expire = models.DateField(auto_now_add=False, null=True, blank=True, verbose_name='投行到期日')
    ABS_expire = models.DateField(auto_now_add=False, null=True, blank=True, verbose_name='ABS到期日')
    defuse_expire = models.DateField(auto_now_add=False, null=True, blank=True, verbose_name='化解到期日')
    data_date = models.DateField(auto_now_add=False, null=True, blank=True)
    saving_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='储蓄余额（万元）')
    saving_yd_avg = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='储蓄日均（万元）')
    is_green_finance = models.BooleanField(default=False)

    def __str__(self):
        return self.customer.name

    class Meta:
        verbose_name_plural = '回报客户清单'


class ContributionTrees(models.Model):
    data_date = models.DateField(primary_key=True, auto_now_add=False, verbose_name='数据日期')
    contribution_tree = models.TextField(verbose_name='贡献度结构树')


class ExpirePrompt(models.Model):
    customer = models.ForeignKey(m.AccountedCompany, on_delete=models.PROTECT)
    staff_id = models.ForeignKey(m.Staff, blank=True, null=True, on_delete=models.PROTECT)
    expire_date = models.DateField(auto_now_add=False, null=True, blank=True)
    remark = models.CharField(max_length=512, default='')
    explain = models.CharField(max_length=256, blank=True, null=True)
    finish_date = models.DateField(auto_now_add=False, null=True, blank=True, verbose_name='办结日期')
    punishment = models.IntegerField(default=0, verbose_name='扣罚金额')
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)

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