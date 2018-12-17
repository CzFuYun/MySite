from datetime import date
from collections import defaultdict
from time import sleep

import execjs
import selenium
from selenium.common.exceptions import NoSuchFrameException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.support import wait, expected_conditions, select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from .page_parser import DcmsWebPage
from private_modules.dcms_shovel.customer import Customer


BROWSER_OPTIONS = Options()
# BROWSER_OPTIONS.add_argument('--headless')
BROWSER_OPTIONS.add_argument('--no-sandbox')
BROWSER_OPTIONS.add_argument('--disable-dev-shm-usage')
BROWSER_OPTIONS.add_argument('--disable-gpu')
BROWSER_DRIVER_DIR = r'D:\chromedriver.exe'

# with open(r'D:\开发中\PurePython\MySite\static\assets\plugins\jquery\jquery.min.js', 'r') as f:
#     jQuery_text = f.read()
# jQuery = execjs.compile(jQuery_text)

class WebConnection:
    def __init__(self, origin_url, **kwargs):
        self.origin_url = origin_url
        self.browser = webdriver.Chrome(BROWSER_DRIVER_DIR, chrome_options=BROWSER_OPTIONS)
        self.main_window = self.browser.current_window_handle
        self.active_frame_path = None
        if kwargs:
            for key, value in kwargs.items():
                self.__dict__[key] = value

    def navigate(self, path, **kwargs):
        params = ''
        if kwargs:
            for key, value in kwargs.items():
                if hasattr(value, '__iter__') and not isinstance(value, str):
                    for v in value:
                        params += ('&' + key + '=' + str(v))
                else:
                    params += ('&' + key + '=' + str(value))
        if path.__contains__('?'):
            path += params
        else:
            path += ('?' + params)
        self.browser.get(self.origin_url + path)
        return self.browser.page_source

    def submit_form(self, form_locator=None, submit_btn_locator=None, **name_value):
        for name, value in name_value.items():
            input_elems = self.browser.find_elements_by_name(name)
            input_type = input_elems[0].get_attribute('type')
            if input_type in ('text', 'password', 'date'):
                input_elems[0].send_keys(str(value))
            elif input_type in ('radio', 'checkbox'):
                for elem in input_elems:
                    if elem.get_attribute('value') == str(value):
                        self.browser.execute_script('arguments[0].checked=true', elem)
                        # elem.click()
            elif input_elems[0].tag_name == 'select':
                elem = select.Select(input_elems[0])
                if hasattr(value, '__iter__') and not isinstance(value, str):
                    for v in value:
                        elem.select_by_value(str(v))
                else:
                    elem.select_by_value(str(value))
        if submit_btn_locator:
            self.browser.find_element(*submit_btn_locator).click()      # 若指定了提交按钮
        else:
            try:
                self.browser.find_element_by_css_selector('[type=submit]').click()      # 若未指定提交按钮，则点击type为submit的按钮
            except NoSuchElementException:
                form = self.browser.find_element(*form_locator) if form_locator else self.browser.find_element_by_tag_name('form')
                try:
                    form_btns = form.find_elements_by_css_selector('[type=button]')
                    if len(form_btns) == 1:
                        form_btns[0].click()
                except:
                    form.submit()

    def get_active_frame_path(self):
        self.active_frame_path = self.browser.execute_script('return location.pathname;')

    def wait_until_elem(self, flag_elem_locator, time_out_second=20, check_per_second=0.5):
        '''
        :param flag_elem_locator: 元组形式的选择器，形如   (By.ID, 'kw')
        :param time_out_second:
        :param check_per_second:
        :return:
        '''
        waiter = wait.WebDriverWait(self.browser, time_out_second, check_per_second)
        # waiter.until(expected_conditions.presence_of_element_located(flag_elem_locator))
        waiter.until(lambda x: x.find_element(*flag_elem_locator))

    def wait_until_alert(self, time_out_second=20, check_per_second=0.5):
        waiter = wait.WebDriverWait(self.browser, time_out_second, check_per_second)
        waiter.until(expected_conditions.alert_is_present)
        pass


