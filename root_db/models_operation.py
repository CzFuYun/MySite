from root_db import  models

NEED_UPDATE_STAFF_INFORMATION = False
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


# def getComplexSerializationRule(model_class_used_to_serialize, primary_key_field='id', caption_field='caption', fk_field=''):


def createOrUpdateCompany(
        customer_id,    name,   need_update_this_company,
        district_sr,            customer_type_sr,           scale_sr,           industry_sr,            type_of_3311_sr,
        district='undefined',   customer_type='undefined',  scale='undefined',  industry='undefined',   type_of_3311='undefined',
        has_base_acc=False,     has_credit=False, sum_settle=0, inter_settle=0):
    '''
    创建或更新客户，在A-存款
    :param customer_id:
    :param name:
    :param district_sr = models_operation.getSimpleSerializationRule(models.District)
    :param customer_type_sr = models_operation.getSimpleSerializationRule(models.CustomerType)
    :param scale_sr = models_operation.getSimpleSerializationRule(models.Scale)
    :param industry_sr = models_operation.getSimpleSerializationRule(models.Industry, 'code')
    :param series_sr = models_operation.getSimpleSerializationRule(models.Series, 'code')
    :param type_of_3311_sr = models_operation.getSimpleSerializationRule(models.TypeOf3311)
    :param district:
    :param customer_type:
    :param scale:
    :param industry:
    :param series:
    :param type_of_3311:
    :param has_base_acc:
    :param has_credit:
    :param sum_settle:
    :param inter_settle:
    :return:
    '''
    customer_obj = models.AccountedCompany.objects.filter(customer_id=customer_id)
    is_customer_exits = customer_obj.exists()
    if not is_customer_exits or need_update_this_company or NEED_UPDATE_ALL_COMPANIES_INFORMATION:
        customer_info_dict = {
            'name': name,
            'has_base_acc': has_base_acc,
            'has_credit': has_credit,
            'sum_settle': sum_settle,
            'inter_settle': inter_settle,
            'district_id': district_sr[district],
            'customer_type_id': customer_type_sr[customer_type],
            'scale_id': scale_sr[scale],
            'industry_id': industry_sr[industry],
            'type_of_3311_id': type_of_3311_sr[type_of_3311],
        }
        if not is_customer_exits:
            customer_info_dict['customer_id'] = customer_id
            models.AccountedCompany.objects.create(**customer_info_dict)
            print('New Added Company【' + name + '】【' + customer_id + '】')
        else:
            customer_obj.update(**customer_info_dict)
            print('Update Company【' + name + '】【' + customer_id + '】')
    else:
        print('【' + name + '】【' + customer_id + '】' + 'already Exits')


def insertDividedCompanyAccount(
        customer_id, account_id, staff_id, sub_department, deposit_type, rate_type, rate, transfer_price, rate_spread,
        base_rate, floating_ratio, acc_open_date, start_date, exp_date, acc_status, data_date, divided_amount, divided_md_avg,
        divided_sd_avg, divided_yd_avg, sub_department_sr, deposit_type_sr, rate_type_sr):
    '''

    :param customer_id:
    :param account_id:
    :param staff_id:
    :param sub_department:
    :param deposit_type:
    :param rate_type:
    :param rate:
    :param transfer_price:
    :param rate_spread:
    :param base_rate:
    :param floating_ratio:
    :param acc_open_date:
    :param start_date:
    :param exp_date:
    :param acc_status:
    :param data_date:
    :param divided_amount:
    :param divided_md_avg:
    :param divided_sd_avg:
    :param divided_yd_avg:
    :param sub_department_sr = models_operation.getSimpleSerializationRule(models.District, 'sd_code', 'caption', 'superior_id')
    :param deposit_type_sr:
    :param rate_type_sr:
    :return:
    '''
    pass
    pass


def translateToSQL(txt_name):
    pass