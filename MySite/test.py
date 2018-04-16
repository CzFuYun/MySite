from root_db import models


def getAdjacentDataDate(clsModel, strDate, mode=0, strField='data_date'):
    '''
    获取给定日期的最近数据日期
    :param clsModel: 一个model类
    :param strDate: 一个可以被数据库识别为日期的字符串
    :param mode: 负数为向前获取，正数为向后获取，0为向前或向后，默认为0
    :param strField:
    :return: 可以被数据库识别为日期的字符串
    '''
    pass

    # if mode <= 0:
    #     dicCondition = {strField + '__lte': strDate}
    #     print(dicCondition)
    #     a=clsModel.objects.values_list(strField).filter(**{'data_date' + '__lte': '2018-03-09'}).order_by('-' + strField)[0]
    #     print(a)
    # if mode >= 0:
    #     dicCondition = {strField + '__gte': strDate}
    #     b=clsModel.objects.values_list(strField).filter(**{'data_date' + '__gte': '2018-03-09'}).order_by(strField)[0]
    #     print(b)


if __name__ == '__main__':
    getAdjacentDataDate(clsModel=models.DividedCompanyAccount, strDate='2018-03-25')
