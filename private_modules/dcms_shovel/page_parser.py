import re
from collections import OrderedDict, namedtuple, defaultdict

from bs4 import BeautifulSoup as BS
from bs4.element import Tag

from .customer import SearchResult
from scraper.dcms_request import DcmsHttpRequest

Element = namedtuple('Element', ['outer_html', 'inner_text'])


class Parser:
    def __init__(self, bs_obj):
        self.bs_obj = bs_obj

    def parse_to_tag_dict_list(self):
        pass

    def parse_to_dict_list(self):
        pass

    def parse_to_dict(self):
        pass


class List(Parser):
    def parse_to_tag_dict_list(self):
        try:
            cols_name = [td.text.strip() for td in self.bs_obj.find('tr', {'class': 'clsSubHeader'}).find_all('td')]
        except:
            cols_name = [td.text.strip() for td in self.bs_obj.find_all('tr', {'class': 'clsHeader'})[1].find_all('td')]
        list_trs = self.bs_obj.find_all('tr')[2: ]
        ret = []
        for tr in list_trs:
            tds = tr.find_all('td')
            ret.append({cols_name[i]: tds[i] for i in range(len(cols_name))})
        return ret

    def parse_to_dict_list(self):
        rgx_clean = re.compile(r'[\t\n\r]')
        tag_dict_list = self.parse_to_tag_dict_list()
        ret = []
        for tag_dict in tag_dict_list:
            ret.append({key: rgx_clean.sub('', value.text) for key, value in tag_dict.items()})
        return ret


class MutiplePageList:
    def __init__(self, url_path, page_param_name, dcms, max_page, cur_page=1):
        '''

        :param url_path:
        :param page_param_name: url_path中，控制当前页数的参数名，例如‘savedListCurrentPage’
        :param dcms:
        :param max_page:
        :param cur_page:
        '''
        if dcms is None:
            dcms = DcmsHttpRequest()
            dcms.login()
            # dcms.setDcmsType(dcms_type)
        self.url_path = url_path
        self.page_param_name = page_param_name
        self.dcms = dcms
        self.dcms_type = dcms.dcms_type
        self.cur_page = cur_page
        self.max_page = max_page

    def jumpToPage(self, page_num):
        self.url_path.params[self.page_param_name] = page_num
        r = self.dcms.get(self.url_path.params)

    def __iter__(self):
        for page_num in range(self.max_page):
            self.url_path.params[self.page_param_name] = page_num
            r = self.dcms.get(self.url_path.params)


class WebPage:
    parser = ('lxml', 'html.parser')
    def __init__(self, HTML_text, url_path=None, connection=None):
        self.url_path = url_path
        self.HTML_text = HTML_text
        self.HTML_soup = BS(HTML_text, self.parser[0])
        self.connection = connection
        self.current_pagenum = 1
        pass

    @property
    def search_result(self):
        return

    @property
    def lists(self):
        return

    @property
    def forms(self):
        return

    @property
    def actions(self):
        return

    @property
    def label_value_areas(self):
        return

    # @property
    # def scripts(self):
    #     return self.HTML_soup.find_all('script')

    def next_page(self, *args, **kwargs):
        pass

    def pre_page(self, *args, **kwargs):
        pass


    # def parse_by_xpath(self, xpath_dict):
    #     result = {}
    #     for k, v in xpath_dict.items():
    #         values = self.HTML_BS.xpath(v)
    #         if re.findall(r'[/@]', k):# k.__contains__('/') or k.__contains__('@'):
    #             fields = self.HTML_BS.xpath(k)
    #             i = 0
    #             for field in fields:
    #                 result[field] = values[i]
    #                 i += 1
    #         else:
    #             result[k] = values
    #     return result
    #
    # def parse_by_re(self, re_str):
    #     pass

