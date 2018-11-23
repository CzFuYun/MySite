from dcms_shovel import connection, customer, page_parser


def update_cp_progress(dcms, name_or_num, cf=None):
    # 更新非特别授信系统进度
    if name_or_num.startswith('CP/') or name_or_num.startswith('SME/'):
        result = dcms.search_work_flow(name_or_num)
        result.click_into()
        result.click_label('工作流')
        dcms.switch_to_application_frame()
        page = page_parser.DcmsWebPage(dcms.browser.page_source, dcms.active_frame_path)
        progresses = page.lists[0].parse_to_dict_list()
        pass
        last_progress = progresses[-1:]['接受状态']
        if last_progress == '授信申请建档':
            progress_id = 40
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

