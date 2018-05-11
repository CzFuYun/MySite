from django.shortcuts import render, HttpResponse, reverse
from app_permission import views, settings
from root_db import models_operation


def login(request):
    return views.login(request)


@views.checkPermission
def home(request):
    return render(request, settings.HOME_PAGE)


def exportAccountedCompany(request):
    # accounted_company.export
    file_name = r'E:\AAA报表定期更新\各项报表整理导入数据库\@AccountedCompany.xlsx'
    models_operation.updateOrCreateCompany(file_name)
    print('Success')

def createDividedCompanyAccount(request):
    # divided_company_account.create
    file_name = r'E:\AAA报表定期更新\各项报表整理导入数据库\@DividedCompanyAccount.xlsx'
    models_operation.createDividedCompanyAccount(file_name)
    print('Success')

def exportContributorAndSeries(request):
    # contributor_and_series.export
    file_name = r'E:\AAA报表定期更新\各项报表整理导入数据库\@Contributor.xlsx'
    models_operation.createContributorAndUpdateSeries(file_name)
    print('Success')

def test(request):

    pass