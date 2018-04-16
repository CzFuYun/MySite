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
    return render(request, 'deposit_and_credit/contribution.html')








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
    dicFilterCondition = {strField + ('__lte' if before else '__gte') : strDate}
    strOrderBy = ('-' if before else '') + strField     # 若向前搜索，则将得到的日期降序排列；否则升序
    return str(clsModel.objects.values(strField).filter(**dicFilterCondition).order_by(strOrderBy)[0][strField])
strLastDataDate = getAdjacentDataDate(rd_models.DividedCompanyAccount)
last_year_last_day = str(dtToday.year - 1) + '-12-31'
CONTRIBUTION_TREE = {}

def getContributionTree(data_date):

    # ↓[('0', 1641), ('0000000000000148', 31), ('0000000000375597', 15), ('0000000001308901', 741), ('0000000001417720', 907), ('0000000001507517', 0), ('0000000001580919', 542), ('0000000001580920', 161335), ('0000000001580921', 0), ('0000000001580924', 72), ('0000000001580926', 1002), ('0000000001580927', 3), ('0000000001580929', 2001), ('0000000001580930', 800), ('0000000001580931', 155187), ('0000000001580932', 22332), ('0000000001580933', 16512), ('0000000001580934', 20000), ('0000000001580937', 522), ('0000000001580939', 1), '...(remaining elements truncated)...']
    last_year_yd_avg = rd_models.DividedCompanyAccount.objects.filter(data_date=last_year_last_day).values_list('customer__customer_id').annotate(Sum('divided_yd_avg'))
    last_year_yd_avg_dict = {}
    for i in last_year_yd_avg:
        last_year_yd_avg_dict[i[0]] = i[1]
    # ↓[('0', 490, -1891), ('0000000000000148', 56, 94), ('0000000000375597', 15, 15), ('0000000001308901', 746, 748), ('0000000001417720', 2141, 3276), ('0000000001507517', 0, 0), ('0000000001580919', 549, 553),
    last_deposit = rd_models.DividedCompanyAccount.objects.filter(data_date=strLastDataDate).values_list('customer__customer_id').annotate(Sum('divided_yd_avg'), Sum('divided_amount'))
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
    for contrib in contrib_qs:
        cust = contrib.customer
        customer_id = contrib.customer_id
        series_code = cust.series.code
        dep_code = contrib.department.code
        temp = {
            customer_id: {
                'name': cust.name,
                'series_code': series_code,
                'series_caption': cust.series.caption,
                'gov_plat_lev': cust.series.gov_plat_lev_id,
                'department_caption': contrib.department.caption,
                'department_code': dep_code,
                'line': contrib.approve_line,
                'defuse': contrib.defuse_expire,
                'last_year_yd_avg_deposit': last_year_yd_avg_dict.get(customer_id, 0),
                'deposit_yd_avg': last_deposit_dict.get(customer_id, {}).get('yd_avg', 0),
                'deposit_amount': last_deposit_dict.get(customer_id, {}).get('amount', 0),
                'industry': cust.industry.caption,
                'loan': contrib.loan,
                'loan_rate': contrib.loan_rate,
                'loan_interest': contrib.loan_interest,
                'lr_bab': contrib.lr_BAB,
                'invest_banking': contrib.invest_banking,
            }
        }
        try:
            contrib_tree[dep_code]['series_customer_data'][series_code].append(temp)
        except:
            contrib_tree[dep_code]['series_customer_data'][series_code] = []
            contrib_tree[dep_code]['series_customer_data'][series_code].append(temp)
    return contrib_tree


if not CONTRIBUTION_TREE:
    print('CONTRIBUTION_TREE = getContributionTree(strLastDataDate)')
    CONTRIBUTION_TREE = getContributionTree(strLastDataDate)
    print(CONTRIBUTION_TREE)