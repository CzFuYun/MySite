import re

from dcms_shovel import connection, customer, page_parser


def get_cp_progress_id(dcms, cp_num, cf=None):
    # 更新非特别授信系统进度
    progress_id = 0
    result = dcms.search_work_flow(cp_num)
    result.click_into()
    result.click_label('工作流')
    dcms.switch_to_application_frame()
    page = page_parser.DcmsWebPage(dcms.browser.page_source, dcms.active_frame_path)
    progresses = page.lists[0].parse_to_dict_list()
    last_progress = progresses[-1]['接受状态'].split('\n')[0].strip()
    progress_reflector = {
        '授信申请建档': 40,
        '待地区审查': _judge_preliminary_progress,
        '待风险审查': 75,
        '待地区信审会审批': 90,
        '待地区CCRO推荐': 100,
        ('授信已批准', '批准条件', '条件待校验', '条件待校验', '待条件待确认', '已符合条件', '条件已落实'): 105,
        '已关闭': _judge_closed_cp_approve_status,
        '续议': 104,
        '否决': 103,
        '退回补充材料': _judge_regressed_cp_progress
    }
    for key, value in progress_reflector.items():
        if last_progress in key:
            progress_id = value if type(value) == int else value(progresses)
            break
    return progress_id


def get_cp_num(dcms, customer_name):
    cp_num = None
    dcms.search_customer(customer_name)
    cust = dcms.search_customer(customer_name)
    cust.go_to_cf_label('授信申请')
    dcms.switch_to_main_frame()
    dcms.switch_to_body_frame()
    page = page_parser.DcmsWebPage(dcms.browser.page_source, dcms.active_frame_path)
    cp_list = page.lists[0].parse_to_tag_dict_list()
    for cp in cp_list:
        seemly_cp_num = cp['授信申请参考编号'].text.strip()
        if cp['状态'].text.strip() not in ('已取消', '已关闭') and (seemly_cp_num.startswith('CP/') or seemly_cp_num.startswith('SME/')):
            rlk = re.findall(r'[A-Z0-9]{32}', str(cp['序号']))[0]
            dcms.browser.execute_script(
                'window.open("http://110.17.1.21:9082/dcms/corporate/application/application_info.view?do=Summary&resultLinkKey={0}")'.format(rlk))
            cp_num_check = int(input('【' + seemly_cp_num + '】号授信流程是否符合要求？\n0.否\n1.是\n>>>'))
            if cp_num_check:
                cp_num = seemly_cp_num
            dcms.browser.close()
            dcms.browser.switch_to_window(dcms.browser.window_handles[0])
    return cp_num


def _judge_preliminary_progress(work_flow_dict_list):
    '''
    判断初审次数
    :param work_flow_dict_list:
    :return:
    '''
    count = 0
    for i in work_flow_dict_list:
        if i['接受状态'].strip() in '待地区审查':
            count += 1
    if count == 1:
        return 45
    elif count == 2:
        return 55
    elif count > 2:
        return 65


def _judge_closed_cp_approve_status(work_flow_dict_list):
    last_2_progress = work_flow_dict_list[-2]['接受状态'].strip()
    if last_2_progress in ('授信已批准', '批准条件', '已符合条件'):
        return 105
    elif last_2_progress in '续议':
        return 104
    elif last_2_progress in '否决':
        return 103
    else:
        return 0


def _judge_regressed_cp_progress(work_flow_dict_list):
    '''
    判断退改授信的进度
    :param work_flow_dict_list:
    :return:
    '''
    last_2_progress = work_flow_dict_list[-2]['接受状态'].strip()
    if last_2_progress in '待风险审查':
        return 80
    elif last_2_progress in '待地区审查':
        regress_count = 0
        for i in work_flow_dict_list:
            if i['接受状态'] in '待地区审查':
                regress_count += 1
        if regress_count == 1:
            return 50
        elif regress_count == 2:
            return 60
        elif regress_count > 2:
            return 70
    else:
        return 0