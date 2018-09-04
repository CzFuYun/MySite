import xlrd, json
from root_db import  models
from django.utils.timezone import timedelta, datetime


NEED_UPDATE_STAFF_INFORMATION = True
NEED_UPDATE_ALL_COMPANIES_INFORMATION = False


########################################################################################################################
def createOrUpdateStaff(staff_id, name, sub_department_caption):
    try:
        staff_obj = models.Staff.objects.filter(staff_id=staff_id)
        staff_qs = staff_obj.values_list('name', 'sub_department__caption')[0]
    except:     # 若不存在该员工
        try:
            sub_department_obj = models.SubDepartment.objects.get(caption=sub_department_caption)
        except:
            print('*' * 50)
            print('Create Staff 【%s-%s】  Failed,department 【%s】 Not Exists.' % (staff_id, name, sub_department_caption))
            print('*' * 50)
        else:
            if sub_department_obj.staff_set.create(staff_id=staff_id, name=name):
                print('New Added Staff【%s-%s】' % (staff_id, name))
            else:
                print('*' * 50)
                print('Failed to Add Staff 【%s-%s】' % (staff_id, name))
                print('*' * 50)
    else:       # 若存在该员工
        if not NEED_UPDATE_STAFF_INFORMATION:
            return
        name_in_db = staff_qs[0]
        sub_department_in_db = staff_qs[1]
        if sub_department_in_db != sub_department_caption or name_in_db != name:
            prompt = ('''Staff【%s-%s】 U insert is Not consistent with the DbRecord 【%s-%s】 . Please Choose:
                0.Ignore
                1.Update Name
                2.Update Department
                3.Both 1 and 2'''
            ) % (name, sub_department_caption, name_in_db, sub_department_in_db)
            choice = input(prompt)
            if choice == '1' or choice == '3':
                staff_obj.update(name=name)
            if choice == '2' or choice == '3':
                try:
                    sub_department_id = models.SubDepartment.objects.get(caption=sub_department_caption).sd_code
                    staff_obj.update(sub_department_id=sub_department_id)
                except:
                    print('*' * 50)
                    print('Update Staff【%s-%s】 Failed,department 【%s】 Not Exists.' % (staff_id, name, sub_department_caption))
                    print('*' * 50)
########################################################################################################################
def getSimpleSerializationRule(model_class_used_to_serialize, primary_key_field='id', caption_field='caption', fk_field=''):
    '''
    返回简单序列化规则的字典，用于提取公司累客户类型、行业、规模，及员工部门名称与编码间的映射关系
    :param model_class_used_to_serialize: LIKE models.CustomerType
    :param primary_key: 'id','code'...
    :param caption_field:
    :param fk_field:该序列化规则的外键约束字段，例如，sub_department有个上级部门的外键约束'superior_id'
    :return:
    '''
    filter_fields = [caption_field, primary_key_field]
    if(fk_field):
        filter_fields.append(fk_field)
    serialization = model_class_used_to_serialize.objects.values_list(*filter_fields)
    serialization_rule_dict = {}
    for i in serialization:
        if fk_field:
            serialization_rule_dict[i[0]] = [i[1], i[2]]
        else:
            serialization_rule_dict[i[0]] = i[1]
    return serialization_rule_dict

def getXlDataForOrmOperation(file_name, table_name, table_head_row=1, last_row=0, extra_fileds_kvp=None):
    '''

    :param file_name:
    :param table_name:
    :param table_head_row:
    :param extra_fileds_kvp: 在excel表现有字段外，还需要添加的自定义字段及默认值，在最终return的数据结构中，将带有这些字段
    :return:
    '''
    work_book = xlrd.open_workbook(file_name)
    work_sheet = work_book.sheet_by_name(table_name)
    table_head_data = work_sheet.row_values(table_head_row - 1)
    ret_list = []
    db_fields = []      # excel列名及数据列号组成的列表，其中列名与数据库表中的各字段名一致
    c = 0
    for col in table_head_data:
        if len(str(col)):
            db_fields.append((c, col))
        c += 1
    if extra_fileds_kvp:
        for extra_filed in extra_fileds_kvp:
            db_fields.append((-1, extra_filed))
    total_rows = work_sheet.nrows
    if last_row == 0:
        last_row = total_rows
    for row_num in range(table_head_row, last_row):
        row_data = work_sheet.row_values(row_num)
        row_data_dict = {}
        for col in db_fields:
            if col[0] >= 0:
                cell_value = row_data[col[0]]
                if len(str(cell_value)):
                    if type(cell_value) == float and cell_value == int(cell_value):
                        row_data_dict[col[1]] = int(cell_value)
                    else:
                        row_data_dict[col[1]] = cell_value
            else:
                row_data_dict[col[1]] = extra_fileds_kvp[col[1]]
        ret_list.append(row_data_dict)
    return ret_list

