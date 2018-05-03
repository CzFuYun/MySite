import json
from django.shortcuts import render, HttpResponse
from root_db import models as rd_models
from deposit_and_credit import models as dac_models
from django.db.models import Q, Sum
from django.utils.timezone import datetime, timedelta
from app_permission.views import checkPermission
# import collections



@checkPermission
def viewOverViewBranch(request):
    if request.method == 'GET':
        strDataDate = getAdjacentDataDate(rd_models.DividedCompanyAccount)
        return render(request, 'deposit_and_credit/dcindex.html', {'data_date': strDataDate})


def ajaxOverViewBranch(request, *args):
    if request.method == 'POST':
        try:
            nDays = int(request.POST.get('days'))
        except:
            nDays = 30
        strStart = str(dtToday - timedelta(days=nDays))
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
        strDataDate = getAdjacentDataDate(rd_models.DividedCompanyAccount)
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
        opener_params['data_date'] = getAdjacentDataDate(dac_models.Contributor, opener_params.get('data_date'))
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


def viewDepartmentContribution(request):
    pass


def ajaxContribution(request):
    data_date = request.POST.get('data_date', None) or strLastDataDate
    tree = dac_models.ContributionTrees.objects.filter(data_date=data_date).values('contribution_tree')
    if tree:
        return HttpResponse(json.dumps(tree))
    else:
        tree = json.dumps(getContributionTree(data_date))
        dac_models.ContributionTrees(data_date=data_date, contribution_tree=tree).save()
        return HttpResponse(tree)


def ajaxDeptOrder(request):
    depts = rd_models.Department.objects.values_list('code').order_by('display_order')
    ordered_depts = []
    for i in depts:
        ordered_depts.append(i[0])
    return HttpResponse(json.dumps(ordered_depts))

########################################################################################################################
dtToday = datetime.today().date()
strToday = str(dtToday)
def getAdjacentDataDate(clsModel, strDate=strToday, before=True, strField='data_date'):
    '''
    获取给定日期的最近数据日期
    :param clsModel: 一个model类
    :param strDate: 一个可以被数据库识别为日期的字符串
    :param before: True为向前获取，默认为True
    :return: 可以被数据库识别为日期的字符串
    '''
    if not strDate:
        strDate = strToday
    dicFilterCondition = {strField + ('__lte' if before else '__gte') : strDate}
    strOrderBy = ('-' if before else '') + strField     # 若向前搜索，则将得到的日期降序排列；否则升序
    return str(clsModel.objects.values(strField).filter(**dicFilterCondition).order_by(strOrderBy)[0][strField])


strLastDataDate = getAdjacentDataDate(rd_models.DividedCompanyAccount)
last_year_last_day = str(dtToday.year - 1) + '-12-31'
CONTRIBUTION_TREE = {}


def getContributionTree(data_date):
    last_year_yd_avg = rd_models.DividedCompanyAccount.objects.filter(data_date=last_year_last_day).values_list(
        'customer__customer_id').annotate(Sum('divided_yd_avg'))
    last_year_yd_avg_dict = {}
    for i in last_year_yd_avg:
        last_year_yd_avg_dict[i[0]] = i[1]
    last_deposit = rd_models.DividedCompanyAccount.objects.filter(data_date=data_date).values_list(
        'customer__customer_id').annotate(Sum('divided_yd_avg'), Sum('divided_amount'))
    last_deposit_dict= {}
    for i in last_deposit:
        last_deposit_dict[i[0]] = {'yd_avg': i[1], 'amount': i[2]}

    contrib_tree = {}
    dep_qs = rd_models.Department.objects.all().order_by('display_order')
    for dep in dep_qs:
        contrib_tree[dep.code] = {
            'department_caption': dep.caption,
            'department_code': dep.code,
            'series_customer_data': {}
        }
    contrib_qs = dac_models.Contributor.objects.filter(data_date=data_date).prefetch_related('customer')
    contributor_num = contrib_qs.count()
    for i in range(contributor_num):
        contrib = contrib_qs[i]
        cust = contrib.customer
        customer_id = contrib.customer_id
        series_code = cust.series.code
        dep_code = contrib.department.code
        gov_plat_lev = cust.series.gov_plat_lev_id
        loan = contrib.loan
        temp = {
            customer_id: {
                'cust_name': cust.name,
                'series_code': series_code,
                'series_caption': cust.series.caption,
                'gov_plat_lev': gov_plat_lev,
                'department_caption': contrib.department.caption,
                'department_code': dep_code,
                'approve_line': contrib.approve_line,
                'defuse_expire': str(contrib.defuse_expire or ''),
                'last_yd_avg': int(last_year_yd_avg_dict.get(customer_id, 0)),
                'yd_avg': int(last_deposit_dict.get(customer_id, {}).get('yd_avg', 0)),
                'deposit_amount': int(last_deposit_dict.get(customer_id, {}).get('amount', 0)),
                'industry': cust.industry.caption,
                'loan': int(loan),
                'loan_rate': float(contrib.loan_rate),
                'loan_interest': float(contrib.loan_interest),
                'net_total': int(contrib.net_total),
                'lr_BAB': int(contrib.lr_BAB),
                'invest_banking': int(contrib.invest_banking),
            }
        }
        series_key = str(gov_plat_lev) + '$' + series_code
        series_customers = contrib_tree[dep_code]['series_customer_data']
        try:
            series_customers[series_key].append(temp)
        except:
            series_customers[series_key] = []
            series_customers[series_key].append(temp)
    return contrib_tree

@checkPermission
def viewCustomerContributionHistory(request):
    customer_id = request.GET.get('customer')
    return render(request, 'deposit_and_credit/customer_contribution_history.html', {'opener_params': json.dumps({'customer_id': customer_id})})
