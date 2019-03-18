from django.shortcuts import render, HttpResponse
from django.db.models import Q

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
    dcms = DcmsHttpRequest()
    dcms.login()
    # r = dcms.search_customer('江苏武进经济发展集团有限公司')

    # CpLedger.objects.get(cp_num='SME/CZZX05/2017/12/00002783').as_dcms_work_flow().getReplyContent()


    no_reply = CpLedger.objects.filter(
        Q(reply_content__isnull=True) &
        (
            Q(cp_num__startswith='SME') |
            Q(cp_num__startswith='CP')
        )
    )
    count = no_reply.count()
    for i in range(count):
        print(i, '/', count, no_reply[i].customer.name, no_reply[i].cp_num)
        no_reply[i].reply_code, no_reply[i].reply_content = no_reply[i].as_dcms_work_flow(dcms).getReply()
        no_reply[i].save()


    return HttpResponse('完成')
