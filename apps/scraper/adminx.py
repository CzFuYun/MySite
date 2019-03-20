# from django.db.models import Sum

import xadmin, re

from django import forms
from xadmin.views.edit import ModelFormAdminView

from .models import LuLedger, CpLedger


class LuCreationModelForm(forms.ModelForm):
    lu_num = forms.CharField(max_length=32, label='放款参考编号')
    is_green = forms.BooleanField()

    class Meta:
        model = LuLedger
        fields = ('lu_num', 'is_green')

    def clean_lu_num(self):
        rgx_lu_num = re.compile(r'[A-Z]{2,5}/[A-Z]{2}\d{2}/\d{4}/\d{2}/\d{8}')
        if rgx_lu_num.match(self.lu_num.strip()):
            return rgx_lu_num.findall(self.lu_num.strip())[0]
        raise ValueError('非法格式的参考编号')


class LuLedgerAdmin:
    ordering = ('-add_date', '-lend_date', )
    list_display = ('lu_num', 'add_date', 'customer', 'lend_date', '_vf_reply_code', '_vf_reply_content')
    list_filter = ('lend_date', 'department', 'cp__cp_type')
    search_fields = ('customer__name', 'contract_code', 'lu_num')
    list_per_page = 20

    # add_form = LuCreationModelForm
    def get_readonly_fields(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            return (
                'inspector', 'cp', 'department', 'staff', 'customer',
                'dcms_business', 'lend_date', 'plan_expire', 'month_dif',
                'currency_type', 'lend_amount', 'rate', 'pledge_ratio',
                'float_ratio', 'net_amount', 'has_baozheng', 'has_diya',
                'has_zhiya', 'contract_code', 'current_amount', 'loan_demand',
                'rlk'
                    )
        else:
            return []

    def save_models(self):
        request = self.request
        instance = self.new_obj
        instance.save()
        instance.inspector = request.user.user_id
        instance.save(update_fields=('inspector', ))


class CpLedgerAdmin:
    list_display = ('cp_num', 'customer', 'reply_date', 'expire_date', 'is_special')
    list_filter = ('reply_date', 'expire_date', 'is_approved', 'cp_type', 'is_special')
    search_fields = ('cp_num', 'customer__name')


xadmin.site.register(LuLedger, LuLedgerAdmin)
xadmin.site.register(CpLedger, CpLedgerAdmin)

