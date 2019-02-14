# from django.db.models import Sum

import xadmin

from .models import LuLedger


class LuLedgerAdmin:
    list_display = ('lu_num', 'lend_date')


xadmin.site.register(LuLedger, LuLedgerAdmin)