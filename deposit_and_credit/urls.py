from django.conf.urls import url
from deposit_and_credit import views

urlpatterns = [
    url(r'overviewbranch\.view', views.viewOverViewBranch, name='viewOverViewBranch'),
    url(r'overviewbranch\.ajax', views.ajaxOverViewBranch, name='ajaxOverViewBranch'),
    url(r'annotatedeposit\.ajax', views.ajaxAnnotateDeposit, name='ajaxAnnotateDeposit'),
    url(r'contribution\.view', views.viewContribution, name='viewContribution'),
    url(r'contribution\.ajax', views.ajaxContribution, name='ajaxContribution'),
    url(r'deptorder\.ajax', views.ajaxDeptOrder, name='ajaxDeptOrder'),
    url(r'staff\.ajax', views.ajaxStaff, name='ajaxStaff'),
    url(r'customercontributionhistory\.view', views.viewCustomerContributionHistory, name='viewCustomerContributionHistory'),
    url(r'seriescontributionhistory\.view', views.viewSeriesContributionHistory, name='viewSeriesContributionHistory'),
    url(r'customercredithistory\.ajax', views.ajaxCustomerCreditHistory, name='ajaxCustomerCreditHistory'),
    url(r'departmentcontributionhistory\.view', views.viewDepartmentContributionHistory, name='viewDepartmentContributionHistory'),
    url(r'expireprompt\.view', views.viewExpirePrompt, name='viewExpirePrompt'),
    url(r'expireprompttable\.view', views.viewExpirePromptTable, name='viewExpirePromptTable'),
    url(r'expireprompt\.edit', views.editExpirePrompt, name='editExpirePrompt'),
]
