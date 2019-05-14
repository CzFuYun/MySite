# from django.db.models import Sum

import xadmin, re

from django import forms
from xadmin.views.edit import ModelFormAdminView
from xadmin.plugins.actions import BaseActionView

from MySite.utilities import cleanCompanyName, downloadWorkbook
from scraper.models import LuLedger, LuLedgerForExport, CpLedger, DailyLeiShou
from scraper.dcms_request import DcmsHttpRequest
from root_db.models import AccountedCompany



# class LuCreationModelForm(forms.ModelForm):
#     lu_num = forms.CharField(max_length=32, label='放款参考编号')
#     is_green = forms.BooleanField()
#
#     class Meta:
#         model = LuLedger
#         fields = ('lu_num', 'is_green')
#
#     def clean_lu_num(self):
#         rgx_lu_num = re.compile(r'[A-Z]{2,5}/[A-Z]{2}\d{2}/\d{4}/\d{2}/\d{8}')
#         if rgx_lu_num.match(self.lu_num.strip()):
#             return rgx_lu_num.findall(self.lu_num.strip())[0]
#         raise ValueError('非法格式的参考编号')

class DownLoadLuLedger(BaseActionView):
    action_name = '导出'
    description = '导出'
    model_perm = 'view'

    def do_action(self, queryset):
        pass

class LuLedgerAdmin:
    ordering = ('-add_date', '-lend_date', )
    list_display = ('lu_num', 'customer', 'dcms_business', 'lend_amount', 'lend_date', '_vf_inspector_name', 'is_inspected', 'add_date')
    list_filter = ('lend_date', 'department', 'cp__cp_type')
    search_fields = ('customer__name', 'contract_code', 'lu_num', 'contract_code')
    list_editable = ('is_inspected', )
    list_per_page = 20
    actions = (DownLoadLuLedger, )

    # add_form = LuCreationModelForm
    def get_readonly_fields(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            return (
                'staff',
                'plan_expire', 'month_dif',
                'rate',
                'float_ratio','has_baozheng', 'has_diya',
                'has_zhiya', 'contract_code', 'current_amount', 'loan_demand',
                'rlk'
                    )
        else:
            return []

    # def save_models(self):
    #     request = self.request
    #     instance = self.new_obj
    #     instance.save()
    #     lu = instance.as_dcms_work_flow(DCMS)
    #     try:
    #         apply_info_areas = lu.apply_info().areas
    #         apply_detail = apply_info_areas['申请明细'].parse()
    #         customer_name = cleanCompanyName(apply_detail['申请人名称'][0].inner_text)
    #         customer = AccountedCompany.objects.get(name=customer_name)
    #         instance.customer = customer
    #
    #
    #
    #         instance.save(update_fields=('customer', ))
    #     except:
    #         pass
    #     if not instance.inspector:
    #         instance.inspector = request.user.user_id
    #         instance.save(update_fields=('inspector', ))

    def save_models(self):
        request = self.request
        instance = self.new_obj
        need_scrape = not bool(instance.add_date)
        instance.save()
        lu_detail = {}
        if need_scrape:
            dcms = DcmsHttpRequest()
            dcms.login()
            lu = instance.lu_num
            try:
                lu_detail = LuLedger.getSingleLuDetailFromDcms(lu, dcms)
            except:
                pass
        if instance.inspector is None:
            lu_detail['inspector'] = request.user.user_id
        LuLedger.objects.filter(pk=instance.pk).update(**lu_detail)


class LuLedgerForExportAdmin():
    list_display = ('_vf_inspector_name', '_vf_reply_code', )


class CpLedgerAdmin:
    list_display = ('cp_num', 'customer', 'reply_date', 'expire_date', 'is_special')
    list_filter = ('reply_date', 'expire_date', 'is_approved', 'cp_type', 'is_special')
    search_fields = ('cp_num', 'customer__name')


class DailyLeiShouAdmin:
    list_display = ('add_date', 'customer', 'contract_code', 'retract_amount', 'retract_date', 'dcms_business')
    list_filter = ('retract_date',)
    search_fields = ('contract_code', 'customer')

xadmin.site.register(LuLedger, LuLedgerAdmin)
xadmin.site.register(LuLedgerForExport, LuLedgerForExportAdmin)
xadmin.site.register(CpLedger, CpLedgerAdmin)
xadmin.site.register(DailyLeiShou, DailyLeiShouAdmin)
