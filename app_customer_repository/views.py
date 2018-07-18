from django.shortcuts import render
from . import models
from deposit_and_credit import models_operation
# Create your views here.

ALLOW_EDIT = False

def test(request):
    # http://139.17.1.35:8000/cr/test
    # c = models.CustomerRepository.objects.filter(name__contains='经济发展')[0]
    # b = models.SubBusiness.objects.filter(caption='承销')[0]
    # new_p = models.ProjectRepository()
    # new_p_dict = {}
    # new_p_dict['customer'] = c
    # new_p_dict['is_green'] = False
    # new_p_dict['project_name'] = ''
    # new_p_dict['business'] = b
    # new_p_dict['total_net'] = 100000
    # new_p_dict['existing_net'] = 0
    # new_p.create_or_update(new_p_dict)
    # models.TargetTask().calculate_target('2018-01-01', '2018-06-30')
    # pr = models.ProjectRepository.objects.filter(close_date__isnull=True)
    # for i in pr:
    #     models.ProjectExecution.takePhoto(i)
    return

def viewProjectRepository(request):
    if request.method == 'GET':
        imp_date = models_operation.DateOperation()
        start_date = imp_date.this_year_start_date_str
        end_date = imp_date.this_year_end_date_str
        return render(request, 'project_repository.html', locals())
    elif request.method == 'POST':
        pass