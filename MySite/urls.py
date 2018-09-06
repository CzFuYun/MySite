"""MySite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from MySite import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'login/', views.login, name='login'),
    url(r'home/', views.home, name='home'),
    url(r'url\.convert', views.convertToUrl),
    url(r'dc/', include('deposit_and_credit.urls'), name='deposit_and_credit'),
    url(r'cr/', include('app_customer_repository.urls')),
    url(r'accounted_company\.export', views.exportAccountedCompany),
    url(r'divided_company_account\.create', views.createDividedCompanyAccount),
    url(r'contributor_and_series\.export', views.exportContributorAndSeries),
    url(r'staffinfo\.update', views.updateStaffInfo, name='updateStaffInfo'),
    url(r'test/', views.test),
    url(r'feedback', views.feedback, name='feedback'),
]
