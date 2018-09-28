import json

from django.urls import resolve
from django.shortcuts import render, HttpResponse, redirect, reverse
from django.contrib.auth import authenticate, login

from app_permission import models, settings, permission_auth


# ↓static ##############################################################################################################
def checkPermission(func):
    def inner(request, *args, **kwargs):
        if request.user.is_superuser:
            return func(request, *args, **kwargs)
        else:
            user_id = request.user.username
            if user_id:
                user_obj = models.UserProfile.objects.filter(**{settings.USER_ID: user_id})
                if user_obj:
                    # if ('super_admin',) in user_obj[0].roles.values_list('caption'):
                    #     return func(request, *args, **kwargs)
                    url_name = resolve(request.path).url_name
                    permitted_url_names = request.session.get('permitted_url_names')
                    if permitted_url_names is None:
                        permitted_url_names = json.dumps(list(user_obj.values_list('roles__permissions__url_name')))
                        request.session['permitted_url_names'] = permitted_url_names
                    if [url_name] in json.loads(permitted_url_names):
                        try:
                            cls_extra_auth = getattr(permission_auth, url_name + 'ExtraAuth')      # 注意getattr()是对大小写敏感的
                        except:     # 若出错，则没有额外的验证步骤
                            return func(request, *args, **kwargs)
                        operation = cls_extra_auth(request, user_obj[0])
                        if operation.is_allowed:
                            return func(request, *args, **kwargs)
            return render(request, 'feedback.html', {'title': '无该权限', 'swal_type': 'error'})
    return inner


def userLogin(request):
    '''用户登录时的视图函数'''
    if request.method == 'POST':
        username = request.POST.get(settings.USER_ID)
        password = request.POST.get(settings.PASSWORD)
        user = authenticate(request, username=username, password=password)
        if user:
            # request.session.set_expiry(settings.SESSION_AGE)
            # request.session[settings.USER_ID] = username
            login(request, user)
            return redirect(reverse(settings.HOME_URL_NAME))
    return render(request, settings.LOGIN_PAGE)
# ↑static ##############################################################################################################


