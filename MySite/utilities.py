import os, json, datetime, decimal
from django.http import StreamingHttpResponse, FileResponse
from django.shortcuts import HttpResponse, render_to_response

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