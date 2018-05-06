import json
from django.db.models import Sum
from django.utils.timezone import timedelta, datetime
from deposit_and_credit import models as dac_models
from root_db import models as rd_models

class ImportantDate():
    def __init__(self):
        self.today = datetime.today().date()

    @property
    def today_str(self):
        return str(self.today)

    @property
    def last_year_num(self):
        return self.today.year - 1

    def last_data_date_str(self, model_class, field='data_date'):
        return getNeighbourDate(model_class, -1, self.today_str, field)


def getNeighbourDate(model_class, search_type=0, date_str=None, field='data_date'):
    '''

    :param model_class:一个model类
    :param date_str:
    :param search_type:小于零向前获取，大于零向后获取；默认为零，双向查找，获取最近的数据日期
    :param field:
    :return:日期字符串
    '''

    if date_str:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        imp_date = ImportantDate()
        date_obj = imp_date.today
        date_str = str(date_obj)
    before_date = after_date = None
    retry = False
    if search_type >= 0:
        try:
            after_date = model_class.objects.filter(**{field + '__gte': date_str}).values_list(field).order_by(field).first()[0]
        except:
            retry = True
    if search_type <= 0 or retry:
        before_date = model_class.objects.filter(**{field + '__lte': date_str}).values_list(field).order_by('-' + field).first()[0]
    if before_date and after_date:
        delta_before = (date_obj - before_date).days
        delta_after = (after_date - date_obj).days
        ret_dict = {
            delta_before: before_date,
            delta_after: after_date
        }
        return str(ret_dict[min(delta_before, delta_after)])
    else:
        return str(before_date or after_date)


def getContributionTree(data_date):
    last_year_str = str(ImportantDate().last_year_num)
    last_year_yd_avg = rd_models.DividedCompanyAccount.objects.filter(
        data_date=last_year_str + '-12-31').values_list(
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


def getCustomerDepositAmountsForHighChartsLine(customer_id_list, group_by=None, start_date=None, end_date=None):
    '''

    :param customer_id_list:
    :param group_by: 'deposit_type__caption'
    :param start_date:
    :param end_date:
    :return: {Group1: [(####-##-##, xxxx.xx), (####-##-##, xxxx.xx), ...], Group2: []}
    '''
    if not end_date:
        end_date = ImportantDate().last_data_date_str(rd_models.DividedCompanyAccount)
    if not start_date:
        start_date = str(ImportantDate().today - timedelta(days=365))
    if len(customer_id_list) == 1:      # 若只查一个客户，将存款按参数指定的方式进行分类
        groups = []
        if group_by:
            group_qs = rd_models.DividedCompanyAccount.objects.filter(customer_id__in=customer_id_list)\
                .values_list(group_by).distinct().order_by(group_by)
            for i in group_qs:
                groups.append(i[0])


        else:
            pass
    else:       # 若查询多个客户，将存款按客户进行分类
        group_by = 'customer__name'
        pass


