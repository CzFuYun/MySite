from django.conf.urls import url
from deposit_and_credit import views

urlpatterns = [
    url(r'overviewbranch\.view', views.viewOverViewBranch, name='viewOverViewBranch'),
    url(r'overviewbranch\.ajax', views.ajaxOverViewBranch, name='ajaxOverViewBranch'),
    url(r'annotatedeposit\.ajax', views.ajaxAnnotateDeposit, name='ajaxAnnotateDeposit'),
    url(r'contribution\.view', views.viewContribution, name='viewContribution'),
    url(r'contribution\.ajax', views.ajaxContribution, name='ajaxContribution'),
    url(r'deptorder\.ajax', views.ajaxDeptOrder, name='ajaxDeptOrder'),
]
