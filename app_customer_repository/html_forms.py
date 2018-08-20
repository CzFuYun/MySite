import re
from django.forms import Form, widgets, fields, ModelForm
from django import forms
from django.shortcuts import reverse
from django.db.models import F
from MySite import utilities
from . import models
from root_db import models as rd_m





# class ProjectForm(Form):
#     customer = fields.CharField(
#         label='客户名称',
#         widget=widgets.TextInput(attrs={'id': 'customer_name', 'name': 'customer_name', 'class': 'form-control'}),
#         required=True,
#         error_messages={'required': '不能为空'},
#         )
#     staff = fields.CharField(
#         label='客户经理',
#         widget=widgets.TextInput(attrs={'id': 'staff', 'name': 'staff', 'class': 'form-control'}),
#         required=True,
#         error_messages={'required': '不能为空'},
#     )
#     is_green = fields.BooleanField(
#         label='绿色金融',
#         widget=widgets.NullBooleanSelect(),
#         required=True,
#         error_messages={'required': '必选'},
#         # initial=0,
#     )
#     business = fields.CharField(
#
#     )
#     plan_pretrial = fields.DateField(
#         label='计划预审',
#         widget=widgets.DateInput(attrs={'id': 'plan_pretrial', 'name': 'plan_pretrial', 'class': 'form-control', 'type': 'date'}),
#     )
#     plan_chushen = fields.DateField(
#         label='计划初审',
#         widget=widgets.DateInput(attrs={'id': 'plan_chushen', 'name': 'plan_chushen', 'class': 'form-control', 'type': 'date'}),
#     )
#     plan_zhuanshen = fields.DateField(
#         label='计划专审',
#         widget=widgets.DateInput(attrs={'id': 'plan_zhuanshen', 'name': 'plan_zhuanshen', 'class': 'form-control', 'type': 'date'}),
#     )
#     plan_xinshen = fields.DateField(
#         label='计划信审',
#         widget=widgets.DateInput(attrs={'id': 'plan_xinshen', 'name': 'plan_xinshen', 'class': 'form-control', 'type': 'date'}),
#     )
#     plan_reply = fields.DateField(
#         label='计划批复',
#         widget=widgets.DateInput(attrs={'id': 'plan_reply', 'name': 'plan_reply', 'class': 'form-control', 'type': 'date'}),
#     )
#     plan_luodi = fields.DateField(
#         label='计划落地',
#         widget=widgets.DateInput(attrs={'id': 'plan_luodi', 'name': 'plan_luodi', 'class': 'form-control', 'type': 'date'}),
#     )
#
#     def __init__(self, *args, **kwargs):
#         super(ProjectForm, self).__init__(*args, **kwargs)
#         self.fields['business'] = forms.CharField(
#             label='业务品种',
#             required=True,
#             error_messages={'required': '不能为空'},
#             widget=widgets.Select(choices=models.SubBusiness.objects.values_list('id', 'caption'), attrs={'class': "form-control"})
#         )


