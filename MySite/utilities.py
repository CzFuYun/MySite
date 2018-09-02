import os, json, datetime, decimal, re, xlsxwriter
from django.http import StreamingHttpResponse, FileResponse
from django import forms
from django.shortcuts import HttpResponse, render_to_response

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

def fileDownload(file_full_name):
    # save_path = 'C:\\Users\\hp\\Downloads'
    file_name = file_full_name.replace(os.path.join(os.path.dirname(file_full_name),''),"")
    with open(file_full_name, 'rb') as f:
        response = FileResponse(f)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
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


def downloadWorkbook(file_name, columns, query_set):
    from io import BytesIO
    from django.utils.encoding import escape_uri_path
    from django.shortcuts import HttpResponse
    data = query_set.values_list(*list(columns.keys()))
    x_io = BytesIO()
    work_book = xlsxwriter.Workbook(x_io)
    work_sheet = work_book.add_worksheet()
    work_sheet.write_row('A1', (*['#'], *list(columns.values())))
    row_num = 1
    for row_data in data:
        work_sheet.write_row(row_num, 0, (*[row_num], *row_data))
        row_num += 1
    work_book.close()
    res = HttpResponse()
    res['Content-Type'] = 'application/octet-stream'
    res['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(file_name))
    res.write(x_io.getvalue())
    return res
