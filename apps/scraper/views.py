from django.shortcuts import render, HttpResponse
from django.db.models import Q

from .crp import CrpHttpRequest
from .dcms_request import DcmsHttpRequest
from .models import LuLedger, CpLedger, DailyLeiShou


def test(request):
    # http://127.0.0.1:8000/scrape/test

    dcms = DcmsHttpRequest()
    dcms.login()
    no_reply = CpLedger.objects.filter(
        Q(reply_content__isnull=True) &
        (
            Q(cp_num__startswith='SME') |
            Q(cp_num__startswith='CP')
        )
    ).values(
        'pk',
        'cp_num',
        'customer__name',
    )
    count = no_reply.count()
    i = 0
    for nr in no_reply:
        i += 1
        print(i, '/', count, nr['customer__name'], nr['cp_num'])
        reply_code, reply_content = CpLedger.objects.get(pk=nr['pk']).as_dcms_work_flow(dcms).getReply()
        CpLedger.objects.filter(pk=nr['pk']).update(
            reply_code=reply_code,
            reply_content=reply_content
        )
    return HttpResponse('完成')
