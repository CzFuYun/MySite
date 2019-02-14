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
    CpLedger.bulkCreateFromCrp('2018-02-14')