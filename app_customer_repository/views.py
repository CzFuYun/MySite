import json, re, collections
from django.views.generic import View, DetailView
from django.views.generic.edit import UpdateView
from django.shortcuts import render, HttpResponse, render_to_response, redirect, reverse
from django.db.models import Q, F, Sum
from app_customer_repository import models, models_operation as mo, html_forms
from deposit_and_credit import models_operation, models as dac_m
from MySite import utilities
from root_db import models as rd_m
# Create your views here.


ALLOW_EDIT = False

def test(request):
    # http://139.17.1.35:8000/cr/test
    # http://127.0.0.1:8000/cr/test
    print('start test')
    models.ProjectExecution.takePhoto()
    print('finish test')


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
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    if action == '1':
        return render(request, 'proj_rep/project_summary.html', {'content_title': '项目储备汇总数', 'opener_params': json.dumps({'start_date': start_date, 'end_date': end_date})})
    elif action == '2':
        content_title = '项目储备清单'
        return render(request, 'proj_rep/project_list.html', locals())
    elif action == '3':
        return downloadProjectList(start_date, end_date)
    elif action == '4':
        imp_date = models_operation.DateOperation()
        if imp_date.date_dif(imp_date.last_data_date_str(models.ProjectExecution, 'photo_date')) < 0:
            return render(request, 'feedback.html', {'title': '数据尚未就绪', 'swal_type': 'error'})
        return trackProjectExe(request)


