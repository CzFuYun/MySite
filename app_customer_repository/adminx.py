import xadmin
from xadmin import views

from .models import CustomerRepository, ProjectRepository, PretrialDocument, PretrialMeeting


class CustomerAdmin:
    pass


class ProjectAdmin:
    list_display = ('customer', 'staff', 'tmp_close_date', 'close_reason', )
    # search_fields = ['staff__name']


class PretrialDocumentAdmin:
    list_display = ('customer_name', 'department', 'accept_date', 'reason', 'net_total', 'agree_net', 'result', 'meeting', )
    list_per_page = 20
    list_filter = ('meeting__caption', 'meeting__meeting_date', 'reason', )
    search_fields = ('customer_name',)
    # list_export_fields = ('', '',)


class PretrialMeetingAdmin:
    list_display = ('caption', 'meeting_date', )
    list_per_page = 20


xadmin.site.register(CustomerRepository, CustomerAdmin)
xadmin.site.register(ProjectRepository, ProjectAdmin)
xadmin.site.register(PretrialDocument, PretrialDocumentAdmin)
xadmin.site.register(PretrialMeeting, PretrialMeetingAdmin)