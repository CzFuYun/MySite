import xadmin

from .models import Staff, AccountedCompany, SubDepartment


class StaffAdmin:
    list_display = ['staff_id', 'name', 'sub_department']
    ordering = ['sub_department__superior__display_order', 'sub_department', 'name']
    relfield_style = 'fk-ajax'
    search_fields = ['staff_id', 'name', 'sub_department__caption']
    list_filter = ['staff_id', 'name']


class AccountedCompanyAdmin:
    relfield_style = 'fk-ajax'
    list_filter = ('customer_type__caption', 'type_of_3311__caption')
    search_fields = ('name', 'series__caption')


class SubDepartmentAdmin:
    relfield_style = 'fk-ajax'


xadmin.site.register(Staff, StaffAdmin)
xadmin.site.register(AccountedCompany, AccountedCompanyAdmin)
xadmin.site.register(SubDepartment, SubDepartmentAdmin)