def viewProjectSummary(request):
    imp_date = models_operation.DateOperation()
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
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
        # if dept_caption == '机关部室':
        #     print()
        business_caption = p['business__superior__caption']
        p_id = p['id']
        project = {**p, **project_exe[p_id]}
        projects_structure_data[dept_caption][business_caption]['projects'].append(project)
    table_col = {     # 项目储备汇总表的列
        business_list[0]: (     # 授信
            ('计划户数',   ['{target}["计划户数"]'], ),
            ('已预审',     ['{project}["current_progress__status_num"] in range(20,100)', 'round({project}["account_num"],2)', '0'], ),
            ('实绩户数',   ['{project}["current_progress__status_num"]>=100', 'round({project}["account_num"],2)', '0'], ),
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



def viewProjectList(request):
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    project_qs, exe_date = models.ProjectRepository.getProjectList(start_date, end_date)
    project_detail = project_qs.values(
        'id',
        'customer__name',
        'staff_id',
        'staff__name',
        'staff__yellow_red_card',
        'staff__sub_department__superior__code',
        'staff__sub_department__superior__caption',
        'business__superior_id',
        'business__superior__caption',
        'business_id',
        'business__caption',
        'total_net',
        'existing_net',
        'projectexecution__new_net_used',
        'projectexecution__current_progress__status_num',
        'projectexecution__current_progress__caption',
    ).order_by(
        'business__superior__display_order',
        'staff__sub_department__superior__display_order',
        'staff_id',
        '-projectexecution__current_progress__status_num'
    )
    buniness_summary = list(models.Business.objects.filter(
        subbusiness__projectrepository__in=project_qs,
        subbusiness__projectrepository__projectexecution__photo_date=exe_date
    ).values('id', 'caption').annotate(
        new_net_sum=Sum('subbusiness__projectrepository__total_net')-Sum('subbusiness__projectrepository__existing_net'),
        new_net_used_sum=Sum('subbusiness__projectrepository__projectexecution__new_net_used'),
    ).order_by('display_order'))
    data = []
    i = 0
    sn = 0
    business = ''
    business_list = []
    for p in project_detail:
        sn += 1
        if business != p['business__superior__caption']:
            business_list.append({'id': buniness_summary[i]['id'], 'caption': buniness_summary[i]['caption']})
            data.append(('summary', buniness_summary[i]))
            business = p['business__superior__caption']
            i += 1
        data.append(('project', {**p, **{'sn': sn}}))
    table_col = [
        {
            'index': 'sn',
            'col_name': '#',
            'width': '2%',
            'td_attr': {
                'project_id': 'id'
            }
        },
        {
            'index': 'customer__name',
            'col_name': '客户名称',
            'width': '15%',
            'td_attr': {}
        },
        {
            'index': 'staff__sub_department__superior__caption',
            'col_name': '经营单位',
            'width': '6%',
            'td_attr': {
                'dept_code': 'staff__sub_department__superior__code',
            }
        },
        {
            'index': 'staff__name',
            'col_name': '客户经理',
            'width': '6%',
            'td_attr': {
                'staff': 'staff_id',
                'yr_card': 'staff__yellow_red_card',
            }
        },
        {
            'index': 'business__caption',
            'col_name': '业务种类',
            'width': '6%',
            'td_attr': {
                'sub_business': 'business_id'
            }
        },
        {
            'index': 'projectexecution__current_progress__caption',
            'col_name': '目前进度',
            'width': '6%',
            'td_attr': {
            'status_num': 'projectexecution__current_progress__status_num'
            }
        },
        {
            'index': 'total_net',
            'col_name': '总敞口',
            'width': '8%',
            'td_attr': {
                'total_net': 'total_net'
            }
        },
        {
            'index': 'existing_net',
            'col_name': '原有敞口',
            'width': '8%',
            'td_attr': {
                'existing_net': 'existing_net'
            }
        },
        {
            'index': 'projectexecution__new_net_used',
            'col_name': '新增敞口已投',
            'width': '8%',
            'td_attr': {
                'new_net_used': 'projectexecution__new_net_used'
            }
        },
    ]
    return render_to_response('proj_rep/project_list_content.html', locals())


def addProject(request):
    form_id = 'project_adder'
    form_action = addProject.__name__
    form_title = '新增项目'
    content_title = '新增项目'
    enc_type = 'multipart/form-data'
    form_js = 'proj_rep/project_form.html'
    if request.method == 'GET':
        form = html_forms.ProjectModelForm()
    elif request.method == 'POST':
        form = html_forms.ProjectModelForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)       # commit=False生成model的实例而不提交到数据库
            project.create()
            form.save_m2m()     # 保存多对多关系，因为使用了save(commit=False)，导致多对多关系未被保存，所以保险起见加上这一句
            return render(request, 'feedback.html')
    return render(request, 'blank_form.html', locals())


class ProjectUpdateView(View):        # DetailView用于显示一个特定类型对象的详细信息。
    context_object_name = 'form'        # 指定获取的模型列表数据保存的变量名。这个变量会被传递给模板
    model = models.ProjectRepository        # 绑定数据模型
    template_name = 'blank_form.html'
    form_class = html_forms.ProjectModelForm
    # success_url = reverse('')
    fields = [
        'customer',
        'project_name',
        'staff',
        'business',
        'is_green',
        'total_net',
        'existing_net',
        'is_defuse',
        'is_pure_credit',
        'plan_pretrial_date',
        'plan_chushen',
        'plan_zhuanshen',
        'plan_xinshen',
        'plan_reply',
        'plan_luodi'
    ]

    def get_form_kwargs(self):
        pass


    # def get_context_data(self, **kwargs):
    #     pass
    #
    # def get_object(self, queryset=None):
    #     pass
    #
    # def get(self, request, *args, **kwargs):
    #     response = super(ProjectUpdateView, self).get(request, *args, **kwargs)
    #     return response


class ProjectDetailView(View):
    def get(self, *args, **kwargs):
        pass


def downloadProjectList(start_date, end_date):
    cols = collections.OrderedDict(
        **{
            'projectrepository__customer__name': '项目主体',
            'projectrepository__customer__industry__caption': '行业门类',
            'projectrepository__customer__type_of_3311__level': '3311类型',
            'projectrepository__is_green': '绿色金融',
            'projectrepository__staff__sub_department__superior__caption': '经营部门',
            'projectrepository__staff__name': '主办人员',
            'projectrepository__business__superior__caption': '业务大类',
            'projectrepository__business__caption': '具体业务',
            'projectrepository__pretrial_doc__meeting__meeting_date': '预审日期',
            'projectrepository__total_net': '总敞口',
            'projectrepository__existing_net': '存量敞口',
            'projectrepository__projectexecution__current_progress__caption': '当前进度',
            'projectrepository__projectexecution__current_progress__status_num': '进度代号',
            'projectrepository__reply_date': '批复日期',
            'projectrepository__projectexecution__new_net_used': '新增敞口投放',
            'projectrepository__is_defuse': '涉及化解',
            'projectrepository__account_num': '折算户数',
            'projectrepository__projectexecution__remark__content': '备注',
            'projectrepository__is_focus': '重点项目',
            'customer__dividedcompanyaccount__divided_amount__sum': '存款余额',
            'customer__dividedcompanyaccount__divided_yd_avg__sum': '存款日均',
        }
    )
    project_qs, exe_date = models.ProjectRepository.getProjectList(start_date, end_date)
    project_details = models.CustomerRepository.objects.prefetch_related(
        'customer__dividedcompanyaccount_set', 'projectrepository_set', 'projectrepository_set__projectexecution_set'
    ).filter(
        customer__dividedcompanyaccount__data_date=models_operation.DateOperation().neighbour_date_date_str(rd_m.DividedCompanyAccount, exe_date),
        projectrepository__projectexecution__photo_date=exe_date,
    ).order_by(
        'projectrepository__staff__sub_department__superior__display_order',
        'projectrepository__staff',
        'projectrepository__business__display_order',
    ).annotate(Sum('customer__dividedcompanyaccount__divided_amount'), Sum('customer__dividedcompanyaccount__divided_yd_avg'))
    return utilities.downloadWorkbook('项目清单\n' + start_date + '→' + end_date + '.xlsx', cols, project_details)


def trackProjectExe(request):
    if request.method == 'POST':
        content_title = '项目进度'
        return render(request, 'proj_exe/project_exe_frame.html', locals())
    elif request.method == 'GET':
        exe_qs = models.ProjectExecution.lastExePhoto().filter(
            (Q(project__tmp_close_date__isnull=True) & Q(project__close_date__isnull=True))
            & Q(current_progress__status_num__lt=200)
        ).values(
            'id',
            'project_id',
            'project__customer__name',
            'project__staff__sub_department__superior__caption',
            'project__staff__sub_department__superior__code',
            'project__staff__name',
            'project__staff_id',
            'project__staff__yellow_red_card',
            'project__business__caption',
            'project__is_focus',
            'current_progress__status_num',
            'current_progress__caption',
            'project__total_net',
            'project__existing_net',
            'new_net_used',
            'remark__content',
            'project__customer__customer_id',
            'current_progress__star__caption',
            'project__plan_pretrial_date',
            'project__plan_chushen',
            'project__plan_zhuanshen',
            'project__plan_xinshen',
            'project__plan_reply',
            'project__plan_luodi',
            'project__pre_approver__name',
            'project__pre_approver__staff_id',
            'project__approver__name',
            'project__approver__staff_id',
            'remark__create_date',
            'project__pretrial_doc__meeting__meeting_date'
        ).order_by(
            'project__staff__sub_department__superior__display_order',
            'project__staff',
            'project__business__display_order',
        )
        table_col = [
            {
                'index': None,
                'col_name': '#',
                'width': '2%',
                'td_attr': {
                    'exe_id': 'id',
                    'project_id': 'project_id',
                }
            },
            {
                'index': 'project__customer__name',
                'col_name': '客户名称',
                'width': '13%',
                'td_attr': {
                    'customer_id': 'project__customer__customer_id'
                }
            },
            {
                'index': 'project__staff__sub_department__superior__caption',
                'col_name': '经营单位',
                'width': '4%',
                'td_attr': {
                    'dept_code': 'project__staff__sub_department__superior__code',
                }
            },
            {
                'index': 'project__staff__name',
                'col_name': '客户经理',
                'width': '4%',
                'td_attr': {
                    'staff': 'project__staff_id',
                    'yr_card': 'project__staff__yellow_red_card',
                }
            },
            {
                'index': 'project__business__caption',
                'col_name': '业务种类',
                'width': '5%',
                'td_attr': {
                    # 'sub_business': 'business_id'
                }
            },
            {
                'index': 'project__pretrial_doc__meeting__meeting_date',
                'col_name': '预审日期',
                'width': '4%',
                'td_attr': {}
            },
            {
                'index': 'current_progress__caption',
                'col_name': '目前进度',
                'width': '4%',
                'td_attr': {
                    'status_num': 'current_progress__status_num',
                    'total_net': 'project__total_net',
                    'existing_net': 'project__existing_net',
                    'new_net_used': 'new_net_used',
                    'plan_20': 'project__plan_pretrial_date',
                    'plan_40': 'project__plan_chushen',
                    'plan_70': 'project__plan_zhuanshen',
                    'plan_80': 'project__plan_xinshen',
                    'plan_100': 'project__plan_reply',
                    'plan_120': 'project__plan_luodi',
                }
            },
            {
                'index': 'remark__content',
                'col_name': '备注',
                'width': '30%',
                'td_attr': {'title': 'remark__create_date'}
            },
            {
                'index': 'current_progress__star__caption',
                'col_name': 'STAR',
                'width': '4%',
                'td_attr': {
                    'is_focus': 'project__is_focus'
                }
            },
            # {
            #     'index': 'project__pre_approver__name',
            #     'col_name': '初审',
            #     'width': '4%',
            #     'td_attr': {
            #         'pre_approver': 'project__pre_approver__staff_id'
            #     }
            # },
            # {
            #     'index': 'project__approver__name',
            #     'col_name': '专审',
            #     'width': '4%',
            #     'td_attr': {
            #         'approver': 'project__approver__staff_id'
            #     }
            # },
        ]
        return render_to_response('proj_exe/project_exe_list.html', locals())


def editProjectExe(request):
    action = editProjectExe.__name__
    if request.method == 'GET':
        exe_id = request.GET.get('exeId')
        exe_obj = models.ProjectExecution.objects.filter(id=exe_id).first()
        form = html_forms.ProjectExeForm_update(instance=exe_obj)
        return render_to_response('proj_exe/ProjectExeForm_update.html', locals())
    elif request.method == 'POST':
        new_value = request.POST.dict().copy()
        exe_id = new_value.pop('id')
        project_exe = models.ProjectExecution.objects.filter(id=exe_id)[0]
        project_exe.update(new_value)
        return render(request, 'feedback.html')


def setProjectReplied(request):
    form_action = setProjectReplied.__name__
    form_title = '确认项目信息'
    if request.method == 'GET':
        exe_id = request.GET.get('exeId')
        project_id = models.ProjectExecution.objects.get(id=exe_id).project_id
        form = html_forms.ProjectModelForm_set_replied(instance=models.ProjectRepository.objects.get(id=project_id))
    elif request.method == 'POST':
        project_id = request.POST.get('id')
        project_obj = models.ProjectRepository.objects.get(id=project_id)
        form = html_forms.ProjectModelForm_set_replied(request.POST, instance=project_obj)
        # ↑若需要modelform对数据库进行数据更新，则除了POST之外，也还需要一个instance
        if form.is_valid():
            form.save()
            pe = models.ProjectExecution.objects.filter(project_id=project_id).last()
            suit_progress = models.Progress.objects.filter(status_num=100, suit_for_business=project_obj.business_id).first()
            pe.update({'current_progress': suit_progress})
            text = ''
            if form.cleaned_data['total_net'] <= project_obj.existing_net:      # 若未给予新增额度
                project_obj.close(35, 0)
                text = '但由于未新增敞口，项目已被自动屏蔽，不再展示'
            return render(request, 'feedback.html', {'text': text})
    return render(request, 'blank_form.html', locals())


def ajaxCustomer(request):
    customer_name = request.GET.get('term')
    if not re.fullmatch(r'[\u4e00-\u9fa5]{2,}', customer_name):
        return
    customer_qs = models.CustomerRepository.objects.filter(
        Q(name__contains=customer_name) | Q(simple_name__contains=customer_name) | Q(customer__name__contains=customer_name)
    ).values('id', 'name')
    ret = []
    for c in customer_qs:
        ret.append([c['id'], c['name']])
    return HttpResponse(json.dumps(ret))


def ajaxStaff(request):
    staff_name = request.GET.get('term')
    if staff_name is None:
        staffs = rd_m.Staff.getBusinessDeptStaff(return_mode=utilities.return_as['choice'])
    elif re.fullmatch(r'[\u4e00-\u9fa5]+', staff_name):
        staffs = rd_m.Staff.getBusinessDeptStaff(name_contains=staff_name, return_mode=utilities.return_as['choice'])
    else:
        return
    return HttpResponse(json.dumps(staffs))


def addCustomer(request):
    form_id = 'customer_adder'
    form_action = addCustomer.__name__
    form_title = '新增客户'
    content_title = '新增客户'
    enc_type = 'multipart/form-data'
    form_js = 'cust/customer_form_add.html'
    if request.method == 'GET':
        form = html_forms.CustomerModelForm_add()
    elif request.method == 'POST':
        form = html_forms.CustomerModelForm_add(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/feedback')
    return render(request, 'blank_form.html', locals())


def matchAccount(request):
    customer_name = request.GET.get('customerName')
    if customer_name:
        customer_list = rd_m.AccountedCompany.matchAccountByName(customer_name, utilities.return_as['choice'])
        return HttpResponse(json.dumps(customer_list))


def delProject(request):
    form_id = 'project_deler'
    form_action = delProject.__name__
    form_title = '删除项目'
    content_title = '删除项目'
    enc_type = 'multipart/form-data'
    # form_js = 'cust/customer_form_add.html'
    project_id = getattr(request, request.method).get('id')
    project = models.ProjectRepository.objects.get(id=project_id)
    if request.method == 'GET':
        form = html_forms.ProjectModelForm_del(instance=project)
        return render(request, 'blank_form.html', locals())
    elif request.method == 'POST':
        remark_content = request.POST.get('remark')
        models.ProjectExecution.objects.filter(project_id=project_id).order_by('-id').first()._update_remark(remark_content)
        if project.close(request.POST.get('close_reason'), request.POST.get('whose_matter')):       # 成功关闭项目
            return render(request, 'feedback.html')
        else:
            form = html_forms.ProjectModelForm_del(request.POST)
            form.is_valid()
            return render(request, 'blank_form.html', locals())

