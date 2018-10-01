import json

from django.urls import resolve
from django.shortcuts import render, HttpResponse, redirect, reverse
from django.contrib.auth import authenticate, login

from app_permission import models, settings, permission_auth


# ↓static ##############################################################################################################
def checkPermission(func):
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return func(request, *args, **kwargs)
            else:
                user = request.user
                url_name = resolve(request.path).url_name
                permitted_url_names = request.session.get('permitted_url_names')
                if permitted_url_names is None:
                    permitted_url_names = json.dumps(list(user.groups.values_list('permissions__codename')))
                    request.session['permitted_url_names'] = permitted_url_names
                if url_name in permitted_url_names:
                    try:
                        cls_extra_auth = getattr(permission_auth, url_name + 'ExtraAuth')      # 注意getattr()是对大小写敏感的
                    except:     # 若出错，则没有额外的验证步骤
                        return func(request, *args, **kwargs)
                    operation = cls_extra_auth(request, user)
                    if operation.is_allowed:
                        return func(request, *args, **kwargs)
            return redirect(settings.LOGIN_URL_NAME)
    return inner


def userLogin(request):
    '''用户登录时的视图函数'''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            request.session.set_expiry(settings.SESSION_AGE)
            return redirect(reverse(settings.HOME_URL_NAME))
    return render(request, settings.LOGIN_PAGE)
# ↑static ##############################################################################################################


