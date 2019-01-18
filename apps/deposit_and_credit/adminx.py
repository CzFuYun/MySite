from django.db.models import Sum

import xadmin
from xadmin import views

from .models import Contributor, ExpirePrompt, LoanDemand
from root_db.models import DividedCompanyAccount

class ContributorAdmin:
    list_filter = ['data_date', 'customer__series', 'department']
    search_fields = ['customer']
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
    list_display = ['customer', 'staff_id', 'expire_date', 'remark']
    relfield_style = 'fk-ajax'


class LoanDemandAdmin:
    list_display = []


xadmin.site.register(Contributor, ContributorAdmin)
xadmin.site.register(ExpirePrompt, ExpirePromptAdmin)
xadmin.site.register(LoanDemand, LoanDemandAdmin)