class DcmsWebPage(WebPage):
    rgx_rlk = re.compile(r'[A-Z0-9]{32}')
    rgx_clean = re.compile(r'[\n\r\t]')
    rgx_get_page = re.compile(r'第\s*(\d+)\s*页\s共\s*(\d+)\s*页')
    NamedCell = namedtuple('NamedCell', ['name', 'value', 'inner_html'])

    @property
    def search_result(self):
        result_table = self.HTML_soup.find_all(class_='clsForm')[0].find_all('tr')[1:]
        try:
            result_data = result_table[1:]
            result_head = result_table[0].find_all('td')
            result = []
            for row in result_data:
                tmp = OrderedDict()
                row_data = row.find_all('td')
                tmp['rlk'] = self.rgx_rlk.findall(str(row_data[0]))
                for i in range(len(result_head)):
                    tmp.setdefault(result_head[i].text, row_data[i].text.strip())
                result.append(SearchResult(self.connection, **tmp))
            return result
        except:
            return None

    @property
    def lists(self):
        tables = self.HTML_soup.find_all('table', attrs={'class': 'clsForm'})
        return [List(table) for table in tables if table.find('tr', {'class': 'clsSubHeader'})]

    # def list_areas(self):
    #     ret = {}
    #     tables = self.HTML_soup.find_all('table', attrs={'class': 'clsForm'})
    #     list_index = 0
    #     for table in tables:
    #         headers = table.find_all('tr', attrs={'class': 'clsHeader'})
    #         sub_headers = table.find_all('tr', attrs={'class': 'clsSubHeader'})
    #         if not headers and not sub_headers:
    #             continue
    #         area_name = headers[0].find('td').text.strip()
    #         first_data_tr_index = len(headers) + len(sub_headers)     # 第一个数据行在这个table所有行中的索引号
    #         if sub_headers:
    #             sub_header = sub_headers[-1]
    #         else:
    #             if len(headers) > 1:
    #                 sub_header = headers[-1]
    #             else:
    #                 area_name = list_index
    #                 sub_header = headers[0]
    #         try:
    #             list_header_col_count = len(sub_header.find_all('td'))
    #         except AttributeError:
    #             list_header_col_count = 0
    #         table_all_trs = table.find_all('tr')
    #         try:
    #             list_data_col_count = len(table_all_trs[first_data_tr_index].find_all('td'))
    #         except AttributeError:
    #             list_data_col_count = 0
    #         if list_header_col_count != list_data_col_count or (list_header_col_count == 0 and list_data_col_count == 0):
    #             continue
    #         col_names = [td.text.strip() for td in sub_header.find_all('td')]
    #         data_trs = table_all_trs[first_data_tr_index: ]
    #         data_list = []
    #         for data_tr in data_trs:
    #             data_td = data_tr.find_all('td')
    #             data_list.append({col_names[i - 1]: Element(data_td[i - 1], self.rgx_clean.sub('', data_td[i - 1].text.strip())) for i in range(list_header_col_count)})
    #         ret[area_name] = data_list
    #         list_index += 1
    #     return ret

    def list_areas(self):
        ret = {}
        tables = self.HTML_soup.find_all('table', attrs={'class': 'clsForm'})
        list_index = 0
        for table in tables:
            area_name, data = self._parse_list(table)
            if area_name is None and data is None:
                continue
            area_name = area_name or list_index
            ret[area_name] = data
        return ret

    def multiple_page_list(self, table):#, area_name, url_path, dcms=None, dcms_type=DcmsHttpRequest.DcmsType.cp.value):
        header_right = table.find_all('tr', attrs={'class': 'clsHeader'}).find_all('td')[-1]
        try:
            cur_page, max_page = self.rgx_get_page.search(header_right.text).groups()
            return MutiplePageList(self.url_path, self.connection, int(max_page))
        except AttributeError:
            return None

    def label_value_areas(self):
        tables = self.HTML_soup.find_all('table', attrs={'class': 'clsForm'})
        ret = {}
        for table in tables:
            if not table.find('td', attrs={'class': 'clsLabel'}):
                continue
            trs = table.find_all('tr')
            area_name = ''
            for tr in trs:
                if 'header' in str(tr.attrs.get('class')).lower():
                    area_name = tr.find('td').text.strip()
                    ret[area_name] = defaultdict(list)
                else:
                    tds = tr.find_all('td')
                    current_label = ''
                    for td in tds:
                        if 'label' in str(td.attrs.get('class')).lower():
                            current_label = td.text.strip()
                        else:
                            ret[area_name][current_label].append(Element(td, self.rgx_clean.sub('', td.text.strip())))
        return ret

    @classmethod
    def _parse_list(cls, table):
        '''
        tables = self.HTML_soup.find_all('table', attrs={'class': 'clsForm'})
        for table in tables:
        :param table:
        :return: 列表名称、列表内容
        '''
        headers = table.find_all('tr', attrs={'class': 'clsHeader'})
        sub_headers = table.find_all('tr', attrs={'class': 'clsSubHeader'})
        if not headers and not sub_headers:
            return None, None
        area_name = headers[0].find('td').text.strip()
        first_data_tr_index = len(headers) + len(sub_headers)  # 第一个数据行在这个table所有行中的索引号
        if sub_headers:
            sub_header = sub_headers[-1]
        else:
            if len(headers) > 1:
                sub_header = headers[-1]
            else:
                area_name = None
                sub_header = headers[0]
        try:
            list_header_col_count = len(sub_header.find_all('td'))
        except AttributeError:
            list_header_col_count = 0
        table_all_trs = table.find_all('tr')
        try:
            list_data_col_count = len(table_all_trs[first_data_tr_index].find_all('td'))
        except AttributeError:
            list_data_col_count = 0
        if list_header_col_count != list_data_col_count or (list_header_col_count == 0 and list_data_col_count == 0):
            return None, None
        col_names = [td.text.strip() for td in sub_header.find_all('td')]
        data_trs = table_all_trs[first_data_tr_index:]
        data_list = []
        for data_tr in data_trs:
            data_td = data_tr.find_all('td')
            data_list.append(
                {col_names[i]: Element(data_td[i], cls.rgx_clean.sub('', data_td[i].text.strip())) for i in range(list_header_col_count)})
        return area_name, data_list