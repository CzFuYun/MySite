from django.shortcuts import render, reverse
from app_permission import views, settings


def login(request):
    return views.login(request)


@views.checkPermission
def home(request):
    return render(request, settings.HOME_PAGE)


def test(request):
    return render(request, 'test.html')