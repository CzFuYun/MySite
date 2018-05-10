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
    models_operation.updateOrCreateCompany(file_name)

def createDividedCompanyAccount(request):
    file_name = r'/home/fuyun/下载/@DividedCompanyAccount.xlsx'
    models_operation.createDividedCompanyAccount(file_name)

def exportContributorAndSeries(request):
    file_name = r'/home/fuyun/下载/@Contributor.xlsx'
    models_operation.createContributorAndUpdateSeries(file_name)

def test(request):

    pass