from copy import deepcopy
from collections import namedtuple

from django.utils.safestring import mark_safe
from django.shortcuts import reverse
import xadmin
from xadmin import views

from MySite.settings import MEDIA_URL
from MySite.utilities import XadminExtraAction
from .models import CustomerRepository, ProjectRepository, PretrialDocument, PretrialDocumentWaitForMeeting, PretrialMeeting
from app_permission import models


def showFile(instance):
    file_name = instance.document_file.name
    if file_name:
        return mark_safe('<a href="' + MEDIA_URL + '/' + file_name + '" target="_blank">查看</a>')
    return ''


class CustomerAdmin:
    relfield_style = 'fk-ajax'


class ProjectAdmin:
    list_display = ['customer', 'staff', 'tmp_close_date', 'close_reason']
    # search_fields = ['staff__name']


class PretrialDocumentAdmin:
    list_display = ['customer_name', 'department', 'accept_date', 'reason', 'net_total', 'agree_net', 'result', 'meeting', 'show_file']
    list_per_page = 50
    list_filter = ['meeting__caption', 'meeting__meeting_date', 'reason']
    search_fields = ['customer_name']
    # list_export_fields = ('', '',)
    relfield_style = 'fk-ajax'

    def queryset(self):
        qs = super(PretrialDocumentAdmin, self).queryset()
        return qs.filter(result__gt=10)

    def show_file(self, instance):
        return showFile(instance)
    show_file.short_description = '预审表'


class PretrialDocumentWaitForMeetingAdmin(XadminExtraAction):
    list_display = ['customer_name', 'department', 'accept_date', 'reason', 'net_total', 'show_file']
    list_per_page = 20
    list_editable = ['net_total', 'reason']
    # reversion_enable = True

    def __init__(self, *args, **kwargs):
        super(PretrialDocumentWaitForMeetingAdmin, self).__init__(*args, **kwargs)
        self.parse_extra_action({
            'voteAtPreMeeting': '投票',
            # 'submitPreDoc': '提交',
            # 'regressPreDoc': '退回',
        })

    def queryset(self):
        qs = super(PretrialDocumentWaitForMeetingAdmin, self).queryset()
        return qs.filter(result__lte=10)

    def show_file(self, instance):
        return showFile(instance)
    show_file.short_description = '预审表'


class PretrialDocumentInLine:
    model = PretrialDocument
    extra = 0


class PretrialMeetingAdmin:
    list_display = ['caption', 'meeting_date']
    list_per_page = 20
    inlines = [PretrialDocumentInLine]


xadmin.site.register(CustomerRepository, CustomerAdmin)
xadmin.site.register(ProjectRepository, ProjectAdmin)
xadmin.site.register(PretrialDocument, PretrialDocumentAdmin)
xadmin.site.register(PretrialDocumentWaitForMeeting, PretrialDocumentWaitForMeetingAdmin)
xadmin.site.register(PretrialMeeting, PretrialMeetingAdmin)