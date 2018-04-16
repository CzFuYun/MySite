from django.db import models

class CustomerStore(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name='企业名称')
    industry = models.ForeignKey('root_db.Industry', null=True, blank=True, on_delete=models.PROTECT, verbose_name='行业')
    sub_industry = models.CharField(max_length=64, null=True, blank=True, verbose_name='细分行业')
    district = models.ForeignKey('root_db.District', null=True, blank=True, on_delete=models.PROTECT, verbose_name='区域')
    type_of_3311 = models.ForeignKey('root_db.TypeOf3311', on_delete=models.PROTECT, verbose_name='3311类型')

    taxes = models.PositiveIntegerField(verbose_name='纳税金额（万元）')
    taxes_rank = models.PositiveSmallIntegerField(verbose_name='纳税排名')
    inlet = models.PositiveIntegerField(verbose_name='进口额（万美元）')
    export = models.PositiveIntegerField(verbose_name='出口额（万美元）')
    in_port = models.PositiveIntegerField(verbose_name='进出口额（万美元）')
    in_port_rank = models.PositiveSmallIntegerField(verbose_name='进出口排名')
    claimer = models.ForeignKey('root_db.Department', null=True, blank=True, on_delete=models.PROTECT, verbose_name='认领状态')


    class Meta:
        verbose_name_plural = '客户库'

