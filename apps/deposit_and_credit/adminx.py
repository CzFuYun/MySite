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
    list_display = ('add_time', '_vf_customer', 'get_expire_prompt_info', 'expire_amount', 'this_month_leishou', 'already_achieved')
    list_filter = ('plan_date', )
    search_fields = ('customer__name',)
    list_editable = ('finish_date', 'already_achieved')

    def _vf_customer(self, instance):
        if instance.customer:
            return instance.customer.name
        else:
            return instance.project.customer.name
    _vf_customer.short_description = '客户名称'

    def get_expire_prompt_info(self, instance):
        return instance.expire_prompt_id
    get_expire_prompt_info.short_description = '到期提示'


class LoanDemandForThisMonthAdmin:
    list_display = ('_vf_customer', '_vf_dept', '_vf_staff', '_vf_industry', 'plan_amount', '_vf_progress', '_vf_stage', 'this_month_leishou', 'already_achieved', '_vf_remark')
    ordering = ('staff__sub_department__superior__display_order', 'staff', '-plan_amount')
    list_per_page = 100

    def _vf_customer(self, instance):
        if instance.customer:
            return instance.customer.name
        else:
            return instance.project.customer.name
    _vf_customer.short_description = '客户名称'

    def _vf_dept(self, instance):
        return instance.staff.sub_department.superior
    _vf_dept.short_description = '经营部门'

    def _vf_staff(self, instance):
        return instance.staff.name
    _vf_staff.short_description = '客户经理'

    def _vf_industry(self, instance):
        return instance.customer.industry
    _vf_industry.short_description = '行业门类'

    def _vf_progress(self, instance):
        current_progress = None
        if instance.project:
            current_progress = instance.project.current_progress
        elif instance.expire_prompt:
            current_progress = instance.expire_prompt.current_progress
        self.current_progress = current_progress
        if instance.plan_amount:
            return '未建档' if current_progress is None else current_progress
        else:
            return '收回'
    _vf_progress.short_description = '当前进度'

    def _vf_stage(self, instance):
        if self.current_progress is None:
            return ''
        else:
            status_num = self.current_progress.status_num
            if status_num <= 30:
                return '支行'
            elif status_num < 100:
                return '分行'
            else:
                return '已批'
    _vf_stage.short_description = '阶段'

    def _vf_remark(self, instance):
        remark = None
        if instance.project:
            remark = instance.project.projectexecution_set.first().remark
            remark = remark.content
        elif instance.expire_prompt:
            remark = instance.expire_prompt.remark
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


xadmin.site.register(Contributor, ContributorAdmin)
xadmin.site.register(ExpirePrompt, ExpirePromptAdmin)
xadmin.site.register(LoanDemand, LoanDemandAdmin)
xadmin.site.register(LoanDemandForThisMonth, LoanDemandForThisMonthAdmin)