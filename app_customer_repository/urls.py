from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url('test', views.viewProjectRepository),
    url(r'pr\.view', views.viewProjectRepository, name='viewProjectRepository'),
    url(r'target\.ajax', views.ajaxTarget, name='ajaxTarget'),
    url(r'projectsummary\.view', views.viewProjectSummary, name='viewProjectSummary'),
]