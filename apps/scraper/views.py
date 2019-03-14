from django.shortcuts import render, HttpResponse


from .crp import CrpHttpRequest
from .dcms_request import DcmsHttpRequest
from .models import LuLedger, CpLedger, DailyLeiShou


def test(request):
    # http://127.0.0.1:8000/scrape/test
    # req = CrpHttpRequest()
    # req.login()
    # p = req.getQiDaiLu('客户编号')
    # for i in p:
    #     print(i)
    # LuLedger.fillInfo()

    # CpLedger._bulkCreateSmeCpFromCrp('2018-01-01')
    # DailyLeiShou.getDailyLeishou('2019-03-01')
    # LuLedger.fillCpSmeDetail()


    # lu = LuLedger.objects.get(lu_num='LU/CZ01/2019/03/00001497').as_dcms_work_flow()
    # r = lu.apply_info().list_areas
    #
    # dcms = DcmsHttpRequest()
    # dcms.login()
    # r = dcms.search_customer('江苏武进经济发展集团有限公司')

    LuLedger.fillCsDetail()
    return HttpResponse('完成')