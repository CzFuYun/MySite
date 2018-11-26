from copy import deepcopy
from collections import namedtuple

from django.utils.safestring import mark_safe
from django.shortcuts import reverse
from django.db.models import Q
import xadmin
from xadmin import views
from xadmin.plugins.actions import BaseActionView

from MySite.settings import MEDIA_URL
from MySite.utilities import XadminExtraAction
from .models import CustomerRepository, ProjectRepository, PretrialDocument, PretrialDocumentWaitForMeeting, PretrialMeeting, ProjectExecution, Progress
from root_db.models import AccountedCompany
from MySite import utilities
from private_modules.dcms_shovel import connection
from deposit_and_credit import models_operation

def showFile(instance):
    file_name = instance.document_file.name
    if file_name:
        return mark_safe('<a href="' + MEDIA_URL + '/' + file_name + '" target="_blank">查看</a>')
    return ''


class CustomerAdmin:
    relfield_style = 'fk-ajax'


class ProjectAdmin:
    list_display = ['customer', 'staff', 'business', 'total_net', 'plan_chushen', 'plan_zhuanshen', 'plan_xinshen', 'plan_reply', 'plan_luodi', 'get_progress'
        # , 'get_total_used', 'is_specially_focus', 'show_remark', 'tmp_close_date', 'close_reason'
                    ]
    list_editable = ['plan_chushen', 'plan_zhuanshen', 'plan_xinshen', 'plan_reply', 'plan_luodi']
    search_fields = ['customer__name']
    list_filter = ['is_focus', 'is_specially_focus', 'business__superior', 'pretrial_doc__meeting__caption', 'reply_date', 'tmp_close_date']
    list_per_page = 15

    def show_remark(self, instance):
        return self.last_exe.remark.content
    show_remark.short_description = '备注'

    def get_total_used(self, instance):
        project_id = instance.id
        self.last_exe = ProjectExecution.objects.filter(project_id=project_id).order_by('-id').first()
        return self.last_exe.total_used
    get_total_used.short_description = '已投放'

    def get_progress(self, instance):
        return instance.projectexecution_set.last().current_progress
    get_progress.short_description = '目前进度'


class PreDocToNewProject(BaseActionView):
    action_name = '转化为项目储备'
    description = '转化所选的 为储备项目'
    model_perm = 'delete'
    def do_action(self, queryset):
        dcms = connection.DcmsConnection('http://110.17.1.21:9082')
        dcms.login('czfzc', 'hxb123')
        imp_date = models_operation.DateOperation()
        for pre_doc in queryset:
            if ProjectRepository.objects.filter(pretrial_doc=pre_doc).exists():
                print(str(pre_doc) + '已在项目储备库中，请核实')
                continue
            if pre_doc.agree_net - pre_doc.exist_net <= 0:
                print(str(pre_doc) + '并未新增额度，请核实')
                continue
            result_dict = utilities.field_choices_to_dict(PretrialDocument.result_choices, False)
            if not result_dict[str(pre_doc.result)].__contains__('通过'):
                print(str(pre_doc) + '并未通过预审，请核实')
                continue
            customer_name = utilities.cleanCompanyName(pre_doc.customer_name)
            customer_rep = CustomerRepository.objects.filter(name=customer_name)
            if not customer_rep.exists():
                new_customer_fields = {'department_id': None, 'type_of_3311_id': None, 'industry_id': None, 'stockholder': None}
                for key in new_customer_fields:
                    new_customer_fields[key]  = getattr(pre_doc, key)
                new_customer_fields['name'] = customer_name
                cf_num = dcms.search_customer(pre_doc.customer_name).cf_num or dcms.search_customer(customer_name).cf_num
                if cf_num:
                    cf_num = cf_num if int(input(customer_name + '信贷文件号：【' + cf_num + '】,是否正确？\n0.不正确\n1.正确')) else input('请输入正确的信贷文件编号>>>')
                else:
                    cf_num = ''
                if AccountedCompany.objects.filter(name=customer_name).exists():
                    new_customer_fields['customer_id'] = AccountedCompany.objects.get(name=customer_name).customer_id
                new_customer_fields['credit_file'] = cf_num
                new_customer_fields['is_strategy'] = bool(int(input(customer_name + '是否战略客户?\n0.否\n1.是')))
                simple_name = input('请确定【' + customer_name + '】的简称>>>')
                if CustomerRepository.objects.filter(simple_name__icontains=simple_name).exists():
                    print('请注意【' + customer_name + '】简称重复：' + simple_name)
                new_customer_fields['simple_name'] = simple_name
                customer = CustomerRepository(**new_customer_fields)
                customer.save()
            else:
                customer = customer_rep[0]
            project_fields = {'staff_id': None, 'is_green': None, 'business_id': None, 'is_defuse': None}
            for key in project_fields:
                project_fields[key] = getattr(pre_doc, key)
            project_fields['customer'] = customer
            project_fields['pretrial_doc'] = pre_doc
            project_fields['total_net'] = pre_doc.agree_net
            project_fields['existing_net'] = pre_doc.exist_net
            project_fields['plan_pretrial_date'] = imp_date.today
            plan = ('plan_chushen', 'plan_zhuanshen', 'plan_xinshen', 'plan_reply', 'plan_luodi')
            delta_days = 20 if project_fields['business_id'] > 11 else 10
            for i in range(len(plan)):
                project_fields[plan[i]] = imp_date.delta_date(delta_days * i)
            project_fields['project_name'] = input('请为【' + customer.simple_name + '】的【' + pre_doc.business.caption + '】项目命名>>>') or (customer.simple_name + pre_doc.business.caption)
            new_project = ProjectRepository(**project_fields)
            new_project.create()
            progress = Progress.objects.filter(status_num=20, suit_for_business=new_project.business)
            ProjectExecution.objects.get(project=new_project).update({'current_progress': progress})
            print(project_fields['project_name'] + '添加成功')


class PretrialDocumentAdmin:
    list_display = ['customer_name', 'department', 'accept_date', 'reason', 'net_total', 'exist_net', 'agree_net', 'result', 'meeting', 'show_file']
    list_per_page = 50
    list_filter = ['meeting__caption', 'meeting__meeting_date', 'reason']
    search_fields = ['customer_name']
    # list_export_fields = ('', '',)
    relfield_style = 'fk-ajax'
    actions = [PreDocToNewProject, ]

    def queryset(self):
        qs = super().queryset()
        return qs.filter(result__gt=10).order_by('-meeting__caption', 'order')

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
        return qs.filter((Q(order=0) | Q(meeting__meeting_date__isnull=True)) & Q(net_total__gt=0))

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