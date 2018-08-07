import json, pickle
from django.shortcuts import render, HttpResponse, render_to_response
from django.db.models import Q, F, Sum
from . import models
from . import models_operation as mo
from deposit_and_credit import models_operation, models as dac_m
from MySite import utilities
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
    models.ProjectExecution.takePhoto(None, '2018-08-01')
    return


def viewProjectRepository(request):
    block = request.POST.get('block')
    if block == 'body':
        imp_date = models_operation.DateOperation()
        wangji_start = str(imp_date.today.year) + '-10-01'
        wangji_end = str(imp_date.today.year + 1) + '-03-31'
        if imp_date.date_dif(imp_date.today, wangji_start) >= 0 and imp_date.date_dif(imp_date.today, wangji_end) <= 0:
            start_date = wangji_start
            end_date = wangji_end
        else:
            start_date = imp_date.this_year_start_date_str
            end_date = imp_date.this_year_end_date_str
        return render_to_response('proj_rep/project_body.html', locals())
    if block == 'js':
        return render_to_response('proj_rep/project_js.html')

def selectProjectAction(request):
    action = request.POST.get('action')
    if action == '1':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        return render(request, 'proj_rep/project_summary.html', {'opener_params': json.dumps({'start_date': start_date, 'end_date': end_date})})
    elif action == '2':
        viewProjectExeDetail(request)
    elif action == '3':
        pass
    elif action == '4':
        pass

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
        'current_progress__status_num',
        'current_progress__caption',
        'new_net_used',
    )
    project_exe = {}
    for exe in exe_data:
        project_exe[exe['project_id']] = {
            **exe
        }
    project_data = models.ProjectRepository.objects.filter(
        (Q(reply_date__isnull=True) | Q(reply_date__gte=start_date) | Q(create_date__gte=start_date))
        & Q(create_date__lte=end_date)
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
    dept = rd_m.Department.getBusinessDept()
    business_list = models.Business.getAllBusiness()
    projects_structure_data = {}
    for d in dept:
        dept_caption = d[1]
        if dept_caption not in projects_structure_data:
            projects_structure_data[dept_caption] = {}
            for b in business_list:
                projects_structure_data[dept_caption][b] = {}
                projects_structure_data[dept_caption][b]['target'] = target_task[dept_caption].get(b, {'计划金额': 0})
                projects_structure_data[dept_caption][b]['projects'] = []
    for p in project_data:
        dept_caption = p['staff__sub_department__superior__caption']
        business_caption = p['business__superior__caption']
        p_id = p['id']
        project = {**p, **project_exe[p_id]}
        projects_structure_data[dept_caption][business_caption]['projects'].append(project)
    table_col = {     # 项目储备汇总表的列
        business_list[0]: (     # 授信
            ('计划户数',   ['{target}["计划户数"]'], ),
            ('已预审',     ['{project}["current_progress__status_num"] in range(20,100)', '{project}["account_num"]', '0'], ),
            ('实绩户数',   ['{project}["current_progress__status_num"]>=100', '{project}["account_num"]', '0'], ),
            ('计划金额',   ['{target}["计划金额"]'], ),
            ('待投放',     ['{project}["current_progress__status_num"] in range(100,200)', '{project}["new_net"]-{project}["new_net_used"]', '0'], ),
            ('实绩金额',   ['{project}["current_progress__status_num"]>100', '{project}["new_net_used"]', '0'], ),
        ),
        business_list[1]: (     # 投行业务
            ('计划金额', ['{target}["计划金额"]'], ),
            ('分行',     ['{project}["current_progress__status_num"] in range(20,85)', '{project}["new_net"]', '0'], ),
            ('总行',     ['{project}["current_progress__status_num"] in range(85,100)', '{project}["new_net"]', '0'], ),
            ('待投放',   ['{project}["current_progress__status_num"] in range(100,200)', '{project}["new_net"]-{project}["new_net_used"]', '0'], ),
            ('实绩',     ['{project}["current_progress__status_num"]>100', '{project}["new_net_used"]', '0'], ),
        ),
        business_list[2]: (     # 直融
            ('计划金额', ['{target}["计划金额"]'], ),
            ('储备',     ['{project}["current_progress__status_num"] in range(20,100)', '{project}["new_net"]', '0'], ),
            ('待投放',   ['{project}["current_progress__status_num"]>=100', '{project}["new_net"]-{project}["new_net_used"]', '0'], ),
            ('实绩',     ['{project}["current_progress__status_num"]>100', '{project}["new_net_used"]', '0'], ),
        ),
        business_list[3]: (     # 监管
            ('计划金额', ['{target}["计划金额"]'], ),
            ('储备',     ['{project}["current_progress__status_num"] in range(20,100)', '{project}["new_net"]', '0'], ) ,
            ('已签协议', ['{project}["current_progress__status_num"]>=100', '{project}["new_net"]-{project}["new_net_used"]', '0'] ),
        ),
    }
    project_summary_table_rows = []
    for d in dept:
        if not projects_structure_data.get(d[1]):
            print('')
        l = []
        for b in business_list:
            cal_rule = table_col[b]
            dept_business_target = projects_structure_data[d[1]][b]['target']       # 不可删，用到这个变量的
            dept_business_projects = projects_structure_data[d[1]][b]['projects']
            for cr in cal_rule:
                c = str(cr[1][0])
                if '{target}' in c:
                    l.append(eval(cr[1][0].format(target='dept_business_target')))
                elif '{project}' in c:
                    cell_sum = 0
                    for p in dept_business_projects:
                        _if = cr[1][0].format(project='p')
                        _then = cr[1][1].format(project='p')
                        _else = cr[1][2].format(project='p')
                        if eval(_if):
                            cell_sum += eval(_then)
                        else:
                            cell_sum += eval(_else)
                    l.append(cell_sum)
        project_summary_table_rows.append(l)
    return HttpResponse(json.dumps(
        {
            'department': dept,
            'business': business_list,
            'table_col': table_col,
            'rows': project_summary_table_rows,
            'detail': projects_structure_data
        }, cls=utilities.JsonEncoderExtend))


def viewProjectExeDetail(request):
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    detail_aggregate = request.POST.get('detail_aggregate')







    return render(request, 'proj_rep/project_exe_detail.html', locals())


def getProjectDetails():
    pass


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

# def ajaxTarget(request):
#     if request.method == 'POST':
#         start_date = request.POST.get('start_date')
#         end_date = request.POST.get('end_date')
#         ret = mo.getTarget(start_date, end_date)
#         return HttpResponse(json.dumps(ret))

