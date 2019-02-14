import json, os, copy
# import datetime as python_datetime
from decimal import Decimal

from django.shortcuts import render, HttpResponse, redirect, reverse, render_to_response
from django.db.models import Q, Sum, F
# from django.forms.models import model_to_dict
from django.utils.timezone import datetime, timedelta

from MySite import utilities
from root_db import models as rd_models
from deposit_and_credit import models as dac_models, models_operation, settings, html_forms, table_structure
from app_permission.views import checkPermission
from scraper.models import CpLedger


def test(request):
    # http://127.0.0.1:8000/dc/test
    # dac_models.LuLedger.create('LU/CZ11/2018/03/00004849')
    # dac_models.LoanDemand.updateByLeiShou('2019-02-01')
    # dac_models.LoanDemand.linkToEpRecord('2019-02-10')
    CpLedger.bulkCreateFromCrp('2019-01-31')
    pass

def updateProgress(request):
    # http://127.0.0.1:8000/dc/progress.update
    # dac_models.ExpirePrompt.fill_cp_num()
    dac_models.ExpirePrompt.updateProgress()
    return HttpResponse('finish')

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
        return render_to_response('contrib/contribution_body.html', {'department': request.user.user_id.sub_department.superior_id, 'data_date': data_date})
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
            'user_dept': request.user.user_id.sub_department.superior_id
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


def downloadContributionData(request):
    data_date = request.GET.get('dataDate')
    dept = request.user.user_id.sub_department.superior.pk
    if dept != 'JGBS':
        q_dept = Q(department=dept)
    else:
        q_dept = Q(department__code__isnull=False)
    data_list = dac_models.Contributor.objects.filter(
        data_date=data_date,
        customer__dividedcompanyaccount__data_date=data_date
    ).filter(q_dept).annotate(
        Sum('customer__dividedcompanyaccount__divided_amount'),
        Sum('customer__dividedcompanyaccount__divided_yd_avg')
    ).order_by(
        'department__display_order',
        '-customer__series__gov_plat_lev',
        'customer__series',
    )
    return utilities.downloadWorkbook('贡献度数据' + data_date + '.xlsx', table_structure.contribution_download, data_list.values(*table_structure.contribution_download.keys()))


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
        series_company_id_qs = rd_models.Series.objects.get(code=series_code).accountedcompany_set.values_list('customer_id')
        series_company_id_list = []
        for i in series_company_id_qs:
            series_company_id_list.append(i[0])            # customer_deposit_daily_amount = rd_models.DividedCompanyAccount.objects.filter(customer_id=customer_id).values_list('data_date').annotate(Sum('divided_amount')).order_by('data_date')
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
        return render(request, 'expire/expire_frame.html', {'filter': filter_condition, 'content_title': '业务到期提示'})
    elif request.method == 'POST':
        request_dict = request.POST
        table_col = copy.deepcopy(table_structure.expire_table)
        imp_date = models_operation.DateOperation()
        data_date_str = imp_date.last_data_date_str(dac_models.Contributor)
        today = imp_date.today
        # data_date = datetime.strptime(data_date_str, '%Y-%m-%d').date()
        expire_id = Q(id=request_dict.get('expire_id')) if request_dict.get('expire_id') else Q(id__isnull=False)
        is_finished = True if request_dict.get('is_finished') == '1' else False
        if is_finished:
            finish_after = Q(
                finish_date__gte=request_dict.get('finish_after')) if request_dict.get('finish_after') else Q(finish_date__isnull=False)
            finish_before = Q(
                finish_date__lte=request_dict.get('finish_before')) if request_dict.get('finish_before') else Q(finish_date__isnull=False)
        else:
            finish_after = Q(finish_date__isnull=True)
            finish_before = Q(finish_date__isnull=True)
            table_col.pop('finish_date')
        expire_after = Q(expire_date__gte=request_dict.get('expire_after')) if request_dict.get('expire_after') else Q(id__isnull=False)
        expire_before = Q(expire_date__lte=request_dict.get('expire_before')) if request_dict.get('expire_before') else Q(id__isnull=False)
        if request_dict.get('download'):
            has_punishment_filter_condition = request_dict.getlist('has_punishment')
            if '1' in has_punishment_filter_condition and '0' in has_punishment_filter_condition:
                has_punishment = Q(punishment__gte=0)
            else:
                if '1' in has_punishment_filter_condition:
                    has_punishment = Q(punishment__gt=0)
                else:
                    has_punishment = Q(punishment=0)
        else:
            has_punishment_filter_condition = eval(request_dict.get('has_punishment'))
            if type(has_punishment_filter_condition) == int:
                if has_punishment_filter_condition:
                    has_punishment = Q(punishment__gt=0)
                else:
                    has_punishment = Q(punishment=0)
            else:
                has_punishment = Q(punishment__gte=0)
        data_list = dac_models.ExpirePrompt.objects.filter(
            expire_id, expire_after & expire_before, has_punishment, finish_after & finish_before
        ).order_by('staff_id__sub_department__superior__display_order', 'staff_id', 'apply_type', 'expire_date')
        if request_dict.get('download'):
            return utilities.downloadWorkbook('到期业务清单' + str(today) + '.xlsx', table_structure.expire_table_download, data_list.values(*table_structure.expire_table_download.keys()), **table_structure.expire_table_sr_for_download)
        else:
            data_list = data_list.values(
                'id',
                'customer__name',
                'customer_id',
                'remark',
                'punishment',
                'staff_id',
                'staff_id__name',
                'staff_id__sub_department__superior__caption',
                'staff_id__sub_department__superior__code',
                'finish_date',
                'expire_date',
                'staff_id__yellow_red_card',
                'staff_id__red_card_expire_date',
                'chushen',
                'reply',
                'current_progress__caption',
                'current_progress__status_num',
                'apply_type',
                'progress_update_date',
                'remark_update_date',
                # 'pre_approver__name',
                # 'approver__name',
            )
            return HttpResponse(json.dumps((table_col, list(table_col.keys()), list(data_list)), cls=utilities.JsonEncoderExtend))


