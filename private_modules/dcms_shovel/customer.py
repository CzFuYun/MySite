from collections import namedtuple

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from dcms_shovel import page_parser


class SearchResult:
    label_reflector = {
        '申请信息': 'tab_dcms_cp_0002',
        '业务': 'tab_dcms_cp_0004',
        '文件生成': 'tab_dcms_cp_0009',
        '工作流': 'tab_dcms_cp_0010',
    }
    def __init__(self, dcms_connection, **kwargs):
        self.dcms_connection = dcms_connection
        for key, value in kwargs.items():
            self.__dict__[key] = value

    def click_into(self):
        self.dcms_connection.browser.find_element_by_partial_link_text(self.__dict__['序号']).click()

    def open_in_new_window(self):
        pass

    def click_label(self, label_text):
        self.dcms_connection.switch_to_main_frame()
        label_id = self.label_reflector[label_text]
        self.dcms_connection.switch_to_body_frame()
        self.dcms_connection.browser.find_element_by_id(label_id).click()
        pass


class CpFlow(SearchResult):
    pass


class Customer:
    work_flow_type_reflector = {
        'CP': '',
        'LU': '',
    }
    cf_label_reflector = {
        '基本信息': '1001',
        '业务': '1002',
        '担保': '1003',
        '授信申请': '1004',
        '额度换用/补偿': '1008',
        '额度使用': '1005',
        '贷后监控': '1006',
    }
    def __init__(self, dcms_connection, name, cf_num=None):
        self.dcms_connection = dcms_connection
        self.name = name
        self.page_cache = {}
        self.__cf_num = cf_num

    @property
    def cf_num(self):
        if self.__cf_num is None:
            self.__cf_num = self.search_cf()
        return self.__cf_num

    def search_cf(self):
        self.dcms_connection.click_main_menu('业务综合查询')
        searchCriteria = 'CREDIT_FILE_NO' if self.__cf_num else 'CUSTOMER_NM'
        searchValue = self.__cf_num or self.name
        self.dcms_connection.submit_form(submit_btn_locator=(By.NAME, 'Go'), searchCriteria=searchCriteria, searchValue=searchValue, searchBranchCode='HQ')
        path = self.dcms_connection.active_frame_path
        self.page_cache['credit_file_search'] = DcmsWebPage(self.dcms_connection.browser.page_source, path)
        try:
            base_detail_dict = self.page_cache['credit_file_search'].lists[0].parse_to_dict_list()[0]
            self.name = base_detail_dict['客户']
            self.__cf_num = base_detail_dict['信贷文件编号']
            return base_detail_dict['信贷文件编号']
        except:
            return

    def get_into_cf_detail_page(self, go_to_label=None):
        try:
            self.dcms_connection.browser.find_element_by_partial_link_text(self.__cf_num).click()
        except:
            self.search_cf()
            self.dcms_connection.browser.find_element_by_partial_link_text(self.__cf_num).click()
        if go_to_label:
            self.go_to_cf_label(go_to_label)

    def go_to_cf_label(self, label_text):
        self.dcms_connection.switch_to_main_frame()
        if not self.dcms_connection.browser.page_source.__contains__('信贷文件明细'):
            self.get_into_cf_detail_page()
        label_id = self.cf_label_reflector[label_text]
        self.dcms_connection.browser.find_element_by_id(label_id).click()

    def get_into_work_flow(self, con_num):
        # 若当前页面在流程列表上，则直接点击链接进入，否则从主选单选择相应功能
        pass
