import json, os
# import datetime as python_datetime
from decimal import Decimal
from django.shortcuts import render, HttpResponse, redirect, reverse, render_to_response
from django.db.models import Q, Sum, F
# from django.forms.models import model_to_dict
from django.utils.timezone import datetime, timedelta
# from MySite import utilities
from root_db import models as rd_models
from deposit_and_credit import models as dac_models, models_operation, settings
from app_permission.views import checkPermission
from MySite import utilities
# import collections



@checkPermission
def viewOverViewBranch(request):
    block = request.POST.get('block')
    if block == 'body':
        strDataDate = models_operation.getNeighbourDate(rd_models.DividedCompanyAccount)
        return render_to_response('overview/dcindex_body.html', {'data_date': strDataDate})
    if block == 'js':
        return render_to_response('overview/dcindex_js.html')
    if block == 'css':
        return render_to_response('overview/dcindex_css.html')

def ajaxOverViewBranch(request, *args):
    if request.method == 'POST':
        try:
            nDays = int(request.POST.get('days'))
        except:
            nDays = 30
        strStart = str(models_operation.DateOperation().today - timedelta(days=nDays))
        qsDepositAmountEveryDay = rd_models.DividedCompanyAccount.objects.filter(
            data_date__gte=strStart).values_list('data_date').annotate(Sum('divided_amount')).order_by('data_date')
        qsBasicDepositAmountEveryDay = rd_models.DividedCompanyAccount.objects.filter(
            data_date__gte=strStart, rate_type=3).values_list('data_date').annotate(Sum('divided_amount')).order_by(
            'data_date')
        qsDepositYearlyAvgEveryDay = rd_models.DividedCompanyAccount.objects.filter(
            data_date__gte=strStart).values_list('data_date').annotate(Sum('divided_yd_avg')).order_by('data_date')
        dicChartElement = {'label': [], 'value': {'对公存款总余额': [], '其中基础型余额': [], '_对公存款当年年日均': []}}
        for i in range(0, len(qsDepositAmountEveryDay)):
            dicChartElement['label'].append(str(qsDepositAmountEveryDay[i][0]))
            dicChartElement['value']['对公存款总余额'].append(qsDepositAmountEveryDay[i][1] / 10000)
            dicChartElement['value']['其中基础型余额'].append(qsBasicDepositAmountEveryDay[i][1] / 10000)
            dicChartElement['value']['_对公存款当年年日均'].append(qsDepositYearlyAvgEveryDay[i][1] / 10000)
        return HttpResponse(json.dumps(dicChartElement))


def ajaxAnnotateDeposit(request):
    '''

    :param request:
    :param group_by: 'department__caption', 'customer__industry__caption', 'customer__has_credit'
    :return:
    '''
    if request.method == 'POST':
        strDataDate = models_operation.getNeighbourDate(rd_models.DividedCompanyAccount)
        strGroupBy = request.POST.get('group_by')
        dicChartElement = {'label': [], 'value': []}
        qs = None
        if strGroupBy.count('department'):
            qs = rd_models.DividedCompanyAccount.objects.filter(
                Q(data_date=strDataDate) & ~Q(department__caption='NONE')
            ).values_list(strGroupBy).annotate(Sum('divided_yd_avg')).order_by('department__display_order')
        elif strGroupBy.count('industry') or strGroupBy.count('has_credit') or strGroupBy.count('customer_type') or\
                strGroupBy.count('deposit_type'):
            qs = rd_models.DividedCompanyAccount.objects.filter(
                Q(data_date=strDataDate)).values_list(strGroupBy).annotate(Sum('divided_yd_avg'))
        for i in range(0, len(qs)):
            dicChartElement['label'].append(qs[i][0])
            dicChartElement['value'].append(qs[i][1] / 10000)
        return HttpResponse(json.dumps(dicChartElement))


@checkPermission
def viewContribution(request):
    block = request.POST.get('block')
    if block == 'css':
        return HttpResponse('')
    if block == 'body':
        data_date = models_operation.DateOperation().last_data_date_str(dac_models.Contributor)
        return render_to_response('contrib/contribution_body.html', {'department': request.user_dep, 'data_date': data_date})
    if block == 'js':
        return render_to_response('contrib/contribution_js.html')


