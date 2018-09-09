import re
from django.forms import ModelForm
from django import forms
from django.shortcuts import reverse
from django.db.models import F
from MySite import utilities
from . import models
from root_db import models as rd_m


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
        self.fields['pre_approver'] = forms.ModelChoiceField(label=self.Meta.model.pre_approver.field.verbose_name, queryset=jgbs7_staff)
        self.fields['approver'] = forms.ModelChoiceField(label=self.Meta.model.approver.field.verbose_name, queryset=jgbs7_staff)
        self.fields['reply_date'].widget = forms.DateInput(attrs={'type': 'date'})


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
    remark = forms.CharField(label='备注', required=False, widget=forms.Textarea(attrs={'rows': 5}))

    class Meta:
        model = models.ProjectRepository
        fields = ('id', 'close_reason', 'whose_matter', )

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        project_id = self.instance.id
        remark_id, remark_content = models.ProjectExecution.objects.filter(project_id=project_id).order_by('-id').values_list('remark__id', 'remark__content')[0]
        self.fields['remark'].initial = remark_content


class ProjectExeForm_update(ModelForm):

    class Meta:
        model = models.ProjectExecution
        fields = ['id']

    def __init__(self, *args, **kwargs):
        super(ProjectExeForm_update, self).__init__(*args, **kwargs)
        self.fields['id'] = forms.CharField(widget=forms.TextInput(attrs={'hidden': 'hidden', 'readonly': 'readonly'}))
        if not self.data:
            if self.instance.current_progress.status_num < 100:
                self.fields['current_progress'] = forms.ModelChoiceField(
                    label=self.Meta.model.current_progress.field.verbose_name,
                    widget=forms.Select(), queryset=models.Progress.getSuitableProgressQsForSubbusiness(self.instance.project.business.id),
                    initial=self.instance.current_progress
                )
            else:
                self.fields['total_used'] = forms.IntegerField(
                    label='项目总计投放净额',
                    initial=self.instance.total_used
                )
            self.fields['remark'] = forms.CharField(
                label=self.Meta.model.remark.field.verbose_name,
                widget=forms.Textarea(),
                initial=self.instance.remark.content if self.instance.remark else '',
            )



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
