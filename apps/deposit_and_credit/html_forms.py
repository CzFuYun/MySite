from django import forms
from django.shortcuts import reverse
from deposit_and_credit import models
from app_customer_repository import models as cr_m
from root_db import models as rd_m
from deposit_and_credit.models_operation import DateOperation

JGBS7_STAFFS = rd_m.Staff.objects.filter(sub_department='JGBS-7')
PROGRESS = cr_m.Progress.objects.filter(id__in=(0, 20, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 98, 99, 100, 104, 105))

class ExpirePromptModelForm(forms.ModelForm):
    pk = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly', 'hidden': 'hidden'}))

    class Meta:
        model = models.ExpirePrompt
        fields = (
            'staff_id',
            'expire_date',
            'apply_type',
            'chushen',
            'reply',
            'current_progress',
            'cp_num',
            'remark',
            'punishment',
            'pre_approver',
            'approver',
            'approve_date',
            'finish_date',
        )
        widgets = {
            'remark': forms.Textarea(attrs={'rows': 3}),
            'expire_date': forms.DateInput(attrs={'type': 'date'}),
            'chushen': forms.DateInput(attrs={'type': 'date'}),
            'reply': forms.DateInput(attrs={'type': 'date'}),
            'approve_date': forms.DateInput(attrs={'type': 'date'}),
            'finish_date': forms.DateInput(attrs={'type': 'date', 'hidden': 'hidden'}),
        }

    def __init__(self, *args, **kwargs):
        super(ExpirePromptModelForm, self).__init__(*args, **kwargs)
        self.fields['pk'].initial = self.instance.id
        self.fields['staff_id'].widget = forms.Select(choices=(), attrs={'select2': '', 'href': reverse('ajaxStaff'), 'src_type': 'static', 'init_value': self.instance.staff_id_id})
        self.fields['current_progress'] = forms.ModelChoiceField(label=self.Meta.model.current_progress.field.verbose_name, queryset=PROGRESS, required=False)
        self.fields['pre_approver'] = forms.ModelChoiceField(label=self.Meta.model.pre_approver.field.verbose_name, queryset=JGBS7_STAFFS, required=False)
        self.fields['approver'] = forms.ModelChoiceField(label=self.Meta.model.approver.field.verbose_name, queryset=JGBS7_STAFFS, required=False)

    def clean_punishment(self):
        n = self.cleaned_data['punishment']
        if n < 0:
            raise forms.ValidationError('不可为负值', code='punishment_invalid')
        else:
            return n

    def clean_approve_date(self):
        imp_date = DateOperation()
        n = self.cleaned_data['approve_date']
        require_reply_date = imp_date.month_dif(-1, self.cleaned_data['expire_date'])
        self.require_reply_limit_date = imp_date.month_last_date(require_reply_date.year, require_reply_date.month)
        if n:
            if self.cleaned_data['current_progress'].status_num < 95:
                self.cleaned_data['current_progress'] = cr_m.Progress.objects.get(id=105)
            if n > self.require_reply_limit_date:
                if not self.cleaned_data['punishment']:
                    self.cleaned_data['punishment'] = 1
        return n

    # def clean_finish_date(self):
    #     n = self.cleaned_data['finish_date']
    #     if n:
    #         return n
    #     else:
    #         pass