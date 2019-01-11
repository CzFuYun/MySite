from django.conf.urls import url

from . import views

urlpatterns = [
    url('customer_dept/', views.CustomerDeptView.as_view()),
]