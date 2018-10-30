from dcms_shovel import connection, customer, page_parser


def update_cp_progress(dcms, name_or_num, cf=None):
    # 更新非特别授信系统进度
    if name_or_num.startswith('CP'):
        dcms.get_into_work_flow(name_or_num)
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

if __name__ == '__main__':
    dcms = connection.DcmsConnection('http://110.17.1.21:9082')
    dcms.login('czfzc', 'hxb123')
    update_cp_progress(dcms, '江苏武进经济发展集团有限公司')

