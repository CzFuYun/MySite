import json
from decimal import Decimal
from django.shortcuts import render, HttpResponse
from root_db import models as rd_models
from deposit_and_credit import models as dac_models, models_operation
from django.db.models import Q, Sum
from django.utils.timezone import datetime, timedelta
from app_permission.views import checkPermission
# import collections



@checkPermission
def viewOverViewBranch(request):
    if request.method == 'GET':
        strDataDate = models_operation.getNeighbourDate(rd_models.DividedCompanyAccount)
        return render(request, 'deposit_and_credit/dcindex.html', {'data_date': strDataDate})


def ajaxOverViewBranch(request, *args):
    if request.method == 'POST':
        try:
            nDays = int(request.POST.get('days'))
        except:
            nDays = 30
        strStart = str(models_operation.ImportantDate().today - timedelta(days=nDays))
        qsDepositAmountEveryDay = rd_models.DividedCompanyAccount.objects.filter(
            data_date__gte=strStart).values_list('data_date').annotate(Sum('divided_amount')).order_by('data_date')
        qsBasicDepositAmountEveryDay = rd_models.DividedCompanyAccount.objects.filter(
            data_date__gte=strStart, rate_type=3).values_list('data_date').annotate(Sum('divided_amount')).order_by(
            'data_date')
        qsDepositYearlyAvgEveryDay = rd_models.DividedCompanyAccount.objects.filter(
            data_date__gte=strStart).values_list('data_date').annotate(Sum('divided_yd_avg')).order_by('data_date')
        dicChartElement = {'label': [], 'value': {'对公存款总余额': [], '其中基础型余额': [], '_对公存款当年年日均': []}}
        for i in range(0, len(qsDepositAmountEveryDay)):
            dicChartElement['label'].append(str(qsDepositAmountEveryDay[i][0]))
            dicChartElement['value']['对公存款总余额'].append(qsDepositAmountEveryDay[i][1] / 10000)
            dicChartElement['value']['其中基础型余额'].append(qsBasicDepositAmountEveryDay[i][1] / 10000)
            dicChartElement['value']['_对公存款当年年日均'].append(qsDepositYearlyAvgEveryDay[i][1] / 10000)
        return HttpResponse(json.dumps(dicChartElement))


def ajaxAnnotateDeposit(request):
    '''

    :param request:
    :param group_by: 'department__caption', 'customer__industry__caption', 'customer__has_credit'
    :return:
    '''
    if request.method == 'POST':
        strDataDate = models_operation.getNeighbourDate(rd_models.DividedCompanyAccount)
        strGroupBy = request.POST.get('group_by')
        dicChartElement = {'label': [], 'value': []}
        qs = None
        if strGroupBy.count('department'):
            qs = rd_models.DividedCompanyAccount.objects.filter(
                Q(data_date=strDataDate) & ~Q(department__caption='NONE')
            ).values_list(strGroupBy).annotate(Sum('divided_yd_avg')).order_by('department__built_order')
        elif strGroupBy.count('industry') or strGroupBy.count('has_credit') or strGroupBy.count('customer_type') or\
                strGroupBy.count('deposit_type'):
            qs = rd_models.DividedCompanyAccount.objects.filter(
                Q(data_date=strDataDate)).values_list(strGroupBy).annotate(Sum('divided_yd_avg'))
        for i in range(0, len(qs)):
            dicChartElement['label'].append(qs[i][0])
            dicChartElement['value'].append(qs[i][1] / 10000)
        return HttpResponse(json.dumps(dicChartElement))


@checkPermission
def viewContribution(request):
    method = request.method
    if method == 'GET':
        return render(request, 'deposit_and_credit/contribution.html', {'department': request.user_dep})
    elif method == 'POST':
        opener_params = {}
        for k, v in request.POST.items():
            opener_params[k] = v
        opener_params['department'] = request.department
        opener_params['data_date'] = models_operation.getNeighbourDate(dac_models.Contributor, date_str=opener_params.get('data_date'))
        customer_types = []
        if opener_params.get('gov'):
            customer_types.append('平台')
        if opener_params.get('no_gov'):
            customer_types.append('非平台')
        # if opener_params.get('no_gov_sme'):
        #     customer_types.append('实体企业（小微）')
        return render(request, 'deposit_and_credit/contribution_table.html', {
            'content_title': '{customer_type}  贡献度一览（数据日期：{data_date}）'.format(
                customer_type='+'.join(customer_types),
                data_date=opener_params['data_date']),
            'opener_params': json.dumps(opener_params),
        })



