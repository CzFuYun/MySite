from django.forms import Form, widgets, fields, ModelForm
from django import forms
from django.db.models import F
from . import models
from root_db import models as rd_m


YES_OR_NO = ((1, '是'), (0, '否'),)

class ProjectForm(Form):
    customer = fields.CharField(
        label='客户名称',
        widget=widgets.TextInput(attrs={'id': 'customer_name', 'name': 'customer_name', 'class': 'form-control'}),
        required=True,
        error_messages={'required': '不能为空'},
        )
    staff = fields.CharField(
        label='客户经理',
        widget=widgets.TextInput(attrs={'id': 'staff', 'name': 'staff', 'class': 'form-control'}),
        required=True,
        error_messages={'required': '不能为空'},
    )
    is_green = fields.ChoiceField(
        label='绿色金融',
        widget=widgets.RadioSelect(attrs={'id': 'is_green', 'name': 'is_green', 'type': 'radio'}),
        choices=((1, '是'), (0, '否'),),
        required=True,
        error_messages={'required': '必选'},
        # initial=0,
    )
    business = fields.CharField(

    )
    plan_pretrial = fields.DateField(
        label='计划预审',
        widget=widgets.DateInput(attrs={'id': 'plan_pretrial', 'name': 'plan_pretrial', 'class': 'form-control', 'type': 'date'}),
    )
    plan_chushen = fields.DateField(
        label='计划初审',
        widget=widgets.DateInput(attrs={'id': 'plan_chushen', 'name': 'plan_chushen', 'class': 'form-control', 'type': 'date'}),
    )
    plan_zhuanshen = fields.DateField(
        label='计划专审',
        widget=widgets.DateInput(attrs={'id': 'plan_zhuanshen', 'name': 'plan_zhuanshen', 'class': 'form-control', 'type': 'date'}),
    )
    plan_xinshen = fields.DateField(
        label='计划信审',
        widget=widgets.DateInput(attrs={'id': 'plan_xinshen', 'name': 'plan_xinshen', 'class': 'form-control', 'type': 'date'}),
    )
    plan_reply = fields.DateField(
        label='计划批复',
        widget=widgets.DateInput(attrs={'id': 'plan_reply', 'name': 'plan_reply', 'class': 'form-control', 'type': 'date'}),
    )
    plan_luodi = fields.DateField(
        label='计划落地',
        widget=widgets.DateInput(attrs={'id': 'plan_luodi', 'name': 'plan_luodi', 'class': 'form-control', 'type': 'date'}),
    )

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['business'] = forms.CharField(
            label='业务品种',
            required=True,
            error_messages={'required': '不能为空'},
            widget=widgets.Select(choices=models.SubBusiness.objects.values_list('id', 'caption'), attrs={'class': "form-control"})
        )

# class BusinessModelForm(ModelForm):
#
#
#     def __init__(self, *args, **kwargs):
#         super(BusinessModelForm, self).__init__(*args, **kwargs)
#
#     class Meta:
#         model = models.Business
#         # exclude = ()
#         fields = '__all__'

class ProjectModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProjectModelForm, self).__init__(*args, **kwargs)
        self.fields['customer'].widget = forms.TextInput()
        # self.fields['customer'].required = True
        self.fields['project_name'].widget = forms.TextInput()
        # self.fields['staff'].choices = rd_m.Staff.getBusinessDeptStaff()
        self.fields['staff'].widget = forms.TextInput()
        self.fields['business'].choices = models.SubBusiness.getAllBusiness()
        self.fields['is_green'].widget = forms.RadioSelect(choices=YES_OR_NO)
        self.fields['is_defuse'].widget = forms.RadioSelect(choices=YES_OR_NO)
        self.fields['is_pure_credit'].widget = forms.RadioSelect(choices=YES_OR_NO)
        self.fields['plan_pretrial_date'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['plan_chushen'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['plan_zhuanshen'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['plan_xinshen'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['plan_reply'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['plan_luodi'].widget = forms.DateInput(attrs={'type': 'date'})



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
        #     'is_green': forms.RadioSelect(choices=YES_OR_NO, attrs={'type': 'radio'})
        # }

