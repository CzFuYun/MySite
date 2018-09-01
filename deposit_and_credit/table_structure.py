import collections, json
from MySite.utilities import field_choices_to_dict
from deposit_and_credit import models

# expire_table = [
#     {
#         'index': None,
#         'col_name': '#',
#         'width': '2%',
#         'td_attr': {
#             'expire_id': 'id',
#         }
#     },
#     {
#         'index': 'customer__name',
#         'col_name': models.ExpirePrompt._meta.get_field('customer').verbose_name,
#         'width': '13%',
#         'td_attr': {
#             'customer_id': 'customer_id'
#         }
#     },
#     {
#         'index': 'staff_id__sub_department__superior__caption',
#         'col_name': '经营单位',
#         'width': '4%',
#         'td_attr': {
#             # 'dept_code': 'staff_id__sub_department__superior__code',
#         }
#     },
#     {
#         'index': 'staff_id__name',
#         'col_name': models.ExpirePrompt._meta.get_field('staff_id').verbose_name,
#         'width': '4%',
#         'td_attr': {
#             'staff_id': 'staff_id',
#             'yr_card': 'staff_id__yellow_red_card',
#             'red_card_expire_date': 'staff_id__red_card_expire_date',
#         }
#     },
#     {
#         'index': 'expire_date',
#         'col_name': models.ExpirePrompt._meta.get_field('expire_date').verbose_name,
#         'width': '5%',
#         'td_attr': {}
#     },
#     {
#         'index': 'chushen',
#         'col_name': models.ExpirePrompt._meta.get_field('chushen').verbose_name,
#         'width': '5%',
#         'td_attr': {}
#     },
#     {
#         'index': 'reply',
#         'col_name': models.ExpirePrompt._meta.get_field('reply').verbose_name,
#         'width': '5%',
#         'td_attr': {}
#     },
#     {
#         'index': 'current_progress__caption',
#         'col_name': models.ExpirePrompt._meta.get_field('current_progress').verbose_name,
#         'width': '4%',
#         'td_attr': {
#             'status_num': 'current_progress__status_num',
#         }
#     },
#     {
#         'index': 'punishment',
#         'col_name': models.ExpirePrompt._meta.get_field('punishment').verbose_name,
#         'width': '5%',
#         'td_attr': {}
#     },
#     {
#         'index': 'remark',
#         'col_name': '备注',
#         'width': '25%',
#         'td_attr': {}
#     },
#     {
#         'index': 'finish_date',
#         'col_name': models.ExpirePrompt._meta.get_field('finish_date').verbose_name,
#         'width': '4%',
#         'td_attr': {}
#     }
# ]


expire_table_col_index = [
    None,
    'customer__name',
    'staff_id__sub_department__superior__caption',
    'staff_id__name',
    'expire_date',
    'apply_type',
    'chushen',
    'reply',
    'current_progress__caption',
    'punishment',
    'remark',
    'finish_date'
]
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
            'td_attr': None
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
            'td_attr': None
        },
    'reply':
        {
            'col_name': models.ExpirePrompt._meta.get_field('reply').verbose_name,
            'width': '4%',
            'td_attr': None
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
