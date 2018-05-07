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
            sub_department_obj.staff_set.create(staff_id=staff_id, name=name)
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
def getSimpleSerializationRule(model_class_used_to_serialize, primary_key_field='id', caption_field='caption'):
    '''
    返回序列化规则的字典，用于提取公司累客户类型、行业、规模，及员工部门名称与编码间的映射关系
    :param model_class_used_to_serialize: LIKE models.CustomerType
    :param primary_key: 'id','code'...
    :param caption_field:
    :return:
    '''
    serialization = model_class_used_to_serialize.objects.values_list(primary_key_field, caption_field)
    serialization_rule_dict = {}
    for i in serialization:
        serialization_rule_dict[i[1]] = i[0]
    return serialization_rule_dict


def serialize(string_as_Key, serialization_rule_dict):
    ret = serialization_rule_dict.get(string_as_Key, None)
    if ret:
        return ret
    else:
        return serialization_rule_dict['undefined']


def createOrUpdateCompanyCustomer(
        customer_id,    name,   need_update_this_company,
        district_sr,            customer_type_sr,           scale_sr,           industry_sr,            series_sr,              type_of_3311_sr,
        district='undefined',   customer_type='undefined',  scale='undefined',  industry='undefined',   series='undefined',     type_of_3311='undefined',
        has_base_acc=False,     has_credit=False, sum_settle=0, inter_settle=0):
    '''

    :param customer_id:
    :param name:
    :param district_sr = getSimpleSerializationRule(models.District)
    :param customer_type_sr = getSimpleSerializationRule(models.CustomerType)
    :param scale_sr = getSimpleSerializationRule(models.Scale)
    :param industry_sr = getSimpleSerializationRule(models.Industry)
    :param series_sr = getSimpleSerializationRule(models.Series)
    :param type_of_3311_sr = getSimpleSerializationRule(models.TypeOf3311)
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
    customer_exits = True if customer_obj.count() else False
    if not customer_exits or need_update_this_company or NEED_UPDATE_ALL_COMPANIES_INFORMATION:
        customer_info_dict = {
            'customer_id': customer_id,
            'name': name,
            'has_base_acc': has_base_acc,
            'has_credit': has_credit,
            'sum_settle': sum_settle,
            'inter_settle': inter_settle,
            'district_id': district_sr[district],
            'customer_type_id': customer_type_sr[customer_type],
            'scale_id': scale_sr[scale],
            'industry_id': industry_sr[industry],
            'series_id': series_sr[series],
            'type_of_3311_id': type_of_3311_sr[type_of_3311],
        }
        if not customer_exits:
            models.AccountedCompany.objects.create(**customer_info_dict)
            print('【New Added Company】' + name + customer_id)
        else:
            models.AccountedCompany.objects.update(**customer_info_dict)
            print('【Update Company】' + name + customer_id)
