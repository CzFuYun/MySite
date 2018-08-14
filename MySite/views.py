import json
from django.shortcuts import render, HttpResponse, reverse, render_to_response
from root_db import models_operation
from app_permission import views, settings



def login(request):
    return views.login(request)


@views.checkPermission
def home(request):
    return render(request, settings.HOME_PAGE)


def exportAccountedCompany(request):
    # http://139.17.1.35:8000/accounted_company.export
    file_name = r'E:\AAA报表定期更新\贡献度\@AccountedCompany.xlsx'
    models_operation.updateOrCreateCompany(file_name)
    print('Success')


def createDividedCompanyAccount(request):
    # http://139.17.1.35:8000/divided_company_account.create
    file_name = r'E:\AAA报表定期更新\贡献度\@DividedCompanyAccount.xlsx'
    models_operation.createDividedCompanyAccount(file_name)
    print('Success')


def exportContributorAndSeries(request):
    # http://139.17.1.35:8000/contributor_and_series.export
    file_name = r'E:\AAA报表定期更新\贡献度\@Contributor.xlsx'
    models_operation.createContributorAndUpdateSeries(file_name)
    print('Success')

def test(request):
    pass


def convertToUrl(request):
    ajax_result = {
        'success': False,
        'data': None,
        'error': None,
    }
    url_name = request.POST.get('url_name') or request.GET.get('url_name')
    try:
        ajax_result['data'] = reverse(url_name)
        ajax_result['success'] = True
    except:
        ajax_result['error'] = '无对应url映射'
    return HttpResponse(json.dumps(ajax_result))


# def getHtmlForm(request):
#     if request.method == 'GET':
#         form_id = request.GET.get('formId') or request.GET.get('form_id')
#         form_template = {
#
#         }
#         template = form_template.get(form_id)
#         return render_to_response(template, locals())