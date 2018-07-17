from django.shortcuts import render
from . import models
# Create your views here.

ALLOW_EDIT = False

def test(request):
    # http://139.17.1.35:8000/cr/test
    c = models.CustomerRepository.objects.filter(name__contains='经济发展')[0]
    b = models.SubBusiness.objects.filter(caption='承销')[0]
    new_p = models.ProjectRepository()
    new_p_dict = {}
    new_p_dict['customer'] = c
    new_p_dict['is_green'] = False
    new_p_dict['project_name'] = ''
    new_p_dict['business'] = b
    new_p_dict['total_net'] = 100000
    new_p_dict['existing_net'] = 0
    new_p.create_or_update(new_p_dict)
    return