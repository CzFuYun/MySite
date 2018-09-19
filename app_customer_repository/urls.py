import os
from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from django.views.static import serve
from . import views

urlpatterns = [
    url('test', views.test),
    url(r'pr\.view', views.viewProjectRepository, name='viewProjectRepository'),
    # url(r'target\.ajax', views.ajaxTarget, name='ajaxTarget'),
    url(r'projectaction\.select', views.selectProjectAction, name='selectProjectAction'),
    url(r'projectsummary\.view', views.viewProjectSummary, name='viewProjectSummary'),
    url(r'projectlist\.view', views.viewProjectList, name='viewProjectList'),
    url(r'project\.add', views.addProject, name='addProject'),
    url(r'project\.edit', views.ProjectUpdateView.as_view(), name='editProject'),
    url(r'projectdetail\.view', views.ProjectDetailView.as_view(), name='viewProjectDetail'),
    url(r'customer\.ajax', views.ajaxCustomer, name='ajaxCustomer'),
    url(r'staff\.ajax', views.ajaxStaff, name='ajaxStaff'),
    url(r'customer\.add', views.addCustomer, name='addCustomer'),
    url(r'matchaccount\.ajax', views.matchAccount, name='matchAccount'),
    url(r'project\.del', views.delProject, name='delProject'),
    url(r'projectexe\.view', views.trackProjectExe, name='trackProjectExe'),
    url(r'projectexe\.edit', views.editProjectExe, name='editProjectExe'),
    url(r'projectreply\.set', views.setProjectReplied, name='setProjectReplied'),
    # url(r'predoc\.download', views.downloadPreDoc, name='downloadPreDoc'),
    # url(r'predoc\.show', serve, {'document_root': os.path.join(*['E:', '例会', '预审会', '预审表', 'static', 'images'])}),
    url(r'predoc\.show', views.showPreDoc, name='showPreDoc'),
    url(r'pretrialmeeting\.view', views.viewPretrialMeeting, name='viewPretrialMeeting'),
    url(r'premeetinglist\.show', views.showPreMeetingList, name='showPreMeetingList'),
]