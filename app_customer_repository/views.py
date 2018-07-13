from django.shortcuts import render
from . import models
# Create your views here.

def test(request):
    # c = models.CustomerRepository.objects.filter(name__contains='常州市城市建设')[0]
    # new_p = models.ProjectRepository()
    # new_p.customer = c
    # new_p.is_green = False
    # new_p.project_name = ''
    # b = models.SubBusiness.objects.filter(caption='承销')[0]
    # new_p.business = b
    # new_p.total_net = 100000
    # new_p.existing_net = 0
    # new_p.calculate_acc_num()
    # new_p.create()
    pe = models.ProjectExecution.objects.get(id=1)

    return