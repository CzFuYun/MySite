import collections


viewProjectSummary_values = (

)

trackProjectExe_fields = [
    'id',
    'project_id',
    'project__customer__name',
    'project__staff__sub_department__superior__caption',
    'project__staff__sub_department__superior__code',
    'project__staff__name',
    'project__staff_id',
    'project__staff__yellow_red_card',
    'project__business__caption',
    'project__is_focus',
    'current_progress__status_num',
    'current_progress__caption',
    'project__total_net',
    'project__existing_net',
    'new_net_used',
    'remark__content',
    'project__customer__customer_id',
    'current_progress__star__caption',
    'project__plan_pretrial_date',
    'project__plan_chushen',
    'project__plan_zhuanshen',
    'project__plan_xinshen',
    'project__plan_reply',
    'project__reply_date',
    'project__pre_approver__name',
    'project__pre_approver__staff_id',
    'project__approver__name',
    'project__approver__staff_id',
    'remark__create_date',
    'project__pretrial_doc__meeting__meeting_date',
    'project__total_net',
]


trackProjectExe_table_col = {
    'row_num': {
        'col_name': '#',
        'width': '2%',
        'td_attr': {
            'exe_id': 'id',
            'project_id': 'project_id',
        }
    },
    'project__customer__name': {
        'col_name': '客户名称',
        'width': '10%',
        'td_attr': {
            'customer_id': 'project__customer__customer_id'
        }
    },
    'project__staff__sub_department__superior__caption': {
        'col_name': '经营单位',
        'width': '3%',
        'td_attr': {
            'dept_code': 'project__staff__sub_department__superior__code',
        }
    },
    'project__staff__name': {
        'col_name': '客户经理',
        'width': '3%',
        'td_attr': {
            'staff': 'project__staff_id',
            'yr_card': 'project__staff__yellow_red_card',
        }
    },
    'project__business__caption': {
        'col_name': '业务种类',
        'width': '3%',
        'td_attr': {
            # 'sub_business': 'business_id'
        }
    },
    'project__total_net': {
        'col_name': '金额',
        'width': '3%',
    },
    'project__pretrial_doc__meeting__meeting_date': {
        'col_name': '预审日期',
        'width': '4%',
        'td_attr': {}
    },
    'current_progress__caption': {
        'col_name': '目前进度',
        'width': '4%',
        'td_attr': {
            'status_num': 'current_progress__status_num',
            'total_net': 'project__total_net',
            'existing_net': 'project__existing_net',
            'new_net_used': 'new_net_used',
            # 'plan_20': 'project__plan_pretrial_date',
            # 'plan_40': 'project__plan_chushen',
            # 'plan_70': 'project__plan_zhuanshen',
            # 'plan_80': 'project__plan_xinshen',
            # 'plan_100': 'project__plan_reply',
            # 'plan_120': 'project__plan_luodi',
        }
    },
    'project__plan_chushen': {
        'col_name': '计划初审',
        'width': '4%',
        'td_attr': {
            '!plan': 40
        },
    },
    'project__plan_zhuanshen': {
        'col_name': '计划专审',
        'width': '4%',
        'td_attr': {
            '!plan': 70
        },
    },
    'project__plan_xinshen': {
        'col_name': '计划信审',
        'width': '4%',
        'td_attr': {
            '!plan': 80
        },
    },
    'project__plan_reply': {
        'col_name': '计划获批',
        'width': '4%',
        'td_attr': {
            '!plan': 100
        },
    },
    'project__reply_date': {
        'col_name': '批复日',
        'width': '4%',
        'td_attr': {
            # 'plan_120': None
        },
    },
    'remark__content': {
        'col_name': '备注',
        'width': '12%',
        'td_attr': {'title': 'remark__create_date'}
    }
}

downloadProjectList_col_part1 = {
    'id': '项目id',
    'customer__name': '项目主体',
    'customer__industry__caption': '行业门类',
    'customer__type_of_3311__level': '3311类型',
    'is_green': '绿色金融',
    'staff__sub_department__superior__caption': '经营部门',
    'staff__name': '主办人员',
    'business__superior__caption': '业务大类',
    'business__caption': '具体业务',
    'pretrial_doc__meeting__meeting_date': '预审日期',
    'total_net': '总敞口',
    'existing_net': '存量敞口',
    'projectexecution__current_progress__caption': '当前进度',
    'projectexecution__current_progress__status_num': '进度代号',
    'reply_date': '批复日期',
    'projectexecution__new_net_used': '新增敞口投放',
    'is_defuse': '涉及化解',
    'account_num': '折算户数',
    'projectexecution__remark__content': '备注',
    'is_focus': '重点项目',
    'is_specially_focus': '重点跟进',
    'tmp_close_date': '临时关闭日期',
    'plan_chushen': '计划到初审',
    'plan_zhuanshen': '计划到专审',
    'plan_xinshen': '计划到信审会',
    'plan_reply': '计划获批',
    'plan_luodi': '计划落地',
    'pretrial_doc__stockholder': '控股方',
    'projectexecution__photo_date': '快照日期',
}

downloadProjectList_col_part2 = {
    'customer__contributor__loan_rate': '贷款利率',
    'customer__dividedcompanyaccount__divided_amount__sum': '存款余额',
    'customer__dividedcompanyaccount__divided_yd_avg__sum': '存款日均',
}