def updateOrCreateCompany(file_name):
    global NEED_UPDATE_ALL_COMPANIES_INFORMATION
    all_sr_dict = {}
    all_sr_dict['district_id'] = getSimpleSerializationRule(models.District)
    all_sr_dict['customer_type_id'] = getSimpleSerializationRule(models.CustomerType)
    all_sr_dict['scale_id'] = getSimpleSerializationRule(models.Scale)
    all_sr_dict['industry_id'] = getSimpleSerializationRule(models.Industry, 'code')
    all_sr_dict['type_of_3311_id'] = getSimpleSerializationRule(models.TypeOf3311)
    data_source_list = getXlDataForOrmOperation(file_name, '@AccountedCompany', 1, 0)
    data_for_bulk_create = []
    for data_dict in data_source_list:
        customer_obj = models.AccountedCompany.objects.filter(customer_id=data_dict['customer_id'])
        if customer_obj.exists() and not NEED_UPDATE_ALL_COMPANIES_INFORMATION:
            continue
        for field in data_dict:
            field_sr = all_sr_dict.get(field)
            if field_sr:        # 若该字段有序列化规则
                value_before_serialize = data_dict[field]
                data_dict[field] = field_sr[value_before_serialize]
        if not customer_obj.exists():
            data_for_bulk_create.append(models.AccountedCompany(**data_dict))
            # models.AccountedCompany.objects.create(**data_dict)
            print('Ready To Add Customer:' + data_dict['name'])
        elif NEED_UPDATE_ALL_COMPANIES_INFORMATION:
            customer_obj.update(**data_dict)
            print('Update Customer:' + data_dict['name'])
        else:
            print(data_dict['name'], 'Already exists')
    while True:
        print('Try To Add New Customers...')
        try:
            models.AccountedCompany.objects.bulk_create(data_for_bulk_create)
        except:
            ipt = input('>>>Error,Retry? <y/n>')
            if ipt == 'n':
                break
        else:
            print('Add New Customers Successfully')
            break

def createDividedCompanyAccount(file_name):
    data_date = input('>>>data_date?')
    all_sr_dict = {}
    all_sr_dict['sub_department_id'] = getSimpleSerializationRule(models.SubDepartment, 'sd_code', 'caption', 'superior')
    all_sr_dict['deposit_type_id'] = getSimpleSerializationRule(models.DepositType)
    all_sr_dict['deposit_type_id'] = getSimpleSerializationRule(models.DepositType)
    all_sr_dict['rate_type_id'] = getSimpleSerializationRule(models.RateType)
    all_sr_dict['acc_status_id'] = getSimpleSerializationRule(models.AccountStatus)
    data_source_list = getXlDataForOrmOperation(file_name, '@DividedCompanyAccount', 1, 0, {'department_id': '', 'data_date': data_date})
    data_for_bulk_create = []
    for data_dict in data_source_list:
        for field in data_dict:
            # value_before_serialize = data_dict[field]
            field_sr = all_sr_dict.get(field)
            if field_sr:
                value_before_serialize = data_dict[field]
                if field == 'sub_department_id':
                    data_dict[field] = field_sr[value_before_serialize][0]
                    data_dict['department_id'] = field_sr[value_before_serialize][1]
                else:
                    data_dict[field] = field_sr[value_before_serialize]
        data_for_bulk_create.append(models.DividedCompanyAccount(**data_dict))
    models.DividedCompanyAccount.objects.bulk_create(data_for_bulk_create)

def createContributorAndUpdateSeries(file_name):
    from deposit_and_credit import models as m
    data_date_str = input('>>>data_date?')
    data_date = datetime.strptime(data_date_str, '%Y-%m-%d').date()
    expire_data_for_bulk_create = []
    expire_data_qs = m.ExpirePrompt.objects.filter(
        expire_date__gte=str(data_date - timedelta(days=180))
    ).values_list('customer_id', 'expire_date')
    customer_expire_dict = {}
    for expire_data in expire_data_qs:
        customer_expire_dict[expire_data[0]] = expire_data[1]
    all_sr_dict = {}
    all_sr_dict['series_id'] = getSimpleSerializationRule(models.Series, 'code', 'caption')
    all_sr_dict['department_id'] = getSimpleSerializationRule(models.Department, 'code', 'caption')
    all_sr_dict['staff_id'] = getSimpleSerializationRule(models.Staff, 'staff_id', 'name')
    data_source_list = getXlDataForOrmOperation(file_name, '@Contributor', 1, 0, {'data_date': data_date_str})
    contributors_for_bulk_create = []
    for data_dict in data_source_list:
        customer_id = data_dict['customer_id']
        if customer_id == 0 or len(str(customer_id)) == 0:
            continue
        # ↓更新系列信息
        series_id = all_sr_dict['series_id'][data_dict.pop('series_id')]        # 在贡献度数据库表里并没有这个字段，要删掉(用pop方法删，返回被删掉的kvp的v)，以防创建数据库记录时报错
        customer_obj = models.AccountedCompany.objects.get(customer_id=customer_id)
        old_series_id = customer_obj.series_id
        if old_series_id != series_id:
            customer_obj.series_id = series_id
            customer_obj.save(force_update=True)
            print('Update %s series from %s to %s' % (customer_obj.name, old_series_id, series_id))
        for field in data_dict:
            field_value = data_dict[field]
            if field_value:
                field_sr = all_sr_dict.get(field)
                if field_sr:
                    data_dict[field] = field_sr[field_value]
        contributors_for_bulk_create.append(m.Contributor(**data_dict))
        # ↓建立到期提醒
        try:
            expire_date = datetime.strptime(data_dict.get('expire_date'), '%Y-%m-%d').date()
        except:
            pass
        else:
            expire_date_str = str(expire_date)
            if customer_id not in customer_expire_dict:     #customer_expire_dict.get(customer_id) != expire_date_str:     # 若到期提醒的数据库里不存在该提醒信息
                if expire_date - timedelta(days=120) <= data_date and expire_date + timedelta(days=180) >= data_date:
                    expire_data_for_bulk_create.append(m.ExpirePrompt(**{
                        'customer_id': customer_id,
                        'expire_date': expire_date_str,
                        'staff_id': all_sr_dict['staff_id'].get(data_dict.get('staff_id')),
                    }))
    m.Contributor.objects.bulk_create(contributors_for_bulk_create)
    if expire_data_for_bulk_create:
        m.ExpirePrompt.objects.bulk_create(expire_data_for_bulk_create)