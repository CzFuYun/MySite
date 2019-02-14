import os, json, datetime, decimal, re, xlsxwriter
from io import BytesIO
from collections import UserList

from django.utils.encoding import escape_uri_path
from django.shortcuts import HttpResponse, reverse
from django.http import StreamingHttpResponse, FileResponse
from django import forms
from django.shortcuts import HttpResponse, render_to_response
from django.utils.safestring import mark_safe



return_as = {
    'choice': 1,
    'list': 2,
    'dict':3,
}
yes_no_choices = (('1', '是'), ('0', '否'),)
yes_no_unknown_choices = (('1', '是'), ('0', '否'), ('', '未知'))

def uploadFile(request, target_dir):
    pass


# def downloadFile(file_full_name, chunck_size=512):
#     def file_iterator():
#         with open(file_full_name, 'rb') as f:
#             while True:
#                 file_block = f.read(chunck_size)
#                 if file_block:
#                     yield file_block
#                 else:
#                     break

def downloadFile(file_full_name):
    # save_path = 'C:\\Users\\hp\\Downloads'
    file_name = file_full_name.replace(os.path.join(os.path.dirname(file_full_name),''),'')
    file = open(file_full_name, 'rb')
    response = FileResponse(file)
    # file.close()
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(file_name))
    return response


class JsonEncoderExtend(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, decimal.Decimal):
            f = float(o)
            i = int(o)
            if f - i:
                return f
            else:
                return i
        else:
            return json.JSONEncoder.default(self, o)


def calHtmlFormMargin(request):
    data = getattr(request, request.method)
    sizeX = data['sizeX']
    sizeY = data['sizeY']
    screenX = data['screenX']
    screenY = data['screenY']
    marginX = (int(screenX) - int(sizeX)) / 2
    marginY = (int(screenY) - int(sizeY)) / 2
    return marginX, marginY


class HtmlFormBody():
    def __init__(self, request):
        self.request = request
        self.data =  getattr(self.request, self.request.method)
        self.main_inputs = []

    def marginXY(self):
        data = self.data
        sizeX = data['sizeX']
        sizeY = data['sizeY']
        screenX = data['screenX']
        screenY = data['screenY']
        self.marginX = (int(screenX) - int(sizeX)) / 2
        self.marginY = (int(screenY) - int(sizeY)) / 2

    def addInput(self, main_input_obj, *args):
        self.main_inputs.append(main_input_obj)
        for i in args:
            self.main_inputs.append(i)

    def fillValue(self, name_value_data):
        for mi in self.main_inputs:
            name = mi.attribute.get['name']
            if name:
                mi.attribute['value'] = name_value_data.get(name, '')

    def prepareForm(self, action_url_name='', enc_type='', submit_method='post', form_title='', form_subtitle=''):
        self.marginXY()
        self.form_id = self.data.get('formId')
        self.action_url_name = action_url_name
        self.enc_type = enc_type
        self.submit_method = submit_method
        self.form_title = form_title
        self.form_subtitle = form_subtitle


class FormInput():
    def __init__(self, tag, html_attribute_dict):
        self.tag = tag
        self.attribute = html_attribute_dict


class FormMainInput(FormInput):
    def __init__(self, tag, html_attribute_dict, label_text):
        FormInput.__init__(self, tag, html_attribute_dict)
        self.label = label_text
        self.satellite = []
        self.sub_elems = []

    def addSatellite(self, satellite_input_obj, *args):
        self.satellite.append(satellite_input_obj)
        for i in args:
            self.satellite.append(i)

    def addSubElem(self, sub_elem_obj, *args):
        self.sub_elems.append(sub_elem_obj)
        for i in args:
            self.sub_elems.append(i)


class FormSatelliteInput(FormInput):
    def __init__(self, tag, html_attribute_dict, icon):
        FormInput.__init__(self, tag, html_attribute_dict)
        self.icon = icon


class FormInputSubElem(FormInput):
    def __init__(self, tag, html_attribute_dict, inner_text):
        FormInput.__init__(self, tag, html_attribute_dict)
        self.text = inner_text


class HtmlFormInfo():
    def __init__(self, request, method='post', title='', subtitle='', enc_type='multipart/form-data'):
        self.request = request
        data = getattr(self.request, self.request.method)
        self.form_id = data.get('formId') or data.get('form_id')
        self.action = data.get('urlName') or data.get('url_name')
        sizeX = data['sizeX']
        sizeY = data['sizeY']
        screenX = data['screenX']
        screenY = data['screenY']
        self.marginX = (int(screenX) - int(sizeX)) / 2
        self.marginY = max((int(screenY) - int(sizeY)) / 2, 0)
        self.title = title
        self.subtitle = subtitle
        self.method = method
        self.enc_type = enc_type


