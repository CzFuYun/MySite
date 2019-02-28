from django.shortcuts import render

# Create your views here.
from .crp import CrpHttpRequest
from .models import LuLedger, CpLedger

def test(request):
    # http://127.0.0.1:8000/scrape/test
    # req = CrpHttpRequest()
    # req.login()
    # p = req.getQiDai('客户编号')
    # for i in p:
    #     print(i)
    # LuLedger.fillInfo()
    crp = CrpHttpRequest()
    crp.login()
    reply_date__gte = '2018-01-01'
    sme_cp = crp.getCsCp(
        *['客户名称', '客户编号', '授信编号', '批复时间', '批复编号', '授信到期时间', '客户经理'],
        **{
            '授信额度(元)': crp.NumCondition.gt(0),
            '批复时间': crp.DateCondition.between(reply_date__gte, crp.data_date),
        }
    )
    for p in sme_cp:
        pass