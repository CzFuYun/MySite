import xadmin

from .models import Staff, AccountedCompany, SubDepartment, DividedCompanyAccount


class StaffAdmin:
    list_display = ['staff_id', 'name', 'sub_department']
    ordering = ['sub_department__superior__display_order', 'sub_department', 'name']
    relfield_style = 'fk-ajax'
    search_fields = ['staff_id', 'name', 'sub_department__caption']
    list_filter = ['staff_id', 'name']


class AccountedCompanyAdmin:
    relfield_style = 'fk-ajax'
    list_display = ('name', 'scale', 'industry', 'customer_id', 'dcms_customer_code')
    list_filter = ('customer_type__caption', 'type_of_3311__caption', 'dcms_customer_code', 'add_date')
    search_fields = ('pk', 'name', 'series__caption', 'dcms_customer_code')


class SubDepartmentAdmin:
    list_display = ('caption', 'superior')
    relfield_style = 'fk-ajax'
    list_per_page = 100

class DividedCompanyAccountAdmin:
    list_display = ['customer', 'data_date']
    list_filter = ['data_date']
    search_fields = ['customer__name']


xadmin.site.register(Staff, StaffAdmin)
xadmin.site.register(AccountedCompany, AccountedCompanyAdmin)
xadmin.site.register(SubDepartment, SubDepartmentAdmin)
xadmin.site.register(DividedCompanyAccount, DividedCompanyAccountAdmin)