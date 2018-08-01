import json
from django.shortcuts import render, HttpResponse, render_to_response
from django.db.models import Q, F, Sum
from . import models
from . import models_operation as mo
from deposit_and_credit import models_operation, models as dac_m
from root_db import models as rd_m
# Create your views here.

ALLOW_EDIT = False

def test(request):
    # http://139.17.1.35:8000/cr/test
    # http://127.0.0.1:8000/cr/test
    # c = models.CustomerRepository.objects.filter(name__contains='经济发展')[0]
    # b = models.SubBusiness.objects.filter(caption='承销')[0]
    # new_p_dict = {}
    # new_p_dict['customer'] = c
    # new_p_dict['is_green'] = False
    # new_p_dict['project_name'] = ''
    # new_p_dict['business'] = b
    # new_p_dict['total_net'] = 100000
    # new_p_dict['existing_net'] = 0
    # new_p = models.ProjectRepository(**new_p_dict)
    # new_p.judge_is_focus()
    # new_p.create_or_update(new_p_dict)
    # models.TargetTask().calculate_target('2018-01-01', '2018-06-30')
    # pr = models.ProjectRepository.objects.filter(close_date__isnull=True)
    # for i in pr:
    #     models.ProjectExecution.takePhoto(i)
    # start_date = '2018-01-01'
    # end_date = '2018-12-31'
    # project_qs = models.ProjectRepository.objects.filter(
    #     create_date__gte=start_date,
    #     create_date__lte=end_date,
    # ).values(
    #     'id',
    #     'staff__sub_department__superior_id',
    #     'business__superior',
    #     'business__superior__caption',
    #     'account_num',
    # )

    # models.ProjectExecution.takePhoto(None, '2018-07-19')

    return

def viewProjectRepository(request):
    if request.method == 'GET':
        imp_date = models_operation.DateOperation()
        wangji_start = str(imp_date.today.year) + '-10-01'
        wangji_end = str(imp_date.today.year + 1) + '-03-31'
        if imp_date.date_dif(imp_date.today, wangji_start) >= 0 and imp_date.date_dif(imp_date.today, wangji_end) <= 0:
            start_date = wangji_start
            end_date = wangji_end
        else:
            start_date = imp_date.this_year_start_date_str
            end_date = imp_date.this_year_end_date_str
        return render(request, 'project_repository.html', locals())


def viewProjectSummary(request):
    imp_date = models_operation.DateOperation()
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    # customer_id_list = []
    # for i in p_exe_qs:
    #     customer_id_list.append(i['project__customer__customer_id'])
    # data_date = models_operation.getNeighbourDate(dac_m.Contributor, 0, exe_date)
    # contribution = dac_m.Contributor.objects.filter(
    #     data_date=data_date,
    #     customer_id__in=customer_id_list,
    #     customer__dividedcompanyaccount__data_date=data_date,
    # ).values(
    #     'customer_id',
    #     'customer__dividedcompanyaccount__divided_yd_avg',
    # ).annotate(Sum('customer__dividedcompanyaccount__divided_yd_avg'), Sum('net_total'))
    last_photo_date = imp_date.last_data_date_str(models.ProjectExecution, 'photo_date')
    exe_date = last_photo_date if imp_date.date_dif(end_date, last_photo_date) > 0 else end_date
    exe_data = models.ProjectExecution.objects.filter(
        photo_date=exe_date
    ).values(
        'project__project_name',
        'project_id',
        'project__business__superior__caption',
        'current_progress',
        'new_net_used',
    ).order_by(
        'project__staff__sub_department__superior__display_order',
        'project__business__superior__display_order',
        # 'project__staff__staff_id',
        'current_progress__display_order',
    )
    project_exe = {}
    for exe in exe_data:
        project_exe[exe['project_id']] = {
            'project_name': exe['project__project_name'],
            'current_progress': exe['current_progress'],
            'new_net_used': exe['new_net_used'],
        }
    project_data = models.ProjectRepository.objects.filter(
        (Q(reply_date__isnull=True) | Q(reply_date__gte=start_date) | Q(create_date__gte=start_date))
        & Q(create_date__lte=end_date)
    ).order_by(
        # 'staff__sub_department__superior__display_order',
        # 'staff_id',
        # 'business__superior__display_order',
        # '-create_date',
    ).values(
            'project_name',
            'id',
            'staff__sub_department__superior__caption',
            # 'business__superior_id',
            'business__superior__caption',
            'account_num',
            'total_net',
            'existing_net',
    ).annotate(new_net=Sum(F('total_net') - F('existing_net')))
    target_task = models.TargetTask.calculate_target(start_date, end_date, None, 'dict')
    # dept = rd_m.Department.getBusinessDept()

    for p in project_data:


        pass




    return render(request, 'project_summary.html', locals())


# Progress.objects.filter(id=11).values('suit_for_business__superior__caption')
# SubBusiness.objects.filter(caption='项目贷款').values_list('progress__caption')
# ProjectRepository.objects.filter().prefetch_related('customer__customer__contributor_set')

# CustomerRepository.objects.prefetch_related(
#     'customer__contributor_set', 'projectrepository_set', 'projectrepository_set__projectexecution_set'
# ).filter(
#     customer__contributor__data_date='2018-07-18', projectrepository__projectexecution__photo_date='2018-07-18',
# ).values(
#     'name',
#     'is_strategy',
#     'customer__contributor__net_total',
#     'projectrepository__business__caption',
#     'projectrepository__projectexecution__total_used',
#     'projectrepository__projectexecution__new_net_used'
# )

def ajaxTarget(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        ret = mo.getTarget(start_date, end_date)
        return HttpResponse(json.dumps(ret))

