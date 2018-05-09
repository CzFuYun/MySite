from django.shortcuts import render, reverse
from app_permission import views, settings
from root_db import models_operation


def login(request):
    return views.login(request)


@views.checkPermission
def home(request):
    return render(request, settings.HOME_PAGE)


def test(request):
    file_name = '/home/fuyun/下载/A-存款.xlsm'
    table_name = '@AccountedCompany'
    table_head_row = 3
    last_row = 6991
    models_operation.updateOrCreateCompany(file_name, table_name, table_head_row, last_row)