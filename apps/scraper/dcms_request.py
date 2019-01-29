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


# class PostUrls:
#     UrlPath = namedtuple('UrlPath', ['path', 'params'])
#     base_params = {
#         'do': 'Search',
#         'searchBranchCode': 'HQ',
#         'scope': 'A',
#         'searchCriteria': None,
#         'searchValue': None
#     }
#
#     def __init__(self, applicationCode):
#         self.dcms_type = '' if applicationCode == 'DCMSCP' else 'sme'
#
#     @property
#     def login(self):
#         return self.UrlPath('dcmscp/login.view', {'step': 'defined', 'post': '登录'})
#
#     @property
#     def search_cp(self):
#         return self.UrlPath(self.dcms_type + 'dcms/corporate/application/inquiry/application_inquiry.view', self.base_params.copy())
#
#     @property
#     def search_cf(self):
#         return self.UrlPath(self.dcms_type + 'mcif/credit_file_setup/credit_file.view', self.base_params.copy())
#
#     @property
#     def search_lu(self):
#         return self.UrlPath(self.dcms_type + 'dcma/limit_utilization/application/application.view', self.base_params.copy())


class DcmsHttpRequest(BaseHttpRequest):
    origin_url = 'http://110.17.1.21:9082/'
    base_params = {
        'do': 'Search',
        'searchBranchCode': 'HQ',
        'scope': 'A',
        'searchCriteria': None,
        'searchValue': None
    }

    def login(self, userId='czfzc', password='hxb123', applicationCode='DCMSCP'):
        self.applicationCode = applicationCode
        # self.post_urls = PostUrls(applicationCode)
        # self.get_urls = GetUrls(applicationCode)
        self.dcms_type = '' if applicationCode == 'DCMSCP' else 'sme'
        self.userId = userId
        self.password = password
        r = self.post(self.UrlPath('dcmscp/login.view', {'step': 'defined', 'post': '登录'}), userId=self.userId, password=self.password, applicationCode=self.applicationCode)
        assert 'HXB_DCMS_WINDOW_' in r.text, '登录失败，用户名或密码不正确'
        self.post_urls = {
            # 'login': self.UrlPath('dcmscp/login.view', {'step': 'defined', 'post': '登录'}),
            'search_cp': self.UrlPath(self.dcms_type + 'dcms/corporate/application/inquiry/application_inquiry.view', self.base_params.copy()),
            'search_cf': self.UrlPath(self.dcms_type + 'mcif/credit_file_setup/credit_file.view', self.base_params.copy()),
            'search_lu': self.UrlPath(self.dcms_type + 'dcma/limit_utilization/application/application.view', self.base_params.copy()),
        }
        self.get_urls = {
            'keep_connection': 'http://110.17.1.21:9082/dcms_index.view'
        }
        return self

    def keepConnection(self):
        r = self.get(self.get_urls['keep_connection'])
        if 'frame' not in r.text:
            self.login()
        threading.Timer(60, self.keepConnection).start()

    def search_cf(self, name_or_cf):
        searchCriteria = SearchBy.cf_num if name_or_cf.startswith('CF') else SearchBy.customer_name
        response = self.post(self.post_urls['search_cf'], searchCriteria=searchCriteria, searchValue=name_or_cf)
        try:
            search_result = DcmsWebPage(response.text, None).lists[0].parse_to_tag_dict_list()
            index = 0
            if len(search_result) > 1:
                print('条件【' + name_or_cf + '】查找到' + str(len(search_result)) + '个客户，请选择：')
                for i in range(len(search_result)):
                    print(str(i + 1) + '.' + search_result[i]['客户'].text.strip())
                index = int(input('>>>')) - 1
            result = search_result[index]['信贷文件编号']
            cf_num = result.text.strip()
            cf_rlk = RegExp.rlk.search(str(result)).group(1)
            return (cf_num, cf_rlk)
        except:
            return (None, None)

    def get_into_cp(self, cp_num):
        r = self.post(self.post_urls['search_cp'], searchValue=cp_num, searchCriteria=SearchBy.con_num)
        rlk = RegExp.rlk.findall(r.text)[0]
        return

    def search_lu(self, lu_num):
        r = self.post(self.post_urls['search_lu'], searchValue=lu_num, searchCriteria=SearchBy.con_num, stopLimit='N')
        rlk = RegExp.rlk.findall(r.text)[0]
        pass