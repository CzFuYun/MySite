import requests, bs4
from collections import namedtuple

# from deposit_and_credit.models_operation import DateOperation


class BaseHttpRequest:
    origin_url = ''
    base_params = {}
    UrlPath = namedtuple('UrlPath', ['path', 'params'])

    def __init__(self, *args, **kwargs):
        self.connection = requests.session()
        self.post_urls = None
        self.get_urls = None

    def get(self, url_path):
        url = url_path if type(url_path) is str else url_path.path
        if not url.strip().lower().startswith('http'):
            url = self.origin_url + url
        while True:
            response = self.connection.get(url)
            if response.status_code == 200:
                break
        return response

    def post(self, url_path, **kwargs):
        if type(url_path) is str:
            url = url_path
            data = kwargs
        else:
            url = url_path.path
            data = {**url_path.params, **kwargs}
        if not url.strip().lower().startswith('http'):
            url = self.origin_url + url
        while True:
            response = self.connection.post(url, data=data)
            if response.status_code == 200:
                break
        return response

    def login(self, *args, **kwargs):
        pass

    @staticmethod
    def encode(string):
        '''
        将含中文的字符串转化为url编码形式
        :param string:
        :return:
        '''
        return str(string.encode())[2:-1].replace(r'\x', '%').upper()