def ajaxContribution(request):
    data_date = request.POST.get('data_date', None) or models_operation.ImportantDate().last_data_date_str(dac_models.Contributor)
    try:
        tree = dac_models.ContributionTrees.objects.filter(data_date=data_date).values_list('contribution_tree')[0][0]
    except:
        temp = models_operation.getContributionTree(data_date)
        tree = json.dumps(temp)
        dac_models.ContributionTrees(data_date=data_date, contribution_tree=tree).save()
    return HttpResponse(tree)


def ajaxDeptOrder(request):
    depts = rd_models.Department.objects.values_list('code').order_by('display_order')
    ordered_depts = []
    for i in depts:
        ordered_depts.append(i[0])
    return HttpResponse(json.dumps(ordered_depts))

########################################################################################################################


@checkPermission
def viewCustomerContributionHistory(request):
    if request.method == 'GET':
        return render(request, 'deposit_and_credit/customer_contribution_history.html', {'opener_params': json.dumps({'null': 'null'})})
    elif request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        daily_deposit_amounts = models_operation.getCustomerDailyDataForHighChartsLine([customer_id], rd_models.DividedCompanyAccount, 'divided_amount', 'deposit_type__caption')
        daily_saving_amounts = models_operation.getCustomerDailyDataForHighChartsLine([customer_id], dac_models.Contributor, 'saving_amount', 'customer__name')
        daily_deposit_amounts.extend(daily_saving_amounts)
        return HttpResponse(json.dumps(daily_deposit_amounts))


@checkPermission
def viewSeriesContributionHistory(request):
    if request.method == 'GET':
        return render(request, 'deposit_and_credit/series_contribution_history.html', {'opener_params': json.dumps({'null': 'null'})})
    elif request.method == 'POST':
        series_code = request.POST.get('series_code')
        series_caption = request.POST.get('series_caption')
        series_company_id_qs = rd_models.Series.objects.get(code=series_code).accountedcompany_set.values_list('customer_id')
        series_company_id_list = []
        for i in series_company_id_qs:
            series_company_id_list.append(i[0])
            # customer_deposit_daily_amount = rd_models.DividedCompanyAccount.objects.filter(customer_id=customer_id).values_list('data_date').annotate(Sum('divided_amount')).order_by('data_date')
        daily_deposit_amounts = models_operation.getCustomerDailyDataForHighChartsLine(
            series_company_id_list,
            rd_models.DividedCompanyAccount,
            'divided_amount',
            'customer__name')
        daily_saving_amounts = models_operation.getCustomerDailyDataForHighChartsLine(
            series_company_id_list,
            dac_models.Contributor,
            'saving_amount')
        daily_deposit_amounts.extend(daily_saving_amounts)
        return HttpResponse(json.dumps(daily_deposit_amounts))


def ajaxCustomerCreditHistory(request):
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        daily_credit_amounts = models_operation.getCustomerDailyDataForHighChartsLine([customer_id], dac_models.Contributor, 'net_total', 'customer__name')
        return HttpResponse(json.dumps(daily_credit_amounts))



def viewDepartmentContributionHistory(request):
    if request.method == 'GET':
        return  render(request, 'deposit_and_credit/department_contribution_history.html')
    elif request.method == 'POST':
        dept_code = request.POST.get('dept_code')
        customers_qs = dac_models.Contributor.objects.filter(
            department=dept_code,
            data_date=models_operation.ImportantDate().last_data_date_str(dac_models.Contributor)
        ).values_list('customer_id')
        dept_customers = []
        for i in customers_qs:
            dept_customers.append(i[0])
        dept_deposit = models_operation.getCustomerDailyDataForHighChartsLine(dept_customers, rd_models.DividedCompanyAccount, 'divided_amount')
        dept_credit = dac_models.Contributor.objects.filter(department=dept_code, data_date__gte='2018-03-31').values_list(
            'data_date',
            'customer__name',
            'customer__industry__caption',
            'customer__series__caption',
            'customer__series__gov_plat_lev',
            'invest_banking',
            'net_total',
            'loan_rate',
            'saving_amount',
        ).order_by('data_date')
        series_by_date = {}
        for i in dept_credit:
            date = str(i[0])
            customer = i[1]
            if date not in series_by_date:
                series_by_date[date] = {}
            if customer not in series_by_date[date]:
                series_by_date[date][customer] = []
            for j in range(2, len(i)):
                series_by_date[date][customer].append(float(i[j]) if type(i[j]) == Decimal else i[j])
        return HttpResponse(json.dumps(series_by_date))