def editExpirePrompt(request):
    form_action = editExpirePrompt.__name__
    pk = getattr(request, request.method).get('pk')
    content_title = '业务到期-详情'
    if pk:
        expire_obj = dac_models.ExpirePrompt.objects.get(id=pk)
        if expire_obj.finish_date and not request.user.is_superuser:
            return render(request, 'feedback.html', {'swal_type': 'error', 'title': '已办结，不可修改'})
        form_title = expire_obj.customer.name
        if request.method == 'GET':
            form = html_forms.ExpirePromptModelForm(instance=expire_obj)
        elif request.method == 'POST':
            old_remark = expire_obj.remark
            old_progress = expire_obj.current_progress
            form = html_forms.ExpirePromptModelForm(request.POST, instance=expire_obj)
            if form.is_valid():
                expire_obj_updated = form.save(commit=False)
                if form.cleaned_data['remark'] != old_remark:
                    today = models_operation.DateOperation().today
                    expire_obj_updated.remark_update_date = today
                    try:
                        expire_obj_updated.remark += ('<' + str(today) + '>')
                    except:
                        expire_obj_updated.remark = ''
                if form.cleaned_data['current_progress'] != old_progress:
                    expire_obj_updated.progress_update_date = models_operation.DateOperation().today
                if request.POST.get('submit_name') == 'set_finish':
                    set_finish = finishExpirePrompt(expire_obj)
                    if not set_finish['success']:
                        return render(request, 'feedback.html', {'title': set_finish['error'], 'swal_type': 'error'})
                expire_obj_updated.save()
                return render(request, 'feedback.html')
        return render_to_response('expire/expire_update_form.html', locals())


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


def finishExpirePrompt(expire_obj):
    ret = {
        'success': False,
        'error': None,
    }
    if not expire_obj.finish_date:
        today = models_operation.DateOperation().today
        expire_obj.finish_date = today
        if expire_obj.punishment >= 100 :
            staff = expire_obj.staff_id
            staff.setYellowRedCard()
        else:
            # expire_obj.punishment = 0
            expire_obj.save()
        ret['success'] = True
        return ret
    else:
        ret['error'] = '不可重复办结'
        return ret


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