def setRequiredFields(self, exclude=('-', )):
    for field_name in self.base_fields:
        if field_name not in exclude:
            field = self.base_fields[field_name]
            field.required = True
            field.widget.attrs.update({'required': ''})
            field_type = str(type(field))
            # if field_type.find('NullBooleanField') >= 0:
            #     self.fields[field_name] = forms.IntegerField(label=field.label, widget=forms.RadioSelect(choices=yes_no_choices))
            if field_type.find('BooleanField') >= 0:      # 布尔型字段要转换一下
                self.fields[field_name] = forms.IntegerField(label=field.label, widget=forms.RadioSelect(choices=yes_no_choices))


class CleanForm():

    def cleanData(self, rule):
        '''

        :param rule: 由字段名和re.compile对象组成的字典
        :return:
        '''
        self.data = self.data.copy()
        for field in self.data:
            reg = rule.get(field)
            if reg:
                value_list = self.data.getlist(field)
                cleaned_value_list = []
                for value in value_list:
                    # if reg.groups:
                    #     cleaned_value_list.append(None)
                    # else:
                        cleaned_value_list.append(reg.findall(value)[0])
                self.data.setlist(field, cleaned_value_list)


def field_choices_to_dict(field_choices, reverse=True):
    dic = {}
    if reverse:
        k, v = 1, 0
    else:
        k, v = 0, 1
    for i in field_choices:
        dic[str(i[k])] = i[v]
    return dic


def downloadWorkbook(file_name, columns, data_list, **field_choice_sr):
    '''

    :param file_name:
    :param columns:
    :param data_list:
    :param field_choice_sr:
    :return:
    '''
    x_io = BytesIO()
    work_book = xlsxwriter.Workbook(x_io)
    work_sheet = work_book.add_worksheet()
    field_index = list(columns.keys())
    work_sheet.write_row('A1', ('#', *list(columns.values())))
    row_num = 1
    for data_dict in data_list:
        row_data = []
        for f in field_index:
            sr = field_choice_sr.get(f)
            if sr:
                cell_data = sr.get(str(data_dict[f]))
            else:
                cell_data = data_dict.get(f)
            row_data.append(cell_data)
        work_sheet.write_row(row_num, 0, (row_num, *row_data))
        row_num += 1
    work_book.close()
    res = HttpResponse()
    res['Content-Type'] = 'application/octet-stream'
    res['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(file_name))
    res.write(x_io.getvalue())
    return res


def combineQueryValues(values, foundations):
    '''
    :param values: 由ORM values方法查询出的一组或多组结果，转化成列表传入
    :param foundations:  合并依据，values中的查询字段名，转化成列表传入，列表长度与values的长度要一致
    :return:
    '''
    import collections
    value_found_dict_list = []
    length = len(values)
    for i in range(1, length):
        found = foundations[i]
        value_dict_list = values[i]
        value_found_dict = collections.OrderedDict()
        for value_dict in value_dict_list:
            value_found_dict[value_dict[found]] = value_dict
        value_found_dict_list.append(value_found_dict)
    ret = []
    for value in values[0]:
        tmp = value
        for i in range(1, length):
            data = value_found_dict_list[i - 1].get(value[foundations[0]], {})
            tmp = {**tmp, **data}
            ret.append(tmp)
    return ret


def cleanCompanyName(string):
    return string.strip().replace('(', '（').replace(')', '）')


class FakeRequest():
    def __init__(self, method, **kwargs):
        self.method = method.upper()


class XadminExtraAction:
    def parse_extra_action(self, extra_action):
        self.list_display = [*self.list_display, 'Action']
        self.action_tag = []
        permitted_url_names = self.request.session.get('permitted_url_names')
        for url_name, text in extra_action.items():
            if self.user.is_superuser or url_name in permitted_url_names:
                self.action_tag.append('<a href="' + reverse(url_name) + '?pk={0}">' + text + '</a>')

    def Action(self, instance):
        if self.action_tag:
            pk = str(instance.id)
            a_tags = ''
            for a in self.action_tag:
                a_tags += a.format(pk)
            return mark_safe(a_tags)
        else:
            return ''


class SingleDimensionalTable(UserList):
    def __init__(self, field_name_list, *row_data):
        super.__init__(self, None)
        self.fields = field_name_list
        self.row_data = row_data
        self._dict_list = None
        pass

    @property
    def dict_list(self):
        if not self._dict_list is None:
            return self._dict_list
        else:
            ret = []
            for row in self.row_data:
                ret.append({self.fields[i]: row[i].strip() for i in range(len(self.fields))})
                pass
            return


def reverseDictKeyValue(dic):
    ret = {}
    for k, v in dic.items():
        ret[v] = k
    return ret