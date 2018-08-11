import os, json, datetime, decimal
from django.http import StreamingHttpResponse, FileResponse
from django.shortcuts import HttpResponse

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


def calHtmlFormMargin(sizeX, sizeY, screenX, screenY):
    marginX = (int(screenX) - int(sizeX)) / 2
    marginY = (int(screenY) - int(sizeY)) / 2
    return {
        'marginX': marginX,
        'marginY': marginY
    }
