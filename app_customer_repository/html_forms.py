from django.forms import Form
from django.forms import widgets  # 插件
from django.forms import fields  # 字段


class Project(Form):
    customer = fields.CharField(

        label='客户名称',
        widget=widgets.TextInput(attrs={'id': 'customer_name', 'name': 'customer_name', 'class': 'form-control'}),
        required=True,
        error_messages={'required': '不能为空'},
        )
    staff = fields.CharField(
        label='客户经理',
        widget=widgets.TextInput(attrs={'id': 'staff', 'name': 'staff', 'class': 'form-control'}),
        required=True,
        error_messages={'required': '不能为空'},
    )
    is_green = fields.ChoiceField(
        label='绿色金融',
        widget=widgets.RadioSelect(attrs={'id': 'is_green', 'name': 'is_green', 'type': 'radio'}),
        choices=((1, '是'), (0, '否'),),
        required=True,
        error_messages={'required': '必选'},
        # initial=0,
    )
    plan_pretrial = fields.DateField(
        label='计划预审',
        widget=widgets.DateInput(attrs={'id': 'plan_pretrial', 'name': 'plan_pretrial', 'class': 'form-control', 'type': 'date'}),
    )
    plan_chushen = fields.DateField(
        label='计划初审',
        widget=widgets.DateInput(attrs={'id': 'plan_chushen', 'name': 'plan_chushen', 'class': 'form-control', 'type': 'date'}),
    )
    plan_zhuanshen = fields.DateField(
        label='计划专审',
        widget=widgets.DateInput(attrs={'id': 'plan_zhuanshen', 'name': 'plan_zhuanshen', 'class': 'form-control', 'type': 'date'}),
    )
    plan_xinshen = fields.DateField(
        label='计划信审',
        widget=widgets.DateInput(attrs={'id': 'plan_xinshen', 'name': 'plan_xinshen', 'class': 'form-control', 'type': 'date'}),
    )
    plan_reply = fields.DateField(
        label='计划批复',
        widget=widgets.DateInput(attrs={'id': 'plan_reply', 'name': 'plan_reply', 'class': 'form-control', 'type': 'date'}),
    )
    plan_luodi = fields.DateField(
        label='计划落地',
        widget=widgets.DateInput(attrs={'id': 'plan_luodi', 'name': 'plan_luodi', 'class': 'form-control', 'type': 'date'}),
    )


class MyForm(Form):  # 继承自Form类
    user = fields.CharField(
        widget=widgets.TextInput(attrs={'id': 'i1', 'class': 'form-control'})
        # 定义生成的html标签类型是input的text框，attrs={'id': 'i1', 'class': 'c1'}代表在这个标签中添加属性ID为i1，添加class为c1
    )

    gender = fields.ChoiceField(
        choices=((1, '男'), (2, '女'),),  # 定义下拉框的选项，元祖第一个值为option的value值，后面为html里面的值
        initial=2,  # 默认选中第二个option
        widget=widgets.RadioSelect(attrs={'class': 'form-control'})  # 插件表现形式为单选按钮
    )

    city = fields.CharField(
        initial=2,  # 初始值为2
        widget=widgets.Select(choices=((1,'上海'),(2,'北京'),), attrs={'class': 'form-control custom-select'})  # 插件表现形式为下拉框
    )

    pwd = fields.CharField(
        widget=widgets.PasswordInput(attrs={'class': 'form-control'}, render_value=True)  # 插件表现形式为密码输入框
    )
