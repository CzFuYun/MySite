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
    ordering = ('-lend_date', )
    list_display = ('lu_num', 'add_date', 'customer', 'lend_date')
    list_filter = ('lend_date', 'department', 'lu_num', 'cp__cp_type')
    search_fields = ('customer__name', 'contract_code', 'lu_num')
    list_bookmarks = [
        {
            'title': '地区',
            'query': {'cp__cp_type__contains': 'CP'},
            'cols': ('pk', ),
        }
    ]


    # add_form = LuCreationModelForm

class CpLedgerAdmin:
    list_display = ('cp_num', 'customer', 'reply_date', 'expire_date', 'is_special')
    list_filter = ('reply_date', 'expire_date')
    search_fields = ('cp_num', 'customer__name')


xadmin.site.register(LuLedger, LuLedgerAdmin)
xadmin.site.register(CpLedger, CpLedgerAdmin)

