from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url('test', views.test),
    url(r'pr\.view', views.viewProjectRepository, name='viewProjectRepository'),
    # url(r'target\.ajax', views.ajaxTarget, name='ajaxTarget'),
    url(r'projectaction\.select', views.selectProjectAction, name='selectProjectAction'),
    url(r'projectsummary\.view', views.viewProjectSummary, name='viewProjectSummary'),
    url(r'projectlist\.view', views.viewProjectList, name='viewProjectList'),
    url(r'project\.add', views.addProject, name='addProject'),
    url(r'customer\.ajax', views.ajaxCustomer, name='ajaxCustomer'),
    url(r'staff\.ajax', views.ajaxStaff, name='ajaxStaff'),
    url(r'customer\.add', views.addCustomer, name='addCustomer'),
    url(r'matchaccount\.ajax', views.matchAccount, name='matchAccount'),
]