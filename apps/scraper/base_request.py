import requests, bs4

# from deposit_and_credit.models_operation import DateOperation


class BaseHttpRequest:
    origin_url = ''

    def __init__(self, *args, **kwargs):
        self.connection = requests.session()

    def get(self, url_path):
        if url_path.strip().lower().startswith('http'):
            url = url_path
        else:
            url = self.origin_url + url_path
        while True:
            response = self.connection.get(url)
            if response.status_code == 200:
                break
        return response

    def post(self, url_path, **kwargs):
        if url_path.strip().lower().startswith('http'):
            url = url_path
        else:
            url = self.origin_url + url_path
        while True:
            response = self.connection.post(url, data=kwargs)
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