from django.db import models


from .utils import DcmsHttpRequest



class CpLedger(models.Model):
    add_date = models.DateField(auto_now_add=True)
    cp_num = models.CharField(max_length=32, primary_key=True, verbose_name='参考编号')
    customer = models.ForeignKey(to='root_db.Customer', on_delete=models.CASCADE, verbose_name='客户')
    is_auto_added = models.BooleanField(default=False, verbose_name='是否自动生成')


class LuLedger(models.Model):
    add_date = models.DateField(auto_now_add=True)
    lu_num = models.CharField(max_length=32, primary_key=True, verbose_name='参考编号')
    cp = models.ForeignKey(to='CpLedger', db_column='cp_num', on_delete=models.CASCADE, verbose_name='授信')
