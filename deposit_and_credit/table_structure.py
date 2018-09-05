import collections, json
from MySite.utilities import field_choices_to_dict
from MySite import utilities
from deposit_and_credit import models


expire_table = {
    'row_num':
        {
            'col_name': '#',
            'width': '2%',
            'td_attr': {'expire_id': 'id'}
        },
    'customer__name':
        {
            'col_name': models.ExpirePrompt._meta.get_field('customer').verbose_name,
            'width': '15%',
            'td_attr': {'customer_id': 'customer_id'}
        },
    'staff_id__sub_department__superior__caption':
        {
            'col_name': '经营单位',
            'width': '4%',
            'td_attr': {'dept_code': 'staff_id__sub_department__superior__code'}
        },
    'staff_id__name':
        {
            'col_name': models.ExpirePrompt._meta.get_field('staff_id').verbose_name,
            'width': '4%',
            'td_attr': {'staff_id': 'staff_id', 'yr_card': 'staff_id__yellow_red_card', 'red_card_expire_date': 'staff_id__red_card_expire_date'}
        },
    'expire_date':
        {
            'col_name': models.ExpirePrompt._meta.get_field('expire_date').verbose_name,
            'width': '4%',
            'td_attr': {'expire_date': None}
        },
    'apply_type':
        {
            'col_name': models.ExpirePrompt._meta.get_field('apply_type').verbose_name,
            'width': '2%',
            'td_attr': {'choice_to_display': field_choices_to_dict(models.ExpirePrompt.apply_type_choices, False)}
        },
    'chushen':
        {
            'col_name': models.ExpirePrompt._meta.get_field('chushen').verbose_name,
            'width': '4%',
            'td_attr': {'plan_chushen': ''}
        },
    'reply':
        {
            'col_name': models.ExpirePrompt._meta.get_field('reply').verbose_name,
            'width': '4%',
            'td_attr': {'plan_reply': ''}
        },
    'current_progress__caption':
        {
            'col_name': models.ExpirePrompt._meta.get_field('current_progress').verbose_name,
            'width': '4%',
            'td_attr': {'status_num': 'current_progress__status_num', 'title': 'progress_update_date'}
        },
    'remark':
        {
            'col_name': models.ExpirePrompt._meta.get_field('remark').verbose_name,
            'width': '25%',
            'td_attr': {'title': 'remark_update_date'}
        },
    'punishment':
        {
            'col_name': models.ExpirePrompt._meta.get_field('punishment').verbose_name,
            'width': '3%',
            'td_attr': None
        },
    'finish_date':
        {
            'col_name': models.ExpirePrompt._meta.get_field('finish_date').verbose_name,
            'width': '4%',
            'td_attr': None
        }
}


expire_table_download = collections.OrderedDict(**{
    'customer__name': '客户名称',
    'staff_id__sub_department__superior__caption': '经营部门',
    'staff_id__name': '客户经理',
    'expire_date': '到期日',
    'apply_type': '续做',
    'chushen': '预计初审日期',
    'reply': '预计批复日期',
    'current_progress__caption': '当前进度',
    'remark': '备注',
    # 'punishment': '扣罚金额',
})
expire_table_sr_for_download = {
    'apply_type': utilities.field_choices_to_dict(models.ExpirePrompt.apply_type_choices, False)
}