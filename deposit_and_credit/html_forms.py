from django import forms
from django.shortcuts import reverse
from deposit_and_credit import models
from app_customer_repository import models as cr_m
from root_db import models as rd_m


class ExpirePromptModelForm(forms.ModelForm):
    pk = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly', 'hidden': 'hidden'}))

    class Meta:
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
        )
        model = models.ExpirePrompt

    def __init__(self, *args, **kwargs):
        super(ExpirePromptModelForm, self).__init__(*args, **kwargs)
        self.fields['staff_id'].widget = forms.Select(choices=(), attrs={'select2': '', 'href': reverse('ajaxStaff'), 'src_type': 'static', 'init_value': self.instance.staff_id_id})
        self.fields['remark'].widget = forms.Textarea(attrs={'rows': 3})
        self.fields['expire_date'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['chushen'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['reply'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['current_progress'] = forms.ModelChoiceField(label=self.Meta.model.current_progress.field.verbose_name, queryset=cr_m.Progress.objects.filter(suit_for_business__caption='一般授信'))
        self.fields['pk'].initial = self.instance.id
        jgbs7_staff = rd_m.Staff.objects.filter(sub_department='JGBS-7')
        self.fields['pre_approver'] = forms.ModelChoiceField(label=self.Meta.model.pre_approver.field.verbose_name, queryset=jgbs7_staff)
        self.fields['approver'] = forms.ModelChoiceField(label=self.Meta.model.approver.field.verbose_name, queryset=jgbs7_staff)