class ProjectModelForm(ModelForm):

    class Meta:
        model = models.ProjectRepository
        fields = [
            'customer',
            'project_name',
            'staff',
            'business',
            'is_green',
            'total_net',
            'existing_net',
            'is_defuse',
            'is_pure_credit',
            'plan_pretrial_date',
            'plan_chushen',
            'plan_zhuanshen',
            'plan_xinshen',
            'plan_reply',
            'plan_luodi'
        ]
        # widgets = {
        #     'customer': forms.TextInput(),
        #     'staff': forms.Select(choices=rd_m.Staff.getBusinessDeptStaff()),
        #     'is_green': forms.RadioSelect(choices=utilities.yes_or_no_choices, attrs={'type': 'radio'})
        # }

    def __init__(self, *args, **kwargs):
        super(ProjectModelForm, self).__init__(*args, **kwargs)
        self.fields['customer'].widget = forms.Select(choices=(), attrs={'select2': '', 'href': reverse('ajaxCustomer'), 'src_type': 'dynamic'})
        self.fields['project_name'].widget = forms.TextInput()
        self.fields['staff'].widget = forms.Select(choices=(), attrs={'select2': '', 'href': reverse('ajaxStaff'), 'src_type': 'static'})
        self.fields['is_green'].widget = forms.RadioSelect(choices=utilities.yes_no_choices)
        self.fields['is_defuse'].widget = forms.RadioSelect(choices=utilities.yes_no_choices)
        self.fields['is_pure_credit'].widget = forms.RadioSelect(choices=utilities.yes_no_choices)
        self.fields['plan_pretrial_date'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['plan_chushen'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['plan_zhuanshen'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['plan_xinshen'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['plan_reply'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['plan_luodi'].widget = forms.DateInput(attrs={'type': 'date'})
        utilities.setRequiredFields(self)


class ProjectModelForm_set_replied(ModelForm):
    id = forms.CharField(widget=forms.TextInput(attrs={'hidden': 'hidden', 'readonly': 'readonly'}))

    class Meta:
        model = models.ProjectRepository
        fields = ('id', 'cp_con_num', 'pre_approver', 'approver', 'total_net', 'reply_content', 'reply_date')

    def __init__(self, *args, **kwargs):
        super(ProjectModelForm_set_replied, self).__init__(*args, **kwargs)
        jgbs7_staff = rd_m.Staff.objects.filter(sub_department='JGBS-7')
        self.fields['pre_approver'] = forms.ModelChoiceField(label=self.Meta.model.pre_approver.field.verbose_name,queryset=jgbs7_staff)
        self.fields['approver'] = forms.ModelChoiceField(label=self.Meta.model.approver.field.verbose_name,queryset=jgbs7_staff)
        # utilities.setRequiredFields(self)


class CustomerModelForm_add(ModelForm):

    class Meta:
        model = models.CustomerRepository
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CustomerModelForm_add, self).__init__(*args, **kwargs)
        self.fields['customer'].widget = forms.Select(choices=())
        self.fields['is_strategy'].widget = forms.RadioSelect(choices=utilities.yes_no_choices)

    # def clean_credit_file(self):
    #     '''
    #     验证credit_file是否合法
    #     :return:
    #     '''
    #     cf = self.cleaned_data['credit_file']
    #     if cf:
    #         reg = re.compile(r'^CF\d{4}/\d{5,6}$')
    #         if reg.match(cf):
    #             return cf
    #         else:
    #             raise forms.ValidationError('信贷文件编号格式错误', code='cf_invalid')
    #     else:
    #         return cf

    def clean_name(self):
        name = self.cleaned_data['name']
        if models.CustomerRepository.objects.filter(name=name).exists():
            raise forms.ValidationError('该客户已存在', code='name_invalid')
        else:
            return name


class ProjectModelForm_del(ModelForm):
    id = forms.CharField(widget=forms.TextInput(attrs={'hidden': 'hidden', 'readonly': 'readonly'}))

    class Meta:
        model = models.ProjectRepository
        fields = ('id', 'close_reason', 'whose_matter', )


class ProjectExeForm_update(ModelForm):


    class Meta:
        model = models.ProjectExecution
        fields = ['id', 'current_progress', 'project']

    def __init__(self, *args, **kwargs):
        super(ProjectExeForm_update, self).__init__(*args, **kwargs)
        self.fields['id'] = forms.CharField(widget=forms.TextInput(attrs={'hidden': 'hidden', 'readonly': 'readonly'}))
        self.fields['remark'] = forms.CharField(
            label=self.Meta.model.remark.field.verbose_name,
            widget=forms.Textarea(),
            initial=self.instance.remark.content if self.instance.remark else '',
        )
        self.fields['current_progress'].widget = forms.Select(choices=models.Progress.getSuitableProgressForSubbusiness(self.instance.project.business.id))


# class ProjectExeForm_update(Form):
#     id = forms.CharField(widget=forms.TextInput(attrs={'hidden': 'hidden', 'readonly': 'readonly'}))
#     current_progress = forms.ChoiceField(label=models.ProjectExecution.current_progress.field.verbose_name)
#     remark = forms.CharField(widget=forms.Textarea())
#
#     def __init__(self, instance):
#         super(ProjectExeForm_update, self).__init__()
#         self.model = models.ProjectExecution
#         self.fields['current_progress'].initial = str(instance.current_progress)
#         self.fields['remark'].initial = str(instance.remark.content)
#         # self.id.initial = instance.id
#
