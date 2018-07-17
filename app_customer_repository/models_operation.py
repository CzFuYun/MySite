

def field_choices_to_dict(field_choices):
    dic = {}
    for i in field_choices:
        dic[str(i[1])] = i[0]
    return dic

def model_object(request, model_cls):
    '''
    从视图函数的request对象中提取数据库表字段值
    :param request:
    :return: dict
    '''
    ret = {}
    method = request.method
    data_dict = getattr(request, method)
    field_list = model_cls._meta.fields
    for field in field_list:
        key = field.name
        value = data_dict.get(key)
        if value:
            ret[key] = value
    return ret

class batchOperation:
    def __init__(self, clsModel):
        self.model = clsModel

    def time_line(self, main_field, main_value, time_field, time_value=0, cursor=0):
        '''
        提取时间轴
        例如可用于获取某个储备项目记录各次更新日期
        :param main_field: 通常为外键字段名，与main_value联合构成具备主体意义的筛选条件，例如：subject_field='project_id'，subject_value=1
        :param time_field: 字段名，如update_date, update_count等具备时间轴意义的字段
        :param time_value: 能对time_field字段进行filter的条件，可以是日期（时间）字符串或对象，或数值，需配合cursor
        :param cursor: 以time_value为原点，向前或向后推移若干位时间坐标
        :return:
        '''
        # self.main_field = main_field
        # self.main_value = main_value
        # self.time_field = time_field
        time_line = []
        if  cursor:
            time_qs = self.model.objects.filter(**{main_field: main_value, time_field: time_value}).values_list(time_field).order_by(
                ('-' if cursor > 0 else '') + time_field
            )[1 : abs(cursor) + 1]
        else:
            time_qs = self.model.objects.filter(**{main_field: main_value}).values_list(time_field).order_by(time_field)
        for i in time_qs:
            time_line.append(i[0])
        return time_line


    def batch_records(self, main_field, time_field, method='last'):
        '''

        :param main_field: 字段名，例如'project_id'
        :param time_field: 字段名，具备时间轴意义的字段，通常为DateField或DateTimeField
        :return:
        '''
        ####若某个储备项目，一天内更新不止一次，这种方法就失效了。。。

        main_bodies = self.model.objects.values(main_field).distinct()
        main_body_count = main_bodies.count()
        return self.model.objects.all().order_by(main_field, ('-' if method == 'last' else '') + time_field)[:main_body_count]