class DcmsConnection(WebConnection):
    def __init__(self, origin_url, **kwargs):
        super().__init__(origin_url, **kwargs)
        self.menu_structure = {}

    def login(self, userId, password, applicationCode='DCMSCP'):
        self.navigate('/dcmscp/login.view')
        self.submit_form(userId=userId, password=password, applicationCode=applicationCode)
        self.browser.switch_to.alert.accept()
        assert self.browser.current_url.__contains__('index.view'), '登录失败'
        self.switch_to_menu_frame()
        all_a = self.browser.find_elements_by_tag_name('a')
        for a in all_a:
            a_path = self.browser.execute_script('''
            var super_ = arguments[0].parentElement.parentElement.previousElementSibling;
            var path = [arguments[0].innerText];
            while(super_ && !super_.className.includes("menufont")){
                path.unshift(super_.innerText);
                super_ = super_.parentElement.previousElementSibling;
            }
            return path
            ''', a)
            self.menu_structure[tuple(a_path)] = a
        self.browser.switch_to.default_content()

    def click_main_menu(self, *item_text):
        # 切换至主菜单的frame
        self.switch_to_menu_frame()
        if len(item_text) == 1:
            foldinglist = self.browser.find_elements_by_id('foldinglist')
            for item in foldinglist:
                self.browser.execute_script('arguments[0].style.display="block"', item)
            self.browser.find_element_by_partial_link_text(item_text[0]).click()
        else:
            self.browser.execute_script('arguments[0].click()', self.menu_structure[tuple(item_text)])
        self.browser.switch_to.default_content()

    def submit_form(self, form_locator=None, submit_btn_locator=None, **name_value):
        try:
            self.switch_to_main_frame()
        except NoSuchFrameException:
            pass
        super().submit_form(form_locator, submit_btn_locator, **name_value)

    def switch_to_header_frame(self):
        self.switch_to_main_frame()
        self.browser.switch_to.frame(self.browser.find_element_by_css_selector('frameset>frame'))
        hidden_inputs = self.browser.find_elements_by_css_selector('input[type=hidden]')
        for elem in hidden_inputs:
            name = elem.get_attribute('name')
            self.browser.execute_script('arguments[0].setAttribute("id", "{name}")'.format(name=name), elem)

    def switch_to_body_frame(self):
        self.switch_to_main_frame()
        try:
            self.browser.switch_to.frame(self.browser.find_elements_by_css_selector('frameset>frame')[1])
        except:
            self.browser.switch_to.frame(self.browser.find_elements_by_css_selector('iframe')[0])
        self.get_active_frame_path()

    def switch_to_application_frame(self):
        self.switch_to_body_frame()
        try:
            self.browser.switch_to.frame(self.browser.find_element_by_tag_name('iframe'))
        except:
            self.browser.switch_to.frame('application_frame')
        self.get_active_frame_path()

    def switch_to_menu_frame(self):
        self.browser.switch_to.default_content()
        self.browser.switch_to.frame('content')

    # def switch_to_top_frame(self):
    #     self.browser.switch_to.default_content()
    #

    def switch_to_main_frame(self):
        self.browser.switch_to.default_content()
        self.browser.switch_to.frame('main')
        self.get_active_frame_path()

    def search_customer(self, name, cf_num=None):
        return Customer(self, name, cf_num)

    def search_work_flow(self, con_num):
        con_num = con_num.strip()
        if con_num.startswith('LU') or con_num.startswith('SMELU'):
            menu_item = ('放款管理', '额度使用', '查询')
        elif con_num.startswith('CP') or  con_num.startswith('SME'):
            menu_item = ('授信申报与审批', '企业法人授信申请', '查询')
        else:
            menu_item = None
        self.click_main_menu(*menu_item)
        self.submit_form(submit_btn_locator=(By.NAME, 'Go'), searchCriteria='ref_no', searchValue=con_num)
        assert not self.browser.page_source.count('对不起, 未找到记录'), con_num + '未找到'
        search_result_page = DcmsWebPage(self.browser.page_source, self.browser.current_url, self)
        return search_result_page.search_result[0]

    def format_date(self, dcms_datetime):
        '''
        将dcms中的日期时间转化为标准格式
        :param dcms_datetime: 11/28/2018 10:16:00 AM
        :return: yyyy-mm-dd
        '''
        js = '''
        var time_stamp = Date.parse("{dcms_datetime}");
        var date = new Date(time_stamp);
        var year = date.getFullYear();
        var month = date.getMonth() + 1;
        var day = date.getDate();
        return [year, month, day];
        '''.format(dcms_datetime=dcms_datetime)
        year, month, day = self.browser.execute_script(js)
        return date(year, month, day)#.isoformat()


if __name__ == '__main__':
    print('start')
    dcms1 = DcmsConnection('http://110.17.1.21:9082')
    dcms1.login('czfzc', 'hxb123')
    customer = dcms1.search_customer('江苏武进经济发展集团公司')
    cf_num = customer.cf_num
    customer.get_into_cf_detail_page('额度使用')
    customer.get_into_cf_detail_page(False)
    print('end')
