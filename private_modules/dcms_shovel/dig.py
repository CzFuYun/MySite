from dcms_shovel import connection, customer, page_parser


def get_cp_progress_id(dcms, name_or_num, cf=None):
    # 更新非特别授信系统进度
    if name_or_num.startswith('CP/') or name_or_num.startswith('SME/'):
        result = dcms.search_work_flow(name_or_num)
        result.click_into()
        result.click_label('工作流')
        dcms.switch_to_application_frame()
        page = page_parser.DcmsWebPage(dcms.browser.page_source, dcms.active_frame_path)
        progresses = page.lists[0].parse_to_dict_list()
        last_progress = progresses[-1]['接受状态']
        progress_reflector = {
            '授信申请建档': 40,
            '待风险审查': 75,
            '待地区信审会审批': 90,
            '待地区CCRO推荐': 100,
            '已关闭': judge_closed_cp_approve_status,
            '续议': 104,
            '否决': 103,
            '退回补充材料': judge_regressed_cp_progress
        }
        progress_id = 0
        # if progress_reflector.get(last_progress):
        #     if type(progress_reflector.get(last_progress)) == int:
        #         return progress_reflector.get(last_progress)
        #     else:
        #         pass

        if last_progress == '授信申请建档':
            progress_id = 40
        elif last_progress == '待风险审查':
            progress_id = 75
        elif last_progress.__contains__('待地区信审会审批'):
            progress_id = 90
        elif last_progress == '待地区CCRO推荐':
            progress_id = 100
        elif last_progress == '已关闭':
            progress_id = judge_closed_cp_approve_status(progresses)
        elif last_progress == '续议':
            progress_id = 104
        elif last_progress == '否决':
            progress_id = 103
        elif last_progress == '退回补充材料':
            pass
    else:
        cust = dcms.search_customer(name_or_num, cf)
        cust.go_to_cf_label('授信申请')
        dcms.switch_to_main_frame()
        dcms.switch_to_body_frame()
        page = page_parser.DcmsWebPage(dcms.browser.page_source, dcms.active_frame_path)
        cp_list = page.lists[0].parse_to_dict_list()
        for cp in cp_list:
            if cp['状态'] not in ('已取消', ):
                pass
        pass
    pass


def get_cp_num(dcms, customer_name):
    cust = dcms.search_customer(customer_name)
    cust.go_to_cf_label('授信申请')
    dcms.switch_to_main_frame()
    dcms.switch_to_body_frame()
    page = page_parser.DcmsWebPage(dcms.browser.page_source, dcms.active_frame_path)
    cp_list = page.lists[0].parse_to_dict_list()
    for cp in cp_list:
        if cp['状态'] in ('已取消',):
            continue

    pass


def judge_closed_cp_approve_status(work_flow_dict_list):
    last_2_progress = work_flow_dict_list[-2]['接受状态']
    if last_2_progress in ('授信已批准', '批准条件', '条件已落实'):
        progress_id = 105
    elif last_2_progress == '续议':
        progress_id = 104
    elif last_2_progress == '否决':
        progress_id = 103
    else:
        raise Exception
    return progress_id


def judge_regressed_cp_progress(work_flow_dict_list):
    '''
    判断已退回的授信流程的工作流进程
    :param work_flow_dict_list:
    :return:
    '''
    pass