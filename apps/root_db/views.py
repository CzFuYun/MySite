from django.shortcuts import render
import json

from django.views.generic import View
from django.db.models import Q
from django.shortcuts import HttpResponse

from .models import AccountedCompany, Staff


def test(request):
    # http://127.0.0.1:8000/rd/test

    # from scraper.dcms_request import DcmsHttpRequest
    # dcms = DcmsHttpRequest()
    # dcms.login()
    # AccountedCompany.fillDcmsInfo(dcms=dcms)

    pass


class CustomerDeptView(View):
    def get(self, request):
        ret = []
        companies = AccountedCompany.objects.filter(Q(sub_dept__isnull=False) | Q(staff__isnull=False)).values(
            'customer_id',
            'name',
            'staff__sub_department__caption',
            'staff__sub_department__superior__caption',
            'sub_dept__caption',
            'sub_dept__superior__caption',
            'belong_to',
        ).order_by('sub_dept__superior__display_order', 'staff')
        for c in companies:
            tmp = []
            tmp.append(c['customer_id'])
            tmp.append(c['name'])
            if c['belong_to'] == 0:
                tmp.append(c['sub_dept__caption'])
                tmp.append(c['sub_dept__superior__caption'])
            elif c['belong_to'] == 1:
                tmp.append(c['staff__sub_department__caption'])
                tmp.append(c['staff__sub_department__superior__caption'])
            ret.append(tmp)
        return HttpResponse(ret)