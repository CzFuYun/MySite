import re, sys, threading
from collections import namedtuple

import requests, bs4

from .base_request import BaseHttpRequest
from  private_modules.dcms_shovel.page_parser import DcmsWebPage


class RegExp:
    rlk = re.compile(r"'([A-Z0-9]{32})'")


class SearchBy:
    con_num = 'ref_no'
    customer_name = 'CUSTOMER_NM'
    cf_num = 'CREDIT_FILE_NO'
    customer_code = 'CUSTOMER_NO'


class DcmsHttpRequest(BaseHttpRequest):
    origin_url = 'http://110.17.1.21:9082/'
    base_params = {
        'do': 'Search',
        'searchBranchCode': 'HQ',
        'scope': 'A',
        'searchCriteria': None,
        'searchValue': None
    }

    class DcmsType:
        cp = 'DCMSCP'
        sme = 'SMEDCMS'
        cs = 'DCMSCS'

    def setDcmsType(self, dcms_type):
        self.dcms_type = 'sme' if dcms_type == self.DcmsType.sme else ''
        self.post_urls = {
            'search_cp': self.UrlPath(
                'dcms/consumer/application/inquiry/application_inquiry.view' if self.applicationCode == 'DCMSCS' else (self.dcms_type + 'dcms/corporate/application/inquiry/application_inquiry.view'),
                self.base_params.copy()
            ),
            'search_cf': self.UrlPath(self.dcms_type + 'mcif/credit_file_setup/credit_file.view', self.base_params.copy()),
            'search_lu': self.UrlPath(self.dcms_type + 'dcma/limit_utilization/application/application.view', self.base_params.copy()),
            'search_customer': self.UrlPath('mcif/customer_search.view', self.base_params.copy()),
        }
        self.get_urls = {
            'keep_connection': 'http://110.17.1.21:9082/dcms_index.view',
        }

    def login(self, userId='czfzc', password='hxb123', applicationCode='DCMSCP', dcms_type='DCMSCP', keep_long=False):
        '''

        :param userId:
        :param password:
        :param applicationCode: DCMSCP  SMEDCMS  DCMSCS
        :return:
        '''
        self.applicationCode = applicationCode
        self.setDcmsType(dcms_type)
        self.userId = userId
        self.password = password
        r = self.post(self.UrlPath('dcmscp/login.view', {'step': 'defined', 'post': '登录'}), userId=self.userId, password=self.password, applicationCode=self.applicationCode)
        assert 'HXB_DCMS_WINDOW_' in r.text, '登录失败，用户名或密码不正确'
        self.setDcmsType(dcms_type)
        if keep_long:
            self.keepConnection()
        return self

    def keepConnection(self):
        r = self.get(self.get_urls['keep_connection'])
        if 'frame' not in r.text:
            self.login()
        threading.Timer(60, self.keepConnection).start()

    def search_cf(self, name_or_cf_code):
        if name_or_cf_code.startswith('CF'):
            searchCriteria = SearchBy.cf_num
        elif name_or_cf_code.startswith('C'):
            searchCriteria = SearchBy.customer_code
        else:
            searchCriteria = SearchBy.customer_name
        # searchCriteria = SearchBy.cf_num if name_or_cf.startswith('CF') else SearchBy.customer_name
        response = self.post(self.post_urls['search_cf'], searchCriteria=searchCriteria, searchValue=name_or_cf_code)
        try:
            search_result = DcmsWebPage(response.text, None).lists[0].parse_to_tag_dict_list()
            index = 0
            if len(search_result) > 1:
                print('条件【' + name_or_cf_code + '】查找到' + str(len(search_result)) + '个客户，请选择：')
                for i in range(len(search_result)):
                    print(str(i + 1) + '.' + search_result[i]['客户'].text.strip())
                index = int(input('>>>')) - 1
            result = search_result[index]['信贷文件编号']
            cf_num = result.text.strip()
            cf_rlk = RegExp.rlk.search(str(result)).group(1)
            return (cf_num, cf_rlk)
        except:
            return (None, None)

    def search_customer(self, name_or_code):
        '''

        :param name_or_code: 客户名称或客户编号C247551
        :return:
        '''
        customerType = 'CP'
        if name_or_code.startswith('C'):
            searchCriteria = 'no'
        elif name_or_code.startswith('P'):
            searchCriteria = 'no'
            customerType = 'CS'
        else:
            searchCriteria = 'nm'
        r = self.post(
            self.post_urls['search_customer'],
            do='AllScopeSearch',
            customerType=customerType,
            cardCategory='I',
            searchCriteria=searchCriteria,
            searchValue=name_or_code
        )
        try:
            rlk = RegExp.rlk.findall(r.text)[0]
        except:
            print('未在DCMS中查询到客户', name_or_code)
            return None
        else:
            search_result = DcmsWebPage(r.text)
            customer_info = search_result.lists[0].parse_to_dict_list()
            index = 0
            if len(customer_info) > 1:
                print('搜索', name_or_code, '获得超过一个结果：')
                for i in range(len(customer_info)):
                    print(i, customer_info[i]['客户名称'], customer_info[i]['客户编号'])
                index = input('请选择>>>')
            shallow_info = customer_info[int(index)]
            deep_info = search_result.lists[0].parse_to_tag_dict_list()[int(index)]
            return (shallow_info, deep_info)

    def search_cp(self, cp_num):
        r = self.post(
            self.post_urls['search_cp'],
            searchValue=cp_num,
            searchCriteria=SearchBy.con_num
        )
        try:
            rlk = RegExp.rlk.findall(r.text)[0]
            return rlk
        except:
            return None

    def search_lu(self, lu_num):
        r = self.post(
            self.post_urls['search_lu'],
            searchValue=lu_num,
            searchCriteria=SearchBy.con_num,
            stopLimit='N'
        )
        rlk = RegExp.rlk.findall(r.text)[0]
        return rlk

