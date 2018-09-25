import xadmin

from .models import Staff, AccountedCompany


class StaffAdmin:
    list_display = ['staff_id', 'name', 'sub_department']
    ordering = ['sub_department__superior__display_order', 'sub_department', 'name']
    relfield_style = 'fk-ajax'
    search_fields = ['name']


class AccountedCompanyAdmin:
    relfield_style = 'fk-ajax'



xadmin.site.register(Staff, StaffAdmin)
xadmin.site.register(AccountedCompany, AccountedCompanyAdmin)