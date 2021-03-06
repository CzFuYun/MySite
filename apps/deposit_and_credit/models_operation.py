import json, datetime as pydate
from django.db.models import Sum
from django.utils.timezone import timedelta, datetime


class DateOperation():
    def __init__(self):
        self.today = datetime.today().date()

    @property
    def today_str(self):
        return str(self.today)

    @property
    def last_year_num(self):
        return self.today.year - 1

    @property
    def last_year_today(self):
        year = self.today.year - 1
        if year / 4 == 0  and year / 100 != 0:
            days = 366
        else:
            days = 365
        return self.today - timedelta(days=days)

    @property
    def this_year_start_date_str(self):
        return str(self.today.year) + '-01-01'

    @property
    def this_year_start_date(self):
        return self.strToDate(self.this_year_start_date_str)

    @property
    def this_year_end_date_str(self):
        return str(self.today.year) + '-12-31'

    @property
    def this_year_end_date(self):
        return self.strToDate(self.this_year_end_date_str)

    def month_first_date(self, year=None, month=None):
        if not year:
            year = self.today.year
        if not month:
            month = self.today.month
        s = str(year) + '-' + str(month) + '-01'
        return datetime.strptime(s, '%Y-%m-%d').date()

    def month_last_date(self, year=None, month=None):
        if not year:
            year = self.today.year
        if not month:
            month = self.today.month
        day = self.judgeMonthDays(year, month)
        s = str(year) + '-' + str(month) + '-' + str(day)
        return datetime.strptime(s, '%Y-%m-%d').date()

    @staticmethod
    def judgeMonthDays(year, month):
        if month == 2:
            if year % 4 == 0 and year % 100:
                days = 29
            else:
                days = 28
        elif month in (1, 3, 5, 7, 8, 10, 12):
            days = 31
        else:
            days = 30
        return days

    def strToDate(self, s):
        return datetime.strptime(s, '%Y-%m-%d').date()

    def date_dif(self, date1, date2=None):
        # 两日期相差天数 date1 - date2
        d1 = self.strToDate(date1) if type(date1) == str else date1
        d2 = self.today if date2 == None else (self.strToDate(date2) if type(date2) == str else date2)
        date_dif = d1 - d2
        return date_dif.days

    def month_count(self, date1, date2):
        # 计算相差月数 date1 - date2
        d1 = self.strToDate(date1) if type(date1) == str else date1
        d2 = self.strToDate(date2) if type(date2) == str else date2
        assert d1 >= d2
        delta_year = d1.year - d2.year
        delta_month = d1.month - d2.month
        return delta_year * 12 + delta_month + (1 if d1.day > d2.day else 0)

    def delta_date(self, days, date=''):
        if date:
            if type(date) == str:
                date_obj = self.strToDate(date)
            else:
                date_obj = date
        else:
            date_obj = self.today
        return date_obj + timedelta(days=days)

    def month_and_date(self, date):
        month = '{:0>2d}'.format(date.month)
        day = '{:0>2d}'.format(date.day)
        return month + '-' + day

    def first_data_date_str(self, model_class, field='data_date'):
        return getNeighbourDate(model_class, 1, '1900-01-01', field)

    def last_data_date_str(self, model_class, field='data_date', returnMode='s'):
        d = getNeighbourDate(model_class, -1, self.today_str, field)
        if returnMode == 's':
            return d
        elif returnMode == 'd':
            return self.strToDate(d)

    def month_dif(self, month, start_date=None):
        '''
        计算起始日期加上或减去相应月份数后的日期，若该日期不存在，如：2018-02-29，则转为当月末日期
        :param start_date: 起始日期
        :param month: 月份数，可正负
        :return:
        '''
        start_date = start_date if not start_date is None else self.today
        start_date = self.strToDate(start_date) if type(start_date) == str else start_date
        start_year = start_date.year
        start_month = start_date.month
        if start_month + month <= 0 or start_month + month > 12:
            result_year = int(month / 12) + start_year
            result_month = start_month + month % 12
        else:
            result_year = start_year
            result_month = start_month + month
        result_day = start_date.day
        if result_day > 28:
            result_day = self.judgeMonthDays(result_year, result_month)
        return pydate.date(result_year, result_month, result_day)

    def neighbour_date_date_str(self, model_class, date_str, field='data_date'):
        return getNeighbourDate(model_class, 0, date_str, field)


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
        imp_date = DateOperation()
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
        try:
            before_date = model_class.objects.filter(**{field + '__lte': date_str}).values_list(field).order_by('-' + field).first()[0]
        except:
            before_date = None
    if before_date and after_date:
        delta_before = (date_obj - before_date).days
        delta_after = (after_date - date_obj).days
        ret_dict = {
            delta_before: before_date,
            delta_after: after_date
        }
        ret = ret_dict[min(delta_before, delta_after)]
    else:
        ret = before_date or after_date
    return str(ret) if ret else ret


