from deposit_and_credit import models

expire_table = [
    {
        'index': None,
        'col_name': '#',
        'width': '2%',
        'td_attr': {
            'expire_id': 'id',
        }
    },
    {
        'index': 'customer__name',
        'col_name': models.ExpirePrompt._meta.get_field('customer').verbose_name,
        'width': '13%',
        'td_attr': {
            'customer_id': 'customer_id'
        }
    },
    {
        'index': 'staff_id__sub_department__superior__caption',
        'col_name': '经营单位',
        'width': '4%',
        'td_attr': {
            # 'dept_code': 'staff_id__sub_department__superior__code',
        }
    },
    {
        'index': 'staff_id__name',
        'col_name': models.ExpirePrompt._meta.get_field('staff_id').verbose_name,
        'width': '4%',
        'td_attr': {
            'staff_id': 'staff_id',
            'yr_card': 'staff_id__yellow_red_card',
            'red_card_expire_date': 'staff_id__red_card_expire_date',
        }
    },
    {
        'index': 'expire_date',
        'col_name': models.ExpirePrompt._meta.get_field('expire_date').verbose_name,
        'width': '5%',
        'td_attr': {}
    },
    {
        'index': 'chushen',
        'col_name': models.ExpirePrompt._meta.get_field('chushen').verbose_name,
        'width': '5%',
        'td_attr': {}
    },
    {
        'index': 'reply',
        'col_name': models.ExpirePrompt._meta.get_field('reply').verbose_name,
        'width': '5%',
        'td_attr': {}
    },
    {
        'index': 'current_progress__caption',
        'col_name': models.ExpirePrompt._meta.get_field('current_progress').verbose_name,
        'width': '4%',
        'td_attr': {
            'status_num': 'current_progress__status_num',
        }
    },
    {
        'index': 'punishment',
        'col_name': models.ExpirePrompt._meta.get_field('punishment').verbose_name,
        'width': '5%',
        'td_attr': {}
    },
    {
        'index': 'remark',
        'col_name': '备注',
        'width': '25%',
        'td_attr': {}
    },
    {
        'index': 'finish_date',
        'col_name': models.ExpirePrompt._meta.get_field('finish_date').verbose_name,
        'width': '4%',
        'td_attr': {}
    }
]
