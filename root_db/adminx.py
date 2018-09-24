import xadmin

from .models import Staff


class StaffAdmin:
    list_display = ['staff_id', 'name', 'sub_department']
    ordering = ['sub_department__superior__display_order', 'sub_department', 'name']
    relfield_style = 'fk-ajax'
    search_fields = ['name']


xadmin.site.register(Staff, StaffAdmin)