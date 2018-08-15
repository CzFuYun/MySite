import re
from django.forms import Form, widgets, fields, ModelForm
from django import forms
from django.db.models import F
from . import models
from root_db import models as rd_m


YES_OR_NO = (('1', '是'), ('0', '否'),)

def modifyFields(self, allow_null):
    for field_name in self.base_fields:
        if field_name in allow_null:
            continue
        field = self.base_fields[field_name]  # self.base_fields说白了就是把所有字段取出来
        field.required = True
        field.widget.attrs.update({'required': ''})
        if str(type(field)).find('BooleanField') >= 0:
            self.fields[field_name] = forms.IntegerField(label=field.label, widget=forms.RadioSelect(choices=YES_OR_NO))


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
    is_green = fields.BooleanField(
        label='绿色金融',
        widget=widgets.NullBooleanSelect(),
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


class ProjectModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProjectModelForm, self).__init__(*args, **kwargs)
        self.fields['customer'].widget = forms.TextInput(attrs={'list': 'customer_list'})
        # self.fields['customer'].required = True
        self.fields['project_name'].widget = forms.TextInput()
        # self.fields['staff'].choices = rd_m.Staff.getBusinessDeptStaff()
        self.fields['staff'].widget = forms.TextInput(attrs={'list': 'staff_list'})
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



class CustomerModelForm_add(forms.ModelForm):
    # is_strategy = forms.IntegerField(label='战略客户')

    class Meta:
        model = models.CustomerRepository
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CustomerModelForm_add, self).__init__(*args, **kwargs)
        # allow_null = ('customer', 'credit_file')
        self.fields['customer'].widget = forms.TextInput(attrs={'list': 'customer_list'})
        self.fields['department'].choices = rd_m.Department.getDepartments()
        self.fields['is_strategy'].widget = forms.RadioSelect(choices=YES_OR_NO)
        self.fields['type_of_3311'].choices = rd_m.TypeOf3311.get3311Type()
        # modifyFields(self, allow_null)
        # for field_name in self.base_fields:
        #     if field_name in allow_null:
        #         continue
        #     field = self.base_fields[field_name]        # self.base_fields说白了就是把所有字段取出来
        #     field.required = True
        #     field.widget.attrs.update({'required': ''})
        #     if str(type(field)).find('BooleanField') >= 0:
        #         self.fields[field_name] = forms.IntegerField(label=field.label, widget=forms.RadioSelect(choices=YES_OR_NO))

    def clean_credit_file(self):
        '''
        验证credit_file是否合法
        :return:
        '''
        cf = self.cleaned_data['credit_file']
        if cf:
            reg = re.compile(r'^CF\d{4}/\d{5,6}$')
            if reg.match(cf):
                return cf
            else:
                raise forms.ValidationError('信贷文件编号格式错误', code='cf_invalid')
        else:
            return cf

    def clean_name(self):
        name = self.cleaned_data['name']
        if models.CustomerRepository.objects.filter(name=name).exists():
            raise forms.ValidationError('该客户已存在', code='name_invalid')
        else:
            return name