def viewContributionTable(request):
    if request.method == 'POST':
        opener_params = {}
        for k, v in request.POST.items():
            opener_params[k] = v
        # opener_params['department'] = request.department
        opener_params['data_date'] = models_operation.getNeighbourDate(dac_models.Contributor,
                                                                       date_str=opener_params.get('data_date'))
        customer_types = []
        if opener_params.get('gov'):
            customer_types.append('平台')
        if opener_params.get('no_gov'):
            customer_types.append('非平台')
        # if opener_params.get('no_gov_sme'):
        #     customer_types.append('实体企业（小微）')
        return render(request, 'contrib/contribution_table.html', {
            'content_title': '{customer_type}  贡献度一览（数据日期：{data_date}）'.format(
                customer_type='+'.join(customer_types),
                data_date=opener_params['data_date']),
            'opener_params': json.dumps(opener_params),
            'data_date': opener_params['data_date'],
            'department_list': rd_models.Department.getBusinessDept(utilities.return_as['choice']),
        })


def ajaxContribution(request):
    data_date = request.POST.get('data_date', None) or models_operation.DateOperation().last_data_date_str(dac_models.Contributor)
    try:
        tree = dac_models.ContributionTrees.objects.filter(data_date=data_date).values_list('contribution_tree')[0][0]
    except:
        temp = models_operation.getContributionTree(data_date)
        tree = json.dumps(temp)
        dac_models.ContributionTrees(data_date=data_date, contribution_tree=tree).save()
    return HttpResponse(tree)


def ajaxDeptOrder(request):
    depts = rd_models.Department.objects.values_list('code', 'caption').order_by('display_order')
    ordered_depts = {}
    for i in depts:
        ordered_depts[i[0]] = i[1]
    return HttpResponse(json.dumps(ordered_depts))


def ajaxStaff(request):
    dept_code = request.POST.get('dept_code')
    staff_qs = rd_models.Staff.objects.filter(sub_department__superior=dept_code).values_list('staff_id', 'name').order_by('name')
    staffs = {}
    if staff_qs:
        for i in staff_qs:
            staffs[i[0]] = i[1]
    return HttpResponse(json.dumps(staffs))

########################################################################################################################


@checkPermission
def viewCustomerContributionHistory(request):
    if request.method == 'GET':
        return render(request, 'contrib/customer_contribution_history.html', {'opener_params': json.dumps({'null': 'null'})})
    elif request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        daily_deposit_amounts = models_operation.getCustomerDailyDataForHighChartsLine([customer_id], rd_models.DividedCompanyAccount, 'divided_amount', 'deposit_type__caption')
        daily_saving_amounts = models_operation.getCustomerDailyDataForHighChartsLine([customer_id], dac_models.Contributor, 'saving_amount', 'customer__name')
        daily_deposit_amounts.extend(daily_saving_amounts)
        return HttpResponse(json.dumps(daily_deposit_amounts))


@checkPermission
def viewSeriesContributionHistory(request):
    if request.method == 'GET':
        return render(request, 'contrib/series_contribution_history.html', {'opener_params': json.dumps({'null': 'null'})})
    elif request.method == 'POST':
        series_code = request.POST.get('series_code')
        series_caption = request.POST.get('series_caption')
        series_company_id_qs = rd_models.Series.objects.get(code=series_code).accountedcompany_set.values_list('customer_id')
        series_company_id_list = []
        for i in series_company_id_qs:
            series_company_id_list.append(i[0])
            # customer_deposit_daily_amount = rd_models.DividedCompanyAccount.objects.filter(customer_id=customer_id).values_list('data_date').annotate(Sum('divided_amount')).order_by('data_date')
        daily_deposit_amounts = models_operation.getCustomerDailyDataForHighChartsLine(
            series_company_id_list,
            rd_models.DividedCompanyAccount,
            'divided_amount',
            'customer__name')
        daily_saving_amounts = models_operation.getCustomerDailyDataForHighChartsLine(
            series_company_id_list,
            dac_models.Contributor,
            'saving_amount')
        daily_deposit_amounts.extend(daily_saving_amounts)
        return HttpResponse(json.dumps(daily_deposit_amounts))


def ajaxCustomerCreditHistory(request):
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        daily_credit_amounts = models_operation.getCustomerDailyDataForHighChartsLine([customer_id], dac_models.Contributor, 'net_total', 'customer__name')
        return HttpResponse(json.dumps(daily_credit_amounts))



