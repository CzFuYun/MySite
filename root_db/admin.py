from django.contrib import admin
from root_db import models

# class AccountedCompanyAdmin(admin.ModelAdmin):
#     list_display = (
#         'name',
#         'customer_type',
#         'scale',
#         'industry',
#         'series',
#         'has_credit',
#     )
#
#
# class SeriesAdmin(admin.ModelAdmin):
#     list_display = (
#         'caption',
#     )
#     list_select_related = True
#
#
# class DividedCompanyAccountAdmin(admin.ModelAdmin):
#     list_display = (
#         'customer',
#         'beneficiary',
#         'sub_department',
#         'deposit_type',
#         'rate_type',
#         'rate_spread',
#         'divided_amount',
#         'divided_yd_avg',
#     )
#     list_filter = (
#         'department',
#         'deposit_type',
#         'exp_date',
#         'deposit_type',
#     )


# class SeriesAdmin(admin.ModelAdmin):
#     list_display = (
#
#     )


# admin.site.register(models.AccountedCompany, AccountedCompanyAdmin)
# admin.site.register(models.Series, SeriesAdmin)
# admin.site.register(models.DividedCompanyAccount, DividedCompanyAccountAdmin)