def getContributionTree(data_date):
    from root_db.models import DividedCompanyAccount, Department
    from deposit_and_credit.models import Contributor
    last_year_str = str(DateOperation().last_year_num)
    last_year_yd_avg = DividedCompanyAccount.objects.filter(
        data_date=last_year_str + '-12-31').values_list(
        'customer__customer_id').annotate(Sum('divided_yd_avg'))
    last_year_yd_avg_dict = {}
    for i in last_year_yd_avg:
        last_year_yd_avg_dict[i[0]] = i[1]
    last_deposit = DividedCompanyAccount.objects.filter(data_date=data_date).values_list(
        'customer__customer_id').annotate(Sum('divided_yd_avg'), Sum('divided_amount'))
    last_deposit_dict= {}
    for i in last_deposit:
        last_deposit_dict[i[0]] = {'yd_avg': i[1], 'amount': i[2]}

    contrib_tree = {}
    dep_qs = Department.objects.all().order_by('display_order')
    for dep in dep_qs:
        contrib_tree[dep.code] = {
            'department_caption': dep.caption,
            'department_code': dep.code,
            'series_customer_data': {}
        }
    contrib_qs = Contributor.objects.filter(data_date=data_date).prefetch_related('customer')
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
                'saving_yd_avg': int(contrib.saving_yd_avg),
                'invest_expire': str(contrib.invest_expire or ''),
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



def getCustomerDailyDataForHighChartsLine(customer_id_list, model_class, annotate_field, group_by=None, start_date=None, end_date=None):
    '''

    :param customer_id_list:
    :param model_class:models.DividedCompanyAccount /   models.Contributor
    :param group_by: 'deposit_type__caption'    /   'customer__name'    ...
    :param annotate_field:'divided_amount'  /   'saving_amount' ...
    :param start_date:
    :param end_date:
    :return: {Group1: [(####-##-##, xxxx.xx), (####-##-##, xxxx.xx), ...], Group2: []}
    '''
    imp_date = DateOperation()
    end_date = end_date or imp_date.last_data_date_str(model_class)
    start_date = start_date or getNeighbourDate(model_class, date_str=str(imp_date.delta_date(-365,end_date)))
    deposit_qs = model_class.objects.filter(customer_id__in=customer_id_list, data_date__gte=start_date, data_date__lte=end_date)
    if group_by:
        deposit_qs = deposit_qs.values_list('data_date', group_by)
    else:
        deposit_qs = deposit_qs.values_list('data_date')
    deposit_qs = deposit_qs.annotate(Sum(annotate_field)).order_by('data_date')
    date_group_amounts = []
    for i in deposit_qs:        # deposit_qs:[(datetime.date(2017, 11, 10), '对公定期存款', 10274), (datetime.date(2017, 11, 10), '对公活期存款', 335), (datetime.date(2017, 11, 10), '对公通知存款', 27553),
        temp = []
        for j in i:     # i:(datetime.date(2017, 11, 10), '对公定期存款', 10274)
            try:
                -j
            except:
                temp.append(str(j))
            else:
                temp.append(int(j))
        date_group_amounts.append(temp)
    return date_group_amounts

def getCustomerCreditAndIbDataForHighChartsLine(customer_id_list, model_class, annotate_field, group_by=None, start_date=None, end_date=None):

    pass