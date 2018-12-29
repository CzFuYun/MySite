import re

from dcms_shovel import connection, customer, page_parser
from apps.deposit_and_credit.models_operation import DateOperation

rgx_rlk = re.compile(r'[A-Z0-9]{32}')


def get_cp_progress_id(dcms, cp_num, cf=None):
    # 更新非特别授信系统进度
    progress_id = 0
    event_date = None
    result = dcms.search_work_flow(cp_num)
    result.click_into()
    result.click_label('工作流')
    dcms.switch_to_application_frame()
    page = page_parser.DcmsWebPage(dcms.browser.page_source, dcms.active_frame_path)
    progresses = page.lists[0].parse_to_dict_list()
    last_progress = progresses[-1]['接受状态'].split('\n')[0].strip()
    progress_reflector = {
        '已取消': -1,
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
            if type(value) == int:
                progress_id = value
                event_date = dcms.format_date(progresses[-1]['接受日期'].strip())
            else:
                progress_id, event_date = value(progresses)
                event_date = event_date if event_date is None else dcms.format_date(event_date)
            break
    return (progress_id, event_date)


def get_cp_num(dcms, customer_name):
    imp_date = DateOperation()
    cp_num = None
    cust = dcms.search_customer(customer_name)
    cust.search_cf()
    cust.go_to_cf_label('授信申请')
    dcms.switch_to_main_frame()
    dcms.switch_to_body_frame()
    page = page_parser.DcmsWebPage(dcms.browser.page_source, dcms.active_frame_path)
    cp_list = page.lists[0].parse_to_tag_dict_list()
    for cp in cp_list:
        status = cp['状态'].text.strip()
        if status in ('已取消', ):
            continue
        seemly_cp_num = cp['授信申请参考编号'].text.strip()
        if not(seemly_cp_num.startswith('CP/') or seemly_cp_num.startswith('SME/')):
            continue
        approve_date = cp['授信批准日期'].text.strip()
        if approve_date and imp_date.date_dif(imp_date.today, approve_date) > 30:
            continue
        cp_create_date = cp['创建时间'].text.strip()
        if cp_create_date and imp_date.date_dif(imp_date.today, cp_create_date) > 180:
            continue
        purpose = cp['目的'].text.strip()
        if purpose in ('重检', ):
            continue
        rlk = rgx_rlk.findall(str(cp['序号']))[0]
        dcms.browser.execute_script(
            'window.open("http://110.17.1.21:9082/dcms/corporate/application/application_info.view?do=Summary&resultLinkKey={0}")'.format(rlk))
        dcms.browser.switch_to_window(dcms.browser.window_handles[1])
        dcms.browser.switch_to.frame(dcms.browser.find_elements_by_css_selector('frameset>frame')[1])
        dcms.browser.find_element_by_id('tab_dcms_cp_0009').click()
        dcms.browser.switch_to.frame(dcms.browser.find_element_by_css_selector('iframe'))
        if '特别授信' in dcms.browser.page_source:
            dcms.browser.switch_to_window(dcms.browser.window_handles[0])
            continue
        dcms.browser.switch_to.default_content()
        dcms.browser.switch_to.frame(dcms.browser.find_elements_by_css_selector('frameset>frame')[1])
        dcms.browser.find_element_by_id('tab_dcms_cp_0010').click()
        dcms.browser.switch_to.frame(dcms.browser.find_element_by_css_selector('iframe'))
        if '特别授信' in dcms.browser.page_source:
            dcms.browser.switch_to_window(dcms.browser.window_handles[0])
            continue
        print(customer_name + '：\n【' + str(seemly_cp_num) + '】号授信流程是否符合要求？\n0.否\n1.是')
        cp_num_check = input('>>>')
        if int(cp_num_check):
            cp_num = seemly_cp_num
        dcms.browser.switch_to_window(dcms.browser.window_handles[0])
        # dcms.browser.execute_script('window.close()')
        # dcms.browser.close()
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
        progress_id = 45
    elif count == 2:
        progress_id = 55
    else:
        progress_id = 65
    return (progress_id, None)


def _judge_closed_cp_approve_status(work_flow_dict_list):
    last_2_progress = work_flow_dict_list[-2]['接受状态'].strip()
    last_2_date_str = work_flow_dict_list[-2]['接受日期'].strip()
    if last_2_progress in ('授信已批准', '批准条件', '已符合条件'):
        progress_id = 105
    elif last_2_progress in '续议':
        progress_id = 104
    elif last_2_progress in '否决':
        progress_id = 103
    else:
        progress_id = 0
    return (progress_id, last_2_date_str)


def _judge_regressed_cp_progress(work_flow_dict_list):
    '''
    判断退改授信的进度
    :param work_flow_dict_list:
    :return:
    '''
    last_2_progress = work_flow_dict_list[-2]['接受状态'].strip()
    if last_2_progress in '待风险审查':
        progress_id = 80
    elif last_2_progress in '待地区审查':
        regress_count = 0
        for i in work_flow_dict_list:
            if i['接受状态'] in '待地区审查':
                regress_count += 1
        if regress_count == 1:
            progress_id = 50
        elif regress_count == 2:
            progress_id = 60
        else:
            progress_id = 70
    else:
        progress_id = 0
    return (progress_id, None)