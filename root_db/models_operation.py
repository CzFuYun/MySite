from root_db import  models


def createOrUpdateStaff(staff_id, name, sub_department_caption):
    try:
        staff_obj = models.Staff.objects.filter(staff_id=staff_id)
        staff_qs = staff_obj.values_list('name', 'sub_department__caption')[0]
    except:     # 若不存在该员工
        try:
            sub_department_obj = models.SubDepartment.objects.get(caption=sub_department_caption)
        except:
            print('*' * 50)
            print('Create Staff %s-%s  Failed,department %s Not Exists.' % (staff_id, name, sub_department_caption))
            print('*' * 50)
        else:
            sub_department_obj.staff_set.create(staff_id=staff_id, name=name)
    else:       # 若存在该员工
        name_in_db = staff_qs[0]
        sub_department_in_db = staff_qs[1]
        if sub_department_in_db != sub_department_caption or name_in_db != name:
            prompt = ('''Staff %s-%s  U insert is Not consistent with the DbRecord %s-%s . Your Choice:
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
                    print('Update Staff[%s-%s] Failed,department %s Not Exists.' % (staff_id, name, sub_department_caption))
                    print('*' * 50)


