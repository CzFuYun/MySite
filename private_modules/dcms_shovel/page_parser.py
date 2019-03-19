import re
from collections import OrderedDict, namedtuple, defaultdict

from bs4 import BeautifulSoup as BS
from bs4.element import Tag

from .customer import SearchResult


Element = namedtuple('Element', ['outer_html', 'inner_text'])


class PageArea:
    def __init__(self, bs_obj, area_name=None, data_start_at=None):
        self.bs_obj = bs_obj
        self.area_name = area_name
        self.data_start_at = data_start_at

    def parse(self, *args, **kwargs):
        if self.data_start_at is None or self.area_name is None:
            headers = self.bs_obj.find_all('tr', attrs={'class': 'clsHeader'})
            sub_headers = self.bs_obj.find_all('tr', attrs={'class': 'clsSubHeader'})
            self.area_name = self.area_name or headers[0].find('td').text.strip()
            self.data_start_at = self.data_start_at or (len(headers) + len(sub_headers))  # 第一个数据行在这个table所有行中的索引号

    def parse_to_tag_dict_list(self):
        pass

    def parse_to_dict_list(self):
        pass

    def parse_to_dict(self):
        pass


class List_old_type(PageArea):
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


class LabelValueArea(PageArea):
    def __init__(self, bs_obj, area_name=None, data_start_at=None, *args, **kwargs):
        super().__init__(bs_obj, area_name, data_start_at)

    def parse(self):
        super().parse()
        ret = defaultdict(list)
        trs = self.bs_obj.find_all('tr')
        # area_name = ''
        for tr in trs:
            tds = tr.find_all('td')
            current_label = ''
            for td in tds:
                if 'label' in str(td.attrs.get('class')).lower():
                    current_label = td.text.strip()
                else:
                    ret[current_label].append(Element(td, DcmsWebPage.rgx_clean.sub('', td.text.strip())))
        return ret

class ComplexTableArea(PageArea):
    pass


class List(PageArea):
    def parse(self):
        super().parse()
        table_all_trs = self.bs_obj.find_all('tr')
        sub_header = table_all_trs[self.data_start_at - 1]
        col_names = [td.text.strip() for td in sub_header.find_all('td')]
        list_header_col_count = len(col_names)
        data_trs = table_all_trs[self.data_start_at:]
        data_list = []
        for data_tr in data_trs:
            data_td = data_tr.find_all('td')
            data_list.append(
                {col_names[i]: Element(data_td[i], DcmsWebPage.rgx_clean.sub('', data_td[i].text.strip())) for i in range(list_header_col_count)})
        return data_list


class SinglePageListArea(List):
    pass


class MultiPageListArea(List):
    def __init__(self, bs_obj, area_name=None, data_start_at=None, max_page=None):      #, url_path, page_param_name, max_page, cur_page=1):
        '''

        :param url_path:
        :param page_param_name: url_path中，控制当前页数的参数名，例如‘savedListCurrentPage’
        :param dcms:
        :param max_page:
        :param cur_page:
        '''
        super().__init__(bs_obj, area_name, data_start_at)
        if max_page is None:
            header_right = bs_obj.find_all('tr', attrs={'class': 'clsHeader'})[0].find_all('td')[-1]
            cur_page, max_page = DcmsWebPage.rgx_get_page.search(header_right.text).groups()
            max_page = int(max_page)
        self.max_page = max_page
        self.cur_page = 1
        self.cache = {}
        self.has_linked = max_page == 1 or False

    def linkToDcms(self, dcms, dcms_type, url_path, page_param_name):
        if not self.has_linked:
            dcms.setDcmsType(dcms_type)
            self.dcms = dcms
            self.dcms_type = dcms_type
            self.url_path = url_path
            self.page_param_name = page_param_name
            self.has_linked = True

    def turnToPage(self, page_num):
        if page_num == 1:
            return self.bs_obj
        else:
            self.cur_page = page_num
            try:
                return self.cache[page_num]
            except KeyError:
                page_num = min(self.max_page, page_num)
                self.url_path.params[self.page_param_name] = page_num - 1
                self.bs_obj = DcmsWebPage(self.dcms.get(self.url_path).text).areas[self.area_name].bs_obj
                self.cache[page_num] = self.bs_obj
                pass

    def parse(self):
        return super().parse()

    @property
    def last_page_content(self):
        self.turnToPage(self.max_page)
        return self.parse()

    @property
    def first_page_content(self):
        return

    def __iter__(self):
        for page_num in range(self.max_page):
            self.url_path.params[self.page_param_name] = page_num
            r = self.dcms.get(self.url_path.params)

    def __getitem__(self, item):
        pass

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


class DcmsWebPage(WebPage):
    rgx_rlk = re.compile(r'[A-Z0-9]{32}')
    rgx_clean = re.compile(r'[\n\r\t]')
    rgx_get_page = re.compile(r'第\s*(\d+)\s*页\s共\s*(\d+)\s*页')
    NamedCell = namedtuple('NamedCell', ['name', 'value', 'inner_html'])

    @classmethod
    def judgeAreaType(cls, area_bs_obj):
        '''
        判断页面区域的类型，返回区域名称及一个可解析的页面区域实例
        :return:
        '''
        headers = area_bs_obj.find_all('tr', attrs={'class': 'clsHeader'})
        sub_headers = area_bs_obj.find_all('tr', attrs={'class': 'clsSubHeader'})
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
                # area_name = None
                sub_header = headers[0]
        try:
            list_header_col_count = len(sub_header.find_all('td'))
        except AttributeError:
            list_header_col_count = 0
        table_all_trs = area_bs_obj.find_all('tr')
        try:
            list_data_col_count = len(table_all_trs[first_data_tr_index].find_all('td'))
        except AttributeError:
            list_data_col_count = 0
        if list_header_col_count == list_data_col_count and (list_header_col_count * list_data_col_count):
            header_right = area_bs_obj.find_all('tr', attrs={'class': 'clsHeader'})[0].find_all('td')[-1]
            try:
                cur_page, max_page = cls.rgx_get_page.search(header_right.text).groups()
                return area_name, MultiPageListArea(area_bs_obj, area_name, max_page=int(max_page))
            except AttributeError:
                return area_name, SinglePageListArea(area_bs_obj, area_name)
        else:
            if area_bs_obj.find('td', attrs={'class': 'clsLabel'}):
                return area_name, LabelValueArea(area_bs_obj, area_name)
            else:
                return area_name, ComplexTableArea(area_bs_obj, area_name)

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
        return [List_old_type(table) for table in tables if table.find('tr', {'class': 'clsSubHeader'})]

    @property
    def areas(self):
        tables = self.HTML_soup.find_all('table', attrs={'class': 'clsForm'})
        area_count = len(tables)
        ret = {}
        for i in range(area_count):
            area_name, area_bs_obj = self.judgeAreaType(tables[i])
            area_name = area_name or i
            if area_bs_obj:
                ret[area_name] = area_bs_obj
        return ret


