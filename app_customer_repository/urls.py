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
]