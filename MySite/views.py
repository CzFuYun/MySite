from django.shortcuts import render, reverse
from app_permission import views, settings
from root_db import models_operation


def login(request):
    return views.login(request)


@views.checkPermission
def home(request):
    return render(request, settings.HOME_PAGE)


def exportAccountedCompany(request):
    file_name = r'E:\AAA报表定期更新\各项报表整理导入数据库\@AccountedCompany.xlsx'
    table_name = '@AccountedCompany'
    table_head_row = 1
    models_operation.updateOrCreateCompany(file_name, table_name, table_head_row)

def test(request):
    file_name = r'E:\AAA报表定期更新\各项报表整理导入数据库\@DividedCompanyAccount.xlsx'
    table_name = '@DividedCompanyAccount'
    table_head_row = 1
    models_operation.createDividedCompanyAccount(file_name, table_name, table_head_row)