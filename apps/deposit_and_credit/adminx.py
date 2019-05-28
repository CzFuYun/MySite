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
    list_display = ('_vf_customer', 'staff', '_vf_progress', 'expire_amount', 'plan_amount', 'this_month_leishou', 'already_achieved', 'plan_date', 'finish_date', 'remark', '_vf_remark')
    list_editable = ('staff', 'expire_amount', 'plan_amount', 'this_month_leishou', 'already_achieved', 'remark', 'plan_date', 'finish_date')
    list_filter = ('plan_date', 'add_time', 'already_achieved', 'finish_date')
    search_fields = ('customer__name',)
    list_per_page = 100

    def queryset(self):
        qs = super().queryset()
        # start_date = imp_date.month_first_date()
        # end_date = imp_date.month_last_date()
        return qs.filter(
            Q(finish_date__isnull=True)
        )


class LoanDemandForThisMonthAdmin:
    list_display = ('_vf_customer', '_vf_dcms_customer_code', '_vf_dept', '_vf_staff', '_vf_industry', 'expire_amount', 'plan_amount', '_vf_progress', '_vf_status_num', '_vf_stage', 'this_month_leishou', 'already_achieved', 'remark', '_vf_remark')
    ordering = ('staff__sub_department__superior__display_order', 'staff', '-plan_amount')
    list_editable = ('remark', )
    list_filter = ('finish_date', )
    list_per_page = 100

    def queryset(self):
        qs = super().queryset()
        start_date = imp_date.month_first_date()
        end_date = imp_date.month_last_date()
        # return qs.filter(
        #     # Q(finish_date__isnull=True) &
        #     (
        #         Q(plan_date__range=(start_date, end_date)) #|
        #         #Q(add_time__range=(start_date, end_date))
        #     )
        # )
        return qs.filter(
            Q(plan_date__range=(start_date, end_date)) |
            Q(add_time__range=(start_date, end_date))
        )

    # def save_models(self):
    #     request = self.request
    #     new_obj = self.new_obj
    #     new_obj.save()
    #     pass


xadmin.site.register(Contributor, ContributorAdmin)
xadmin.site.register(ExpirePrompt, ExpirePromptAdmin)
xadmin.site.register(LoanDemand, LoanDemandAdmin)
xadmin.site.register(LoanDemandForThisMonth, LoanDemandForThisMonthAdmin)