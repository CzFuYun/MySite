from django.shortcuts import render, HttpResponse
from django.db.models import Q

from .crp import CrpHttpRequest
from .dcms_request import DcmsHttpRequest
from .models import LuLedger, CpLedger, DailyLeiShou


def test(request):
    # http://127.0.0.1:8000/scrape/test
    DailyLeiShou.getDailyLeishou()
    # LuLedger.fillCpSmeDetail()
    return HttpResponse('完成')
