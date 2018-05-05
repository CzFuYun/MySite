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


def getCustomerDepositAmount(customer_id_list, group_by_dict, date_range):
    pass


