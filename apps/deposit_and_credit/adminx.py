import re

from django.db.models import Sum, Q

import xadmin
from xadmin import views

from .models import Contributor, ExpirePrompt, LoanDemand, LoanDemandForThisMonth
from root_db.models import DividedCompanyAccount
from deposit_and_credit.models_operation import DateOperation

imp_date = DateOperation()

class ContributorAdmin:
    list_filter = ['data_date', 'customer__series', 'department']
    search_fields = ['customer__name']
    list_display = [
        'approve_line', 'customer', 'department', 'getIndustry',
        'loan_rate', 'loan', 'net_BAB', 'net_TF', 'net_GL', 'net_total', 'invest_banking',
        'totalDeposit_amount', 'saving_amount', 'totalDeposit_ydavg', 'saving_yd_avg',
        'getSeries', 'getGovLevel', 'defuse_expire'
    ]
    # list_export_fields = [*list_display, *[ 'defuse_expire']]
    list_per_page = 10

    def getSeries(self, instance):
        return instance.customer.series
    getSeries.short_description = '系列'

    def getIndustry(self, instance):
        return instance.customer.industry
    getIndustry.short_description = '行业'

    def totalDeposit_ydavg(self, instance):
        customer = instance.customer
        data_date = instance.data_date
        costomer_set = DividedCompanyAccount.objects.filter(customer=customer, data_date=data_date)
        return costomer_set.aggregate(Sum('divided_yd_avg'))['divided_yd_avg__sum']
    totalDeposit_ydavg.short_description = '对公存款年日均'

    def totalDeposit_amount(self, instance):
        customer = instance.customer
        data_date = instance.data_date
        costomer_set = DividedCompanyAccount.objects.filter(customer=customer, data_date=data_date)
        return costomer_set.aggregate(Sum('divided_amount'))['divided_amount__sum']
    totalDeposit_amount.short_description = '对公存款余额'

    def getGovLevel(self, instance):
        return instance.customer.series.gov_plat_lev
    getGovLevel.short_description = '平台等级'


class ExpirePromptAdmin:
    ordering = ['staff_id__sub_department__superior__display_order', 'staff_id']
    list_filter = ['expire_date', 'finish_date', 'current_progress']
    list_display = ['pk', 'customer', 'staff_id', 'expire_date', 'current_progress', '_vf_status_num', 'remark', 'finish_date']
    list_editable = ['finish_date']
    search_fields = ('customer__name', )
    relfield_style = 'fk-ajax'


class LoanDemandAdmin:
    list_display = ('_vf_customer', 'staff', 'expire_amount', 'plan_amount', 'this_month_leishou', 'already_achieved', 'remark', 'this_month_must', 'add_time')
    list_editable = ('staff', 'expire_amount', 'plan_amount', 'this_month_leishou', 'already_achieved', 'remark', 'this_month_must')
    list_filter = ('plan_date', 'add_time')
    search_fields = ('customer__name',)

    def _vf_customer(self, instance):
        if instance.customer:
            return instance.customer.name
        else:
            return instance.project.customer.name
    _vf_customer.short_description = '客户名称'

    def _vf_expire(self, instance):
        return instance.expire_prompt_id
    _vf_expire.short_description = '到期提示'


class LoanDemandForThisMonthAdmin:
    list_display = ('_vf_customer', '_vf_dept', '_vf_staff', '_vf_industry', 'expire_amount', 'plan_amount', '_vf_progress', '_vf_status_num', '_vf_stage', 'this_month_leishou', 'already_achieved', 'remark', '_vf_remark')
    ordering = ('staff__sub_department__superior__display_order', 'staff', '-plan_amount')
    list_editable = ('remark', )
    list_per_page = 100

    def _vf_customer(self, instance):
        self.pr = instance.project
        self.ep = instance.expire_prompt
        self.staff = instance.staff
        if self.pr:
            self.staff = self.pr.staff
        elif self.ep:
            self.staff = self.ep.staff_id
        if instance.customer:
            self.customer = instance.customer
        elif self.pr:
            self.customer = self.pr.customer
        elif self.ep:
            self.customer = self.ep.customer
        return self.customer.name
    _vf_customer.short_description = '客户名称'

    def _vf_dept(self, instance):
        return self.staff.sub_department.superior
    _vf_dept.short_description = '经营部门'

    def _vf_staff(self, instance):
        return self.staff.name
    _vf_staff.short_description = '客户经理'

    def _vf_industry(self, instance):
        return self.customer.industry
    _vf_industry.short_description = '行业门类'

    def _vf_progress(self, instance):
        current_progress = None
        if self.pr:
            current_progress = self.pr.current_progress
        elif self.ep:
            current_progress = self.ep.current_progress
        self.current_progress = current_progress
        if instance.plan_amount:
            return '未建档' if current_progress is None else current_progress
        else:
            return '收回'
    _vf_progress.short_description = '当前进度'

    def _vf_status_num(self, instance):
        return self.current_progress.status_num if self.current_progress else 0
    _vf_status_num.short_description = '进度代码'

    def _vf_stage(self, instance):
        if instance.plan_amount == 0:
            return '收回'
        elif instance.already_achieved:
            return '已投'
        if self.current_progress is None:
            return '其他'
        else:
            status_num = self.current_progress.status_num
            if status_num <= 30:
                return '支行'
            elif status_num < 85:
                return '分行'
            elif status_num == 85:
                return '总行'
            elif status_num >= 100:
                return '已批'
            else:
                return str(self.current_progress)
    _vf_stage.short_description = '阶段'

    def _vf_remark(self, instance):
        remark = None
        if self.pr:
            remark = self.pr.projectexecution_set.first().remark
            remark = remark.content
        elif self.ep:
            remark = self.ep.remark
            if remark:
                remark = re.split(r'<\d{4}-\d{2}-\d{2}>', remark)
                try:
                    remark = remark[-2]
                except:
                    remark = remark[-1]
        return remark or ''
    _vf_remark.short_description = '备注'

    def queryset(self):
        qs = super().queryset()
        start_date = imp_date.month_first_date()
        end_date = imp_date.month_last_date()
        return qs.filter(
            Q(finish_date__isnull=True) & (
                Q(plan_date__range=(start_date, end_date)) |
                Q(add_time__range=(start_date, end_date))
            )
        )

    def save_models(self):
        request = self.request
        new_obj = self.new_obj
        new_obj.save()
        pass


xadmin.site.register(Contributor, ContributorAdmin)
xadmin.site.register(ExpirePrompt, ExpirePromptAdmin)
xadmin.site.register(LoanDemand, LoanDemandAdmin)
xadmin.site.register(LoanDemandForThisMonth, LoanDemandForThisMonthAdmin)