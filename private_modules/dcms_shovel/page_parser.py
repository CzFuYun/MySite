import re
from collections import OrderedDict

from bs4 import BeautifulSoup as BS
from bs4.element import Tag

from .customer import SearchResult

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
        cols_name = [td.text.strip() for td in self.bs_obj.find('tr', {'class': 'clsSubHeader'}).find_all('td')]
        list_trs = self.bs_obj.find_all('tr')[2: ]
        ret = []
        for tr in list_trs:
            tds = tr.find_all('td')
            ret.append({cols_name[i]: tds[i] for i in range(len(cols_name))})
        return ret

    def parse_to_dict_list(self):
        tag_dict_list = self.parse_to_tag_dict_list()
        ret = []
        for tag_dict in tag_dict_list:
            ret.append({key: value.text.strip() for key, value in tag_dict.items()})
        return ret


class Detail(Parser):
    def parse_to_dict(self):
        pass


class WebPage:
    parser = ('lxml', 'html.parser')
    def __init__(self, HTML_text, path_url=None, connection=None):
        self.path_url = path_url
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
    def details(self):
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

    @property
    def details(self):
        detail_tables = self.HTML_soup.find_all('table', attrs={'class': 'clsForm'})
        return [List(table) for table in detail_tables if not table.find('tr', {'class': 'clsSubHeader'})]


