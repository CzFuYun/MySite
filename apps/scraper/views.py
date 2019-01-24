from django.shortcuts import render

# Create your views here.
from .crp import CrpHttpRequest
from .models import LuLedger

def test(request):
    # req = CrpHttpRequest()
    # req.login()
    # p = req.getDtcx('客户编号')
    # for i in p:
    #     print(i)
    LuLedger.updateAmount()