def viewDepartmentContributionHistory(request):
    if request.method == 'GET':
        return  render(request, 'contrib/department_contribution_history.html')
    elif request.method == 'POST':
        dept_code = request.POST.get('dept_code')
        customers_qs = dac_models.Contributor.objects.filter(
            department=dept_code,
            data_date=models_operation.DateOperation().last_data_date_str(dac_models.Contributor)
        ).values_list('customer_id')
        dept_customers = []
        for i in customers_qs:
            dept_customers.append(i[0])
        dept_deposit = models_operation.getCustomerDailyDataForHighChartsLine(dept_customers, rd_models.DividedCompanyAccount, 'divided_amount')
        dept_credit = dac_models.Contributor.objects.filter(department=dept_code, data_date__gte='2018-03-31').values_list(
            'data_date',
            'customer__name',
            'customer__industry__caption',
            'customer__series__caption',
            'customer__series__gov_plat_lev',
            'invest_banking',
            'net_total',
            'loan_rate',
            'saving_amount',
        ).order_by('data_date')
        series_by_date = {}
        for i in dept_credit:
            date = str(i[0])
            customer = i[1]
            if date not in series_by_date:
                series_by_date[date] = {}
            if customer not in series_by_date[date]:
                series_by_date[date][customer] = []
            for j in range(2, len(i)):
                series_by_date[date][customer].append(float(i[j]) if type(i[j]) == Decimal else i[j])
        return HttpResponse(json.dumps(series_by_date))

# @checkPermission
def viewExpirePrompt(request):
    # imp_date = models_operation.DateOperation()
    # expire_before = imp_date.delta_date(60)
    block = request.POST.get('block')
    if block == 'body':
        return render_to_response('expire/expire_body.html')
    if block == 'js':
        return render_to_response('expire/expire_js.html')


def viewExpirePromptTable(request):
    if request.method == 'GET':
        filter_dict = request.GET
        filter_condition = '{'
        for f in filter_dict:
            if len(filter_dict.getlist(f)) <= 1:
                filter_condition += ('"' + f + '":"' + filter_dict[f] + '",')
            else:
                filter_condition += ('"' + f + '":"' + str(filter_dict.getlist(f)) + '",')
        filter_condition += '}'
        return render(request, 'expire/expire_table.html', {'filter': filter_condition})
    elif request.method == 'POST':
        imp_date = models_operation.DateOperation()
        data_date_str = imp_date.last_data_date_str(dac_models.Contributor)
        today = imp_date.today
        data_date = datetime.strptime(data_date_str, '%Y-%m-%d').date()
        expire_id = Q(id=request.POST.get('expire_id')) if request.POST.get('expire_id') else Q(id__gt=0)
        is_finished = True if request.POST.get('is_finished') == '1' else False
        if is_finished:
            finish_after = Q(
                finish_date__gte=request.POST.get('finish_after') if request.POST.get('finish_after') else '1990-01-01')
            finish_before = Q(
                finish_date__lte=request.POST.get('finish_before') if request.POST.get('finish_before') else str(today))
        else:
            finish_after = Q(finish_date__isnull=True)
            finish_before = Q(finish_date__isnull=True)
        expire_after = Q(expire_date__gte=request.POST.get('expire_after') if request.POST.get('expire_after') else str(
            data_date - timedelta(days=100)))
        expire_before = Q(
            expire_date__lte=request.POST.get('expire_before') if request.POST.get('expire_before') else str(
                today + timedelta(days=180)))
        has_punishment = Q(punishment__gt=0) if '1' in request.POST.getlist('has_punishment') else Q(punishment=0)
        non_punishment = Q(punishment=0) if '0' in request.POST.getlist('has_punishment') else Q(punishment__gt=0)
        expire_qs = dac_models.ExpirePrompt.objects.filter(
            expire_id, expire_after & expire_before, has_punishment | non_punishment, finish_after & finish_before
        ).values_list(
            'customer_id',
            'id',
            'remark',
            'punishment',
            'staff_id',
            'finish_date',
            'expire_date',
            'staff_id__yellow_red_card',
            'staff_id__red_card_expire_date',
        )
        expire_customers = []
        customer_expire_data_dict = {}
        for i in expire_qs:
            customer_id = i[0]
            expire_customers.append(customer_id)
            customer_expire_data_dict[customer_id] = [
                i[1],
                i[2],
                i[3],
                i[4],
                i[5],
                i[6],
                i[7],
                i[8],
            ]
        customer_qs = dac_models.Contributor.objects.filter(
            customer_id__in=expire_customers,
            data_date=data_date_str
        ).values_list(
            'customer_id',
            'customer__name',
            'department_id',
            'department__caption',
            'staff_id',
            'staff__name',
            'expire_date',
        ).order_by('department__display_order', 'staff__name', 'expire_date')
        ret = []
        display_num = 0
        for i in customer_qs:
            display_num += 1
            customer_id = i[0]
            staff_id = i[4]
            staff_name = i[5]
            staff_id_in_expire_prompt = customer_expire_data_dict[customer_id][3]
            expire_date = customer_expire_data_dict[customer_id][5]
            if staff_id_in_expire_prompt != staff_id and staff_id_in_expire_prompt:
                staff_id = staff_id_in_expire_prompt
                staff_name = rd_models.Staff.objects.filter(staff_id=staff_id_in_expire_prompt)[0].name
            # print(customer_id)
            # if customer_id == '0000000001581675':
            #     print('')
            tmp = {
                'display_num': display_num,
                'expire_prompt_id': customer_expire_data_dict[customer_id][0],
                'customer_id': customer_id,
                'customer_name': i[1],
                'dept_id': i[2],
                'dept_caption': i[3],
                'staff_id': staff_id,
                'staff_name': staff_name,
                'expire_date': str(expire_date) if expire_date else str(i[6]),
                'days_remain': ((i[6] if i[6] else expire_date) - today).days,
                'remark': customer_expire_data_dict[customer_id][1],
                'punishment': customer_expire_data_dict[customer_id][2],
                'finish_date': str(customer_expire_data_dict[customer_id][4]),
                'yellow_red_card': customer_expire_data_dict[customer_id][6],
                'red_card_expire_date': str(customer_expire_data_dict[customer_id][7]),
            }
            ret.append(tmp)
        return HttpResponse(json.dumps(ret))


def editExpirePrompt(request):
    ajax_result = {
        'success': False,
        'error': None,
    }
    expire_id = request.POST.get('expire_id')
    q = dac_models.ExpirePrompt.objects.filter(id=expire_id)
    if q[0].finish_date:
        ajax_result['error'] = '已办结，不可编辑'
    else:
        file_obj = request.FILES.get('explain')
        if file_obj:
            file_full_name = os.path.join(settings.EXPIRE_EXPLAIN_IMG_FOLDER, file_obj.name)
            try:
                tmp_file = open(file_full_name)
            except:
                with open(file_full_name, 'wb') as f:
                    for i in file_obj:
                        f.write(i)
                q.update(**{'explain': file_obj.name})
                ajax_result['success'] = True
            else:
                tmp_file.close()
                ajax_result['success'] = False
                ajax_result['error'] = '已存在同名文件'
                return HttpResponse(json.dumps(ajax_result))
        expire_dict = {}
        expire_dict['expire_date'] = request.POST.get('expire_date')
        expire_dict['staff_id'] = request.POST.get('staff')
        expire_dict['punishment'] = int(request.POST.get('punishment'))
        expire_dict['remark'] = request.POST.get('remark')
        if q.update(**expire_dict):
            ajax_result['success'] = True and (ajax_result['success'] or not file_obj)
    return HttpResponse(json.dumps(ajax_result))


def viewExpireExplain(request):
    ajax_result = {
        'success': False,
        'data': None,
        'error': None,
    }
    expire_id = request.POST.get('expire_prompt_id')
    q = dac_models.ExpirePrompt.objects.filter(id=expire_id)
    if q:
        file_name = q[0].explain
        if file_name:
            ajax_result['data'] = file_name
            ajax_result['success'] = True
        else:
            ajax_result['error'] = '未上传情况说明'
    else:
        ajax_result['error'] = '记录不存在'
    return HttpResponse(json.dumps(ajax_result))


def finishExpirePrompt(request):
    ajax_result = {
        'success': False,
        'error': None,
    }
    expire_prompt_id = request.POST.get('expire_prompt_id')
    q = dac_models.ExpirePrompt.objects.filter(id=expire_prompt_id)[0]
    if q and not q.finish_date:
        today = models_operation.DateOperation().today
        q.finish_date = today
        q.save()
        if q.punishment:
            staff = q.staff_id
            staff.setYellowRedCard()
        ajax_result['success'] = True
        return HttpResponse(json.dumps(ajax_result))
    else:
        ajax_result['error'] = '不可重复办结'
        return HttpResponse(json.dumps(ajax_result))


def resetRedCard(request):
    ajax_result = {
        'success': False,
        'error': None,
    }
    staff_id = request.POST.get('staff_id')
    if staff_id:
        staff = rd_models.Staff.objects.filter(staff_id=staff_id)
        if staff.exists():
            red_card_expire_date = staff.values('red_card_expire_date')[0]['red_card_expire_date']
            if red_card_expire_date < models_operation.DateOperation().today:
                staff[0].resetRedCard()
                ajax_result['success'] = True
            else:
                ajax_result['error'] = 'Do NOT cheat me'
        else:
            ajax_result['error'] = '无员工信息'
    else:
        ajax_result['error'] = '未能获取工号'
    return HttpResponse(json.dumps(ajax_result))




