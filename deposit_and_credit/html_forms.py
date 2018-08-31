from django import forms
from deposit_and_credit import models


class ExpirePromptModelForm(forms.ModelForm):

    class Meta:
        exclude = ('customer', 'finish_date', 'created_at',)
        model = models.ExpirePrompt

    def __init__(self, *args, **kwargs):
        super(ExpirePromptModelForm, self).__init__(*args, **